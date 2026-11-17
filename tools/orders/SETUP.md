# No Skips orders: setup and daily use

How an order flows:

1. The customer orders on the site. The WhatsApp message carries an order number (NS-DDMM-XXXX) and their email. At the same moment the order lands in your Google Sheet, and the customer gets a "we got your order" email. Nothing is charged.
2. You open the admin page, Orders tab. You check the order and, for Track Plate, Track Tag and Alias, press **Make print files**. GitHub builds the files in your private repo in a few minutes and shows the preview. You can email that preview to the customer, who approves it with one tap.
3. You press **Approve**, enter shipping, and the customer gets an email with the total, your UPI ID and the order number to put in the UPI note.
4. When the money arrives, you enter the UTR and press **Confirm payment**. Then **Printing**, **Dispatched** (courier and tracking) and **Delivered**. Each step emails the customer.
5. If you cannot make an order before payment, **Reject** it (nothing was charged). After payment, **Cancel and refund**: the console shows the amount, you send it back from your bank app, enter the refund UTR, and the customer gets the reference.

Everything is free. Emails go from your Gmail, which allows about 100 emails a day on a personal account. The admin page shows how many are left today.

---

## One-time setup (about 20 minutes)

### 1. Make the sheet and the script

1. Go to sheets.google.com and create a blank sheet. Name it **No Skips Orders**.
2. In the sheet: **Extensions > Apps Script**. Delete what is in the editor, paste the whole of `tools/orders/Code.gs` from the repo, and press **Save**.
3. In the function list at the top choose **setup**, press **Run**, and allow the permissions it asks for (Sheets, sending email as you, Drive for the optional QR). Google shows an "unverified app" warning because you wrote the script yourself: choose Advanced, then Go to the project.
4. Open **Execution log**. Copy the line **Admin key: ...**. That is your orders key. Keep it private.
5. Back in the sheet there are now three tabs: Orders, Subscribers, Settings. In **Settings**, fill in at least your **UPI ID**. Optional: upload your UPI QR image to Google Drive and paste its file id (the long part of its link) next to **UPI QR file id**, so it is attached to every payment email.
6. In the editor, choose **sendTestEmail** and press Run. You should get a test email.

### 2. Put it online

1. In the editor: **Deploy > New deployment**. Type: **Web app**. Execute as: **Me**. Who has access: **Anyone**. Press Deploy and copy the **Web app URL** (it ends in `/exec`).
2. "Anyone" only means the site can send orders and sign-ups to it. Reading or changing orders needs the orders key.

### 3. Switch the site on

1. Turn on GitHub Pages: on github.com open **Prathaam-Modi/no-skips > Settings > Pages**. Source: **Deploy from a branch**, Branch: **main**, folder **/ (root)**, Save. After a minute the site is at `https://prathaam-modi.github.io/no-skips/` and the admin page at `https://prathaam-modi.github.io/no-skips/admin.html`.
2. Open the admin page, unlock with your GitHub key, and in the **Site** tab paste the Web app URL under **Email list and order updates**. Save.
3. Open the **Orders** tab and paste the orders key from step 1.4.

### 4. Print files on GitHub (private repo)

1. On github.com: **New repository**, name **no-skips-orders**, **Private**, no README. Create it.
2. Tell Claude it exists. Claude pushes the workflow and the order kit into it.
3. Give your admin key access: github.com > Settings > Developer settings > Fine-grained tokens > your No Skips token > Edit. Repository access: add **no-skips-orders** next to no-skips. Permissions: **Actions: Read and write** and **Contents: Read and write**. Save. (The key value does not change.)

Order details stay in the private repo; nothing about customers goes into the public no-skips repo.

---

## Daily use

- **Admin page > Orders**. The chips show what needs you: To review, Awaiting payment, Paid, Printing, Dispatched, Refund due.
- **Repeat buyer** flags show when one email has 3 or more open orders (change the number in the sheet's Settings tab). The site also caps each order: 2 Vol. 01 sets, 5 of anything else (change per product in the Site tab).
- Orders that were never actually sent on WhatsApp: **Cancel** without emailing (untick "Email the customer").
- **Email the list** at the bottom of the Orders tab: send yourself a test first. If the list is bigger than the day's email allowance, it stops and carries on when you press Send again the next day with the same subject.
- You can also work straight in the sheet. Do not rename the columns or tabs.

## If something goes wrong

- **"That orders key was not accepted"**: run `newAdminKey` in the editor and paste the new key into the Orders tab.
- **Changed Code.gs**: Deploy > Manage deployments > pencil > Version: New version > Deploy. The URL stays the same.
- **Emails not arriving**: check the customer's spam folder, and the "Emails left today" number in the Orders tab.
- **Print files fail**: the Orders tab shows the reason (usually a wrong Spotify link). Fix it with the customer, then press Make print files again. You can always fall back to the order kit on a laptop: `print-files/order_kit/README.txt`.
