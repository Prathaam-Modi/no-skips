# Deferred products

Sidelined by the owner on 24 Nov 2026. Nothing here is deleted. These products are hidden on the site (deferred:true in index.html) and their print files sit here so the live folders only hold what we actually sell.

Why: the range had grown to too many things. The owner's benchmark is the printed B-Side tray: thick, slightly heavy, feels worth the money in the hand. Products that do not reach that feel, or that are purely functional gadgets, wait here. The next range leans to home decor (sculptural planters, shelf pieces, plant miniatures) plus console plates.

## 28 Nov 2026: the site flips to games
The first game print, the P3 Six Cuts chess set, passed, so the site flips to Play as agreed. "Play everything. Skip nothing." The rest of the old range is sidelined here, nothing deleted.
- Moved to stl/ and a1_ready/: A1 Track Plate, C1 Vol. 01 tray, the six C2 Studio Minis (C2_01 to C2_06), D8 B-Side, D17 Bookends, D18 Ripple, H1 Terrace, H2 Twist, H3 Echo.
- Moved to blueprints/: bp_A1, bp_C1, bp_C2, bp_D8, bp_H1, bp_H2, bp_H3.
- On the site: deferred:true,hide:true in index.html, listed in DEFERRED in admin.html. The stock.json caps for D8 and D18 are removed.
- The Engrave add-on was only offered on D8, so it is no longer shown anywhere. The code stays in index.html and admin.html.
- Navigation for Collectibles, Everyday, Room Tone, Reserve and Gifts is gone from the site, and so is the Run 50 bulk block (B5 was already deferred).

## In this folder (24 Nov 2026)
- stl/ and a1_ready/: A3 Rail, A4 45s, A5 Track Tag, B1 Stack, B2 Lift, B3 Alias, B5 Run 50, B6 Crate, C4 Side A, C5 Gain, D1 Wedge, D2 Tape Case, D4 Sleeve, D5 Hold, D6 Fold, D7 Channel, D9 Perch, D10 Eject, D11 Standby, D13 Drumroll, D14 Dock, D15 Stage, D16 Lean, D19 Key rail, G1 Patched In, D12 Rotary (deferred 24 Nov 2026, 11 pm: the first print had stringing in the screw holes and the snap posts slipped out).
- blueprints/: the matching bp_*.png files.
- Also deferred on the site with no folder of their own: RS1 Desk set (made of D7 and D15) and C2 Studio Mini sold as a single (the six mini STLs stay live because they are the Vol. 01 set).

## Still live
The Play range only: P3 Six Cuts (chess set and board, on the waitlist), P2 Tangram (coming soon until its reprint passes). P1 Crosses stays in the print folders but is not listed on the site.

## CAD
CAD scripts stay in print-files/cad because they share helpers (ns.py, build2.py and others). They still write to print-files/stl when run; move the output here if you rebuild a deferred product.

## To bring one back
1. git mv print-files/deferred/stl/<folder> print-files/stl/ (and the same for a1_ready and blueprints).
2. In index.html delete deferred:true,hide:true from its entry.
3. In admin.html remove its id from DEFERRED and add it to LAUNCH or SECOND.
4. Log it in the changelog and the status doc.
