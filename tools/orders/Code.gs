/**
 * No Skips orders and email - Google Apps Script web app.
 *
 * Lives inside the Google Sheet "No Skips Orders" (Extensions > Apps Script).
 * Setup and use: tools/orders/SETUP.md in the no-skips repo.
 *
 * What it does
 *  - The website posts every order (with its order number) and every email sign-up here.
 *  - The admin page (admin.html, Orders tab) lists orders and moves them through
 *    review > approved (payment request) > paid > printing > dispatched > delivered,
 *    or rejected / cancelled / refund due > refunded. Each step emails the customer.
 *  - Customers can approve a preview and unsubscribe from links in their emails.
 *  - Emails go out from the owner's Gmail through MailApp (free; Google allows about
 *    100 recipients a day on a personal Gmail account).
 */

const SHEET_ORDERS = 'Orders';
const SHEET_SUBS = 'Subscribers';
const SHEET_SETTINGS = 'Settings';

const ORDER_COLS = ['Order no.', 'Created', 'Status', 'Email', 'Newsletter', 'Phase', 'Items', 'Items JSON',
  'Subtotal', 'Shipping', 'Total', 'Paid UTR', 'Paid at', 'Courier', 'Tracking', 'Refund amount', 'Refund UTR',
  'Reason', 'Note', 'Preview approved', 'Print files', 'Flags', 'Last email', 'History', 'Message'];
const SUB_COLS = ['Email', 'Joined', 'Source', 'Status', 'Updated'];

const STATUS = {
  new: 'To review',
  approved: 'Approved, awaiting payment',
  paid: 'Paid',
  printing: 'Printing',
  dispatched: 'Dispatched',
  delivered: 'Delivered',
  rejected: 'Rejected',
  cancelled: 'Cancelled',
  refund_due: 'Refund due',
  refunded: 'Refunded'
};
/* Which moves are allowed. Everything else is refused, so an order cannot skip payment. */
const NEXT = {
  new: ['approved', 'rejected', 'cancelled'],
  approved: ['paid', 'cancelled'],
  paid: ['printing', 'refund_due'],
  printing: ['dispatched', 'refund_due'],
  dispatched: ['delivered'],
  delivered: ['refund_due'],
  refund_due: ['refunded'],
  rejected: [], cancelled: [], refunded: []
};

const SETTINGS_DEFAULT = [
  ['Business name', 'No Skips', 'Shown in emails'],
  ['UPI ID', '', 'Where customers pay, e.g. yourname@okaxis. Required before you approve an order'],
  ['UPI name', 'No Skips', 'Name shown in the UPI app'],
  ['UPI QR file id', '', 'Optional: Google Drive file id of your UPI QR image, attached to payment emails'],
  ['Owner email', '', 'Gets a copy of every new order. Empty = the Google account that runs this script'],
  ['Reply-to', '', 'Customers reply here. Empty = owner email'],
  ['WhatsApp', '917411148303', 'Digits only'],
  ['Site URL', 'https://prathaam-modi.github.io/no-skips/', ''],
  ['Pay within (hours)', '48', 'Shown in the payment email'],
  ['Max open orders per email', '3', 'More than this is flagged for review, not blocked']
];

/* ------------------------------------------------------------------ setup */

/** Run once from the Apps Script editor: creates the tabs and the admin key. */
function setup() {
  const ss = SpreadsheetApp.getActive();
  const o = sheet_(SHEET_ORDERS, ORDER_COLS);
  const s = sheet_(SHEET_SUBS, SUB_COLS);
  let st = ss.getSheetByName(SHEET_SETTINGS);
  if (!st) {
    st = ss.insertSheet(SHEET_SETTINGS);
    st.getRange(1, 1, 1, 3).setValues([['Setting', 'Value', 'Notes']]).setFontWeight('bold');
    st.getRange(2, 1, SETTINGS_DEFAULT.length, 3).setValues(SETTINGS_DEFAULT);
    st.setColumnWidth(1, 200); st.setColumnWidth(2, 320); st.setColumnWidth(3, 480);
  }
  o.setFrozenRows(1); s.setFrozenRows(1);
  const rule = SpreadsheetApp.newDataValidation().requireValueInList(Object.keys(STATUS), true).build();
  o.getRange(2, 3, o.getMaxRows() - 1, 1).setDataValidation(rule);
  const props = PropertiesService.getScriptProperties();
  if (!props.getProperty('ADMIN_KEY')) props.setProperty('ADMIN_KEY', randomKey_(32));
  if (!props.getProperty('LINK_SECRET')) props.setProperty('LINK_SECRET', randomKey_(32));
  Logger.log('Admin key (paste into the admin page, Orders tab): ' + props.getProperty('ADMIN_KEY'));
  return props.getProperty('ADMIN_KEY');
}

/** Run from the editor if the admin key leaks: makes a new one. */
function newAdminKey() {
  const k = randomKey_(32);
  PropertiesService.getScriptProperties().setProperty('ADMIN_KEY', k);
  Logger.log('New admin key: ' + k);
}

/** Run from the editor to check emails reach you before going live. */
function sendTestEmail() {
  const to = ownerEmail_();
  send_(to, 'Test from your No Skips orders sheet', [
    p_('If you can read this, order emails will work.'),
    p_('Emails left today: ' + MailApp.getRemainingDailyQuota())
  ]);
  Logger.log('Sent to ' + to);
}

/* ------------------------------------------------------------------ web entry points */

function doPost(e) {
  let body = {};
  try { body = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { return json_({ ok: false, error: 'bad json' }); }
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    if (body.type === 'signup') return json_(signup_(body));
    if (body.type === 'order') return json_(newOrder_(body));
    if (body.type === 'admin') {
      const key = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY');
      if (!key || body.key !== key) return json_({ ok: false, error: 'That orders key was not accepted.' });
      return json_(admin_(body));
    }
    return json_({ ok: false, error: 'unknown type' });
  } catch (err) {
    return json_({ ok: false, error: String(err && err.message || err) });
  } finally {
    try { lock.releaseLock(); } catch (_) {}
  }
}

function doGet(e) {
  const q = (e && e.parameter) || {};
  if (q.a === 'unsub') {
    if (!q.e || q.t !== sign_('unsub:' + q.e.toLowerCase())) return page_('That link did not work', 'Reply to any of our emails and we will take you off the list by hand.');
    setSubscriber_(q.e, 'unsubscribed', 'link');
    return page_('You are unsubscribed', 'You will not get drop and offer emails from ' + setting_('Business name') + ' any more. Order emails for orders you place still come through.');
  }
  if (q.a === 'approve') {
    if (!q.r || q.t !== sign_('approve:' + q.r)) return page_('That link did not work', 'Reply to the preview email with "Approved" and we will carry on.');
    const row = findOrder_(q.r);
    if (!row) return page_('Order not found', 'Reply to the preview email and we will sort it out.');
    const o = readOrder_(row);
    if (!o['Preview approved']) {
      writeFields_(row, { 'Preview approved': stamp_() });
      addHistory_(row, 'Customer approved the preview');
      send_(ownerEmail_(), o['Order no.'] + ': preview approved by the customer', [p_(o['Email'] + ' approved the preview for ' + o['Order no.'] + '.')]);
    }
    return page_('Preview approved', 'Thank you. We print exactly what you saw. Order ' + o['Order no.'] + '.');
  }
  return page_(setting_('Business name'), 'Nothing to see here.');
}

/* ------------------------------------------------------------------ public actions */

function signup_(b) {
  const email = cleanEmail_(b.email);
  if (!email) return { ok: false, error: 'email' };
  const fresh = setSubscriber_(email, 'subscribed', String(b.source || 'site').slice(0, 30));
  if (fresh) {
    send_(email, 'You are on the ' + setting_('Business name') + ' list', [
      p_('Thanks for signing up. You get the first word on every drop, and the odd launch price.'),
      p_('A few emails a month at most.')
    ], { unsub: email });
  }
  return { ok: true };
}

function newOrder_(b) {
  const ref = String(b.ref || '');
  if (!/^NS-\d{4}-[A-Z0-9]{4}$/.test(ref)) return { ok: false, error: 'ref' };
  if (findOrder_(ref)) return { ok: true, dup: true };
  const email = cleanEmail_(b.email);
  const items = Array.isArray(b.items) ? b.items.slice(0, 30) : [];
  const subtotal = Math.max(0, Math.round(Number(b.total) || 0));
  const flags = [];
  if (!email) flags.push('No valid email');
  if (email) {
    const open = countOpen_(email), max = Number(setting_('Max open orders per email')) || 3;
    if (open >= max) flags.push('Repeat buyer: ' + open + ' open orders');
  }
  const sh = sheet_(SHEET_ORDERS, ORDER_COLS);
  const row = {
    'Order no.': ref, 'Created': stamp_(), 'Status': 'new', 'Email': email, 'Newsletter': b.news ? 'yes' : '',
    'Phase': String(b.phase || '').slice(0, 12), 'Items': String(b.itemsText || '').slice(0, 1000),
    'Items JSON': JSON.stringify(items).slice(0, 40000), 'Subtotal': subtotal, 'Shipping': '', 'Total': subtotal,
    'Flags': flags.join('; '), 'History': stamp_() + ' Order received from the site', 'Message': String(b.message || '').slice(0, 3000)
  };
  sh.appendRow(ORDER_COLS.map(c => row[c] !== undefined ? row[c] : ''));
  if (b.news && email) setSubscriber_(email, 'subscribed', 'order');
  if (email) {
    send_(email, 'We got your order ' + ref, [
      p_('Thanks. Your order number is <b>' + ref + '</b>. Keep it handy: it is how we tell orders apart.'),
      itemsTable_(items, subtotal, null),
      p_('What happens next: we check every order by hand, usually within a day. You then get an email with the final price including shipping and how to pay by UPI. <b>Nothing is charged until then.</b>'),
      b.phase === 'preorder' ? p_('This is a pre-order. Pieces are printed in order of payment.') : '',
      p_('If you have not sent the WhatsApp message yet, please send it so we can talk if anything needs checking.')
    ]);
    writeFields_(findOrder_(ref), { 'Last email': stamp_() + ' received' });
  }
  send_(ownerEmail_(), 'New order ' + ref + ' (' + rupees_(subtotal) + ')', [
    p_((email || 'No email') + (flags.length ? ' <b>(' + flags.join('; ') + ')</b>' : '')),
    itemsTable_(items, subtotal, null), p_('Review it in the admin page, Orders tab.')
  ]);
  return { ok: true };
}

/* ------------------------------------------------------------------ admin actions */

function admin_(b) {
  switch (b.action) {
    case 'list': return listOrders_(b);
    case 'update': return updateOrder_(b);
    case 'note': {
      const row = findOrder_(b.ref); if (!row) return { ok: false, error: 'Order not found' };
      writeFields_(row, { 'Note': String(b.note || '').slice(0, 1000) }); return { ok: true, order: pub_(row) };
    }
    case 'resend': return resend_(b);
    case 'preview': return sendPreview_(b);
    case 'printfiles': {
      const row = findOrder_(b.ref); if (!row) return { ok: false, error: 'Order not found' };
      writeFields_(row, { 'Print files': String(b.url || '').slice(0, 500) }); addHistory_(row, 'Print files: ' + (b.url || ''));
      return { ok: true, order: pub_(row) };
    }
    case 'subscribers': {
      const subs = rows_(SHEET_SUBS, SUB_COLS);
      return { ok: true, subscribed: subs.filter(s => s['Status'] === 'subscribed').length, total: subs.length, quota: MailApp.getRemainingDailyQuota() };
    }
    case 'newsletter': return newsletter_(b);
    default: return { ok: false, error: 'unknown action' };
  }
}

function listOrders_(b) {
  const all = rows_(SHEET_ORDERS, ORDER_COLS);
  const orders = all.slice(-500).reverse().map(publicOrder_);
  const counts = {};
  Object.keys(STATUS).forEach(k => counts[k] = 0);
  all.forEach(o => { counts[o['Status']] = (counts[o['Status']] || 0) + 1; });
  return {
    ok: true, orders, counts, labels: STATUS, next: NEXT,
    quota: MailApp.getRemainingDailyQuota(), upiReady: !!setting_('UPI ID'),
    subscribed: rows_(SHEET_SUBS, SUB_COLS).filter(s => s['Status'] === 'subscribed').length
  };
}

function updateOrder_(b) {
  const row = findOrder_(b.ref);
  if (!row) return { ok: false, error: 'Order not found' };
  const o = readOrder_(row), from = o['Status'], to = String(b.to || '');
  if (!STATUS[to]) return { ok: false, error: 'Unknown status' };
  if ((NEXT[from] || []).indexOf(to) < 0) return { ok: false, error: 'Cannot go from ' + STATUS[from] + ' to ' + STATUS[to] + '.' };
  const notify = b.notify !== false && !!o['Email'];
  const f = { 'Status': to };
  const reason = String(b.reason || '').slice(0, 500);
  const note = String(b.message || '').slice(0, 800);
  const items = parseItems_(o['Items JSON']);
  let subject = '', blocks = [], extra = {};

  if (to === 'approved') {
    if (!setting_('UPI ID')) return { ok: false, error: 'Add your UPI ID in the Settings tab of the sheet first.' };
    const ship = Math.max(0, Math.round(Number(b.shipping) || 0));
    const total = Number(o['Subtotal']) + ship;
    f['Shipping'] = ship; f['Total'] = total;
    subject = 'Approved: pay ' + rupees_(total) + ' for order ' + o['Order no.'];
    blocks = paymentBlocks_(o, items, ship, total, note);
    extra = qrAttachment_();
  } else if (to === 'paid') {
    const utr = String(b.utr || '').replace(/\s/g, '').slice(0, 40);
    if (!utr) return { ok: false, error: 'Enter the UPI reference (UTR) of the payment.' };
    f['Paid UTR'] = utr; f['Paid at'] = stamp_();
    subject = 'Payment received for ' + o['Order no.'];
    blocks = [p_('We received ' + rupees_(o['Total']) + ' (UPI ref ' + esc_(utr) + '). Your order is confirmed and in the print queue.'),
      itemsTable_(items, o['Subtotal'], o['Shipping']),
      o['Phase'] === 'preorder' ? p_('As a pre-order, it is printed in order of payment. We email you when it goes on the printer.') : p_('We email you when it goes on the printer, and again with tracking when it ships.')];
  } else if (to === 'printing') {
    subject = 'On the printer: ' + o['Order no.'];
    blocks = [p_('Your order ' + o['Order no.'] + ' is printing now. Each piece is checked by hand before it is packed.')];
  } else if (to === 'dispatched') {
    const courier = String(b.courier || '').slice(0, 60), tracking = String(b.tracking || '').slice(0, 200);
    if (!courier || !tracking) return { ok: false, error: 'Enter the courier and the tracking number or link.' };
    f['Courier'] = courier; f['Tracking'] = tracking;
    subject = 'Shipped: ' + o['Order no.'];
    blocks = [p_('Your order ' + o['Order no.'] + ' is on its way with ' + esc_(courier) + '.'),
      p_('Tracking: ' + (/^https?:\/\//.test(tracking) ? '<a href="' + esc_(tracking) + '">' + esc_(tracking) + '</a>' : '<b>' + esc_(tracking) + '</b>')),
      p_('Please film a short unboxing video when it arrives. If anything is broken or wrong, message us within 48 hours of delivery with photos and that video, as the Terms explain.')];
  } else if (to === 'delivered') {
    subject = 'Delivered: ' + o['Order no.'];
    blocks = [p_('The courier shows your order ' + o['Order no.'] + ' as delivered. We hope it is a keeper.'),
      p_('Anything broken or not as approved? Message us on WhatsApp within 48 hours of delivery with photos and the unboxing video.'),
      p_('If you post it, tag <b>@noskips.in</b>. We share the good ones.')];
  } else if (to === 'rejected') {
    subject = 'About your order ' + o['Order no.'];
    blocks = [p_('Sorry, we cannot make this order.' + (reason ? ' ' + esc_(reason) : '')), p_('<b>Nothing was charged.</b> Reply to this email or message us on WhatsApp if you would like to change it and order again.')];
    f['Reason'] = reason;
  } else if (to === 'cancelled') {
    subject = 'Order ' + o['Order no.'] + ' cancelled';
    blocks = [p_('Your order ' + o['Order no.'] + ' is cancelled.' + (reason ? ' ' + esc_(reason) : '')), p_('<b>Nothing was charged.</b>')];
    f['Reason'] = reason;
  } else if (to === 'refund_due') {
    const amt = Math.max(0, Math.round(Number(b.amount) || Number(o['Total']) || 0));
    if (!amt) return { ok: false, error: 'Enter the refund amount.' };
    f['Refund amount'] = amt; f['Reason'] = reason;
    subject = 'Refund on the way for ' + o['Order no.'];
    blocks = [p_('We are refunding <b>' + rupees_(amt) + '</b> for order ' + o['Order no.'] + '.' + (reason ? ' ' + esc_(reason) : '')),
      p_('It goes back to the UPI account you paid from, within 7 days. You get another email with the UPI reference when it is sent.')];
  } else if (to === 'refunded') {
    const rutr = String(b.utr || '').replace(/\s/g, '').slice(0, 40);
    if (!rutr) return { ok: false, error: 'Enter the UPI reference (UTR) of the refund.' };
    f['Refund UTR'] = rutr;
    subject = 'Refund sent for ' + o['Order no.'];
    blocks = [p_('We sent the refund of ' + rupees_(o['Refund amount']) + ' for order ' + o['Order no.'] + '. UPI ref <b>' + esc_(rutr) + '</b>.'), p_('It usually shows in your account within a day.')];
  }
  if (note && to !== 'approved') blocks.push(p_(esc_(note)));
  writeFields_(row, f);
  addHistory_(row, STATUS[from] + ' > ' + STATUS[to] + (reason ? ' (' + reason + ')' : '') + (notify ? ', emailed' : ', no email'));
  if (notify && subject) {
    const q = MailApp.getRemainingDailyQuota();
    if (q < 1) return { ok: true, warn: 'Status saved, but the daily email limit is used up. The email was not sent.', order: pub_(row) };
    send_(o['Email'], subject, blocks, extra);
    writeFields_(row, { 'Last email': stamp_() + ' ' + to });
  }
  return { ok: true, order: pub_(row) };
}

function resend_(b) {
  const row = findOrder_(b.ref); if (!row) return { ok: false, error: 'Order not found' };
  const o = readOrder_(row);
  if (o['Status'] !== 'approved') return { ok: false, error: 'Only the payment request can be sent again.' };
  if (!o['Email']) return { ok: false, error: 'This order has no email.' };
  send_(o['Email'], 'Reminder: pay ' + rupees_(o['Total']) + ' for order ' + o['Order no.'],
    paymentBlocks_(o, parseItems_(o['Items JSON']), o['Shipping'], o['Total'], ''), qrAttachment_());
  writeFields_(row, { 'Last email': stamp_() + ' payment reminder' }); addHistory_(row, 'Payment request sent again');
  return { ok: true, order: pub_(row) };
}

function sendPreview_(b) {
  const row = findOrder_(b.ref); if (!row) return { ok: false, error: 'Order not found' };
  const o = readOrder_(row);
  if (!o['Email']) return { ok: false, error: 'This order has no email.' };
  if (!b.png) return { ok: false, error: 'No preview image.' };
  const blob = Utilities.newBlob(Utilities.base64Decode(String(b.png)), 'image/png', o['Order no.'] + '_preview.png');
  const link = webAppUrl_() + '?a=approve&r=' + encodeURIComponent(o['Order no.']) + '&t=' + sign_('approve:' + o['Order no.']);
  send_(o['Email'], 'Check your preview for ' + o['Order no.'], [
    p_('Here is exactly what we will print for order <b>' + o['Order no.'] + '</b>. Please check every letter.'),
    '<p><img src="cid:preview" alt="Preview of your piece" style="max-width:100%;border:1px solid #d9d2c2;border-radius:6px"></p>',
    b.message ? p_(esc_(String(b.message).slice(0, 800))) : '',
    button_(link, 'It is right, print it'),
    p_('Something to change? Just reply to this email. Spotify Codes: scan the picture with the Spotify app (Search, then the camera) to check it opens your song.')
  ], { inline: { preview: blob } });
  writeFields_(row, { 'Last email': stamp_() + ' preview' }); addHistory_(row, 'Preview emailed');
  return { ok: true, order: pub_(row) };
}

function newsletter_(b) {
  const subject = String(b.subject || '').slice(0, 150), text = String(b.body || '').slice(0, 8000);
  if (!subject || !text) return { ok: false, error: 'Write a subject and a message.' };
  const paras = text.split(/\n\s*\n/).map(t => p_(esc_(t).replace(/\n/g, '<br>')));
  if (b.test) { send_(ownerEmail_(), '[Test] ' + subject, paras, { unsub: ownerEmail_() }); return { ok: true, sent: 1, test: true }; }
  const list = rows_(SHEET_SUBS, SUB_COLS).filter(s => s['Status'] === 'subscribed').map(s => s['Email']);
  const props = PropertiesService.getScriptProperties();
  const key = 'NL_' + Utilities.base64EncodeWebSafe(subject).slice(0, 40);
  const done = JSON.parse(props.getProperty(key) || '[]');
  let sent = 0;
  for (const em of list) {
    if (done.indexOf(em) >= 0) continue;
    if (MailApp.getRemainingDailyQuota() < 5) break;   // keep a few for order emails
    send_(em, subject, paras, { unsub: em }); done.push(em); sent++;
  }
  props.setProperty(key, JSON.stringify(done));
  const left = list.length - done.length;
  return { ok: true, sent, left, note: left ? left + ' still to send. Press Send again tomorrow (the same subject carries on where it stopped).' : 'Sent to everyone on the list.' };
}

/* ------------------------------------------------------------------ email building */

function paymentBlocks_(o, items, ship, total, note) {
  const upi = setting_('UPI ID'), name = setting_('UPI name') || setting_('Business name');
  const hours = setting_('Pay within (hours)') || '48';
  const deep = 'upi://pay?pa=' + encodeURIComponent(upi) + '&pn=' + encodeURIComponent(name) + '&am=' + total + '&cu=INR&tn=' + encodeURIComponent(o['Order no.']);
  return [
    p_('Good news: we can make order <b>' + o['Order no.'] + '</b>. Here is the final price.'),
    itemsTable_(items, o['Subtotal'], ship),
    note ? p_(esc_(note)) : '',
    '<table role="presentation" style="border-collapse:collapse;margin:16px 0;width:100%;max-width:440px"><tr><td style="padding:14px 16px;border:1px solid #171615;border-radius:6px">'
      + '<div style="font:600 12px/1.4 monospace;letter-spacing:.06em;text-transform:uppercase;color:#6b655b">Pay by UPI</div>'
      + '<div style="font-size:22px;font-weight:700;margin:4px 0">' + rupees_(total) + '</div>'
      + '<div>To: <b>' + esc_(upi) + '</b> (' + esc_(name) + ')</div>'
      + '<div>Note: <b>' + o['Order no.'] + '</b></div></td></tr></table>',
    '<p><a href="' + deep + '" style="color:#C8202B;font-weight:600">Open in a UPI app</a> (works on most phones)</p>',
    p_('Please pay within ' + esc_(hours) + ' hours to keep your place, and put the order number in the UPI note. Then reply to this email or send the payment screenshot on WhatsApp.'),
    o['Phase'] === 'preorder' ? p_('Pre-order: you can cancel for a full refund until we start printing, as the Terms explain.') : ''
  ];
}

function qrAttachment_() {
  const id = setting_('UPI QR file id');
  if (!id) return {};
  try { return { attachments: [DriveApp.getFileById(id).getBlob().setName('UPI_QR.png')] }; } catch (e) { return {}; }
}

function itemsTable_(items, subtotal, ship) {
  const rows = (items || []).map(it => {
    const opts = []
      .concat(it.mode ? [it.mode === 'wave' ? 'Sound wave' : 'Spotify Code'] : [])
      .concat(it.accent ? ['Accent ' + it.accent] : [])
      .concat(it.pick ? [it.pick] : [])
      .concat((it.fields || []).filter(f => !/spotify .*link/i.test(f.label)).map(f => f.label + ': ' + f.value))
      .concat(it.gift ? ['Gift' + (it.giftNote ? ' (' + it.giftNote + ')' : '')] : []);
    return '<tr><td style="padding:8px 0;border-top:1px solid #d9d2c2;vertical-align:top"><b>' + esc_(it.name) + '</b> x' + (it.qty || 1)
      + (opts.length ? '<br><span style="color:#6b655b;font-size:13px">' + esc_(opts.join(', ')) + '</span>' : '') + '</td>'
      + '<td style="padding:8px 0;border-top:1px solid #d9d2c2;text-align:right;vertical-align:top;white-space:nowrap">' + rupees_((it.price || 0) * (it.qty || 1)) + '</td></tr>';
  }).join('');
  let foot = '';
  if (ship !== null && ship !== undefined && ship !== '') {
    foot = '<tr><td style="padding:6px 0;border-top:1px solid #d9d2c2">Shipping</td><td style="text-align:right;border-top:1px solid #d9d2c2;white-space:nowrap">' + rupees_(ship) + '</td></tr>'
      + '<tr><td style="padding:6px 0;font-weight:700">Total</td><td style="text-align:right;font-weight:700;white-space:nowrap">' + rupees_(Number(subtotal) + Number(ship)) + '</td></tr>';
  } else {
    foot = '<tr><td style="padding:6px 0;border-top:1px solid #d9d2c2;font-weight:700">Total before shipping</td><td style="text-align:right;border-top:1px solid #d9d2c2;font-weight:700;white-space:nowrap">' + rupees_(subtotal) + '</td></tr>';
  }
  return '<table role="presentation" style="border-collapse:collapse;width:100%;max-width:440px;margin:12px 0">' + rows + foot + '</table>';
}

function send_(to, subject, blocks, opt) {
  opt = opt || {};
  if (!to) return;
  const brand = setting_('Business name') || 'No Skips';
  const wa = setting_('WhatsApp');
  const unsub = opt.unsub ? webAppUrl_() + '?a=unsub&e=' + encodeURIComponent(opt.unsub) + '&t=' + sign_('unsub:' + String(opt.unsub).toLowerCase()) : '';
  const html = '<div style="background:#F3EEE2;padding:24px 12px;font:15px/1.5 Helvetica,Arial,sans-serif;color:#171615">'
    + '<div style="max-width:520px;margin:0 auto;background:#fbf8f0;border:1px solid #d9d2c2;border-radius:6px;padding:22px">'
    + '<div style="font-weight:800;font-size:18px;letter-spacing:-.02em;margin-bottom:14px"><span style="display:inline-block;width:6px;height:18px;background:#C8202B;vertical-align:-3px;margin-right:8px;border-radius:1px"></span>' + esc_(brand.toUpperCase()) + '</div>'
    + blocks.filter(Boolean).join('')
    + '<p style="margin-top:22px;color:#6b655b;font-size:12px">' + esc_(brand) + ', printed to order in Bengaluru.'
    + (wa ? ' WhatsApp <a href="https://wa.me/' + wa + '" style="color:#6b655b">+' + wa.replace(/^(\d{2})(\d{5})(\d+)$/, '$1 $2 $3') + '</a>.' : '')
    + (unsub ? ' <a href="' + unsub + '" style="color:#6b655b">Unsubscribe</a> from drop emails.' : '') + '</p>'
    + '</div></div>';
  const o = { to, subject, htmlBody: html, name: brand, replyTo: setting_('Reply-to') || ownerEmail_() };
  if (opt.attachments) o.attachments = opt.attachments;
  if (opt.inline) o.inlineImages = opt.inline;
  MailApp.sendEmail(o);
}

const p_ = t => t ? '<p style="margin:0 0 12px">' + t + '</p>' : '';
const button_ = (href, label) => '<p style="margin:18px 0"><a href="' + href + '" style="display:inline-block;background:#C8202B;color:#fff;text-decoration:none;font-weight:600;padding:12px 18px;border-radius:6px">' + esc_(label) + '</a></p>';

/* ------------------------------------------------------------------ sheet helpers */

function sheet_(name, cols) {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold');
  }
  return sh;
}
function rows_(name, cols) {
  const sh = sheet_(name, cols), n = sh.getLastRow();
  if (n < 2) return [];
  const head = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  return sh.getRange(2, 1, n - 1, head.length).getValues().map(r => { const o = {}; head.forEach((h, i) => o[h] = r[i]); return o; });
}
function findOrder_(ref) {
  const sh = sheet_(SHEET_ORDERS, ORDER_COLS), n = sh.getLastRow();
  if (n < 2 || !ref) return 0;
  const f = sh.getRange(2, 1, n - 1, 1).createTextFinder(String(ref)).matchEntireCell(true).findNext();
  return f ? f.getRow() : 0;
}
function readOrder_(row) {
  const sh = sheet_(SHEET_ORDERS, ORDER_COLS);
  const head = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  const vals = sh.getRange(row, 1, 1, head.length).getValues()[0];
  const o = {}; head.forEach((h, i) => o[h] = vals[i] instanceof Date ? Utilities.formatDate(vals[i], 'Asia/Kolkata', 'yyyy-MM-dd HH:mm') : vals[i]);
  return o;
}
const pub_ = row => publicOrder_(readOrder_(row));
function publicOrder_(o) {
  return {
    ref: o['Order no.'], created: o['Created'] instanceof Date ? Utilities.formatDate(o['Created'], 'Asia/Kolkata', 'yyyy-MM-dd HH:mm') : o['Created'],
    status: o['Status'], email: o['Email'], news: o['Newsletter'] === 'yes', phase: o['Phase'], items: parseItems_(o['Items JSON']), itemsText: o['Items'],
    subtotal: Number(o['Subtotal']) || 0, shipping: o['Shipping'] === '' ? null : Number(o['Shipping']), total: Number(o['Total']) || 0,
    paidUtr: o['Paid UTR'], paidAt: o['Paid at'], courier: o['Courier'], tracking: o['Tracking'], refundAmount: o['Refund amount'], refundUtr: o['Refund UTR'],
    reason: o['Reason'], note: o['Note'], previewApproved: o['Preview approved'] ? String(o['Preview approved']) : '', printFiles: o['Print files'],
    flags: o['Flags'], lastEmail: o['Last email'], history: String(o['History'] || '').split('\n').filter(Boolean)
  };
}
function writeFields_(row, fields) {
  const sh = sheet_(SHEET_ORDERS, ORDER_COLS);
  const head = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  Object.keys(fields).forEach(k => { const i = head.indexOf(k); if (i >= 0) sh.getRange(row, i + 1).setValue(fields[k]); });
}
function addHistory_(row, line) {
  const sh = sheet_(SHEET_ORDERS, ORDER_COLS);
  const i = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].indexOf('History') + 1;
  const cell = sh.getRange(row, i);
  cell.setValue(String(cell.getValue() || '') + '\n' + stamp_() + ' ' + line);
}
function countOpen_(email) {
  return rows_(SHEET_ORDERS, ORDER_COLS).filter(o => String(o['Email']).toLowerCase() === email && ['new', 'approved', 'paid', 'printing'].indexOf(o['Status']) >= 0).length;
}
function setSubscriber_(email, status, source) {
  const sh = sheet_(SHEET_SUBS, SUB_COLS), n = sh.getLastRow();
  email = String(email).trim().toLowerCase();
  if (n >= 2) {
    const f = sh.getRange(2, 1, n - 1, 1).createTextFinder(email).matchEntireCell(true).findNext();
    if (f) {
      const r = f.getRow(), was = sh.getRange(r, 4).getValue();
      sh.getRange(r, 4, 1, 2).setValues([[status, stamp_()]]);
      return status === 'subscribed' && was !== 'subscribed';
    }
  }
  if (status !== 'subscribed') return false;
  sh.appendRow([email, stamp_(), source, status, stamp_()]);
  return true;
}
function settings_() {
  const c = CacheService.getScriptCache(), hit = c.get('settings');
  if (hit) return JSON.parse(hit);
  const sh = SpreadsheetApp.getActive().getSheetByName(SHEET_SETTINGS), o = {};
  if (sh && sh.getLastRow() > 1) sh.getRange(2, 1, sh.getLastRow() - 1, 2).getValues().forEach(r => { if (r[0]) o[String(r[0]).trim()] = String(r[1]).trim(); });
  c.put('settings', JSON.stringify(o), 60);
  return o;
}
const setting_ = k => settings_()[k] || '';
const ownerEmail_ = () => setting_('Owner email') || Session.getEffectiveUser().getEmail();
const webAppUrl_ = () => ScriptApp.getService().getUrl();

/* ------------------------------------------------------------------ small helpers */

function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function page_(title, text) {
  return HtmlService.createHtmlOutput('<meta name="viewport" content="width=device-width,initial-scale=1"><div style="font:16px/1.5 Helvetica,Arial,sans-serif;max-width:480px;margin:40px auto;padding:0 16px;color:#171615">'
    + '<h1 style="font-size:24px;letter-spacing:-.02em">' + esc_(title) + '</h1><p>' + esc_(text) + '</p></div>').setTitle(title);
}
function cleanEmail_(e) { e = String(e || '').trim().toLowerCase(); return /^[^\s@<>]+@[^\s@<>]+\.[a-z]{2,}$/.test(e) && e.length <= 120 ? e : ''; }
function parseItems_(s) { try { const a = JSON.parse(s || '[]'); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
function rupees_(n) { return 'Rs ' + Math.round(Number(n) || 0).toLocaleString('en-IN'); }
function stamp_() { return Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyyy-MM-dd HH:mm'); }
function esc_(s) { return String(s === undefined || s === null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function randomKey_(n) { const ch = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'; let s = ''; for (let i = 0; i < n; i++) s += ch[Math.floor(Math.random() * ch.length)]; return s; }
function sign_(s) {
  const secret = PropertiesService.getScriptProperties().getProperty('LINK_SECRET') || '';
  return Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(s, secret)).slice(0, 22);
}
