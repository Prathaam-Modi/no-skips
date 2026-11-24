# Deferred products

Sidelined by the owner on 24 Nov 2026. Nothing here is deleted. These products are hidden on the site (deferred:true in index.html) and their print files sit here so the live folders only hold what we actually sell.

Why: the range had grown to too many things. The owner's benchmark is the printed B-Side tray: thick, slightly heavy, feels worth the money in the hand. Products that do not reach that feel, or that are purely functional gadgets, wait here. The next range leans to home decor (sculptural planters, shelf pieces, plant miniatures) plus console plates.

## In this folder
- stl/ and a1_ready/: A3 Rail, A4 45s, A5 Track Tag, B1 Stack, B2 Lift, B3 Alias, B5 Run 50, B6 Crate, C4 Side A, C5 Gain, D1 Wedge, D2 Tape Case, D4 Sleeve, D5 Hold, D6 Fold, D7 Channel, D9 Perch, D10 Eject, D11 Standby, D13 Drumroll, D14 Dock, D15 Stage, D16 Lean, D19 Key rail, G1 Patched In.
- blueprints/: the matching bp_*.png files.
- Also deferred on the site with no folder of their own: RS1 Desk set (made of D7 and D15) and C2 Studio Mini sold as a single (the six mini STLs stay live because they are the Vol. 01 set).

## Still live
C1 Vol. 01 (tray plus the six C2 minis), D8 B-Side, D12 Rotary, D18 Ripple. Second drop: A1 Track Plate, D17 Bookends.

## CAD
CAD scripts stay in print-files/cad because they share helpers (ns.py, build2.py and others). They still write to print-files/stl when run; move the output here if you rebuild a deferred product.

## To bring one back
1. git mv print-files/deferred/stl/<folder> print-files/stl/ (and the same for a1_ready and blueprints).
2. In index.html delete deferred:true,hide:true from its entry.
3. In admin.html remove its id from DEFERRED and add it to LAUNCH or SECOND.
4. Log it in the changelog and the status doc.
