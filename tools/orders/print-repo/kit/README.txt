NO SKIPS ORDER KIT, REV B (Track Plate A1, Track Tag A5, Alias B3)

Replaces the old Spotify code kit. The old kit made the rev A shapes (3 mm tag with no rim,
plate code 1.0 mm high, no base bar). This one makes the same rev B parts as the range files.

Setup (once)
  pip install trimesh shapely manifold3d matplotlib svgelements numpy
  Keep code_to_print.py, Poppins-Bold.ttf and the fixed_parts folder together.
  Try it: python code_to_print.py tag test_code.svg --name "Test"   (test_code.svg is a dummy, it will not scan)

Per order
1. Spotify app: open the song > Share > Copy song link.
2. Fastest: give the link and the script downloads the code itself:
     python code_to_print.py tag --link "https://open.spotify.com/track/..." --title "Starboy" --artist "The Weeknd" -o order_0124
   If the download fails (no internet, or Spotify changes its code service), make the SVG by hand at
   spotifycodes.com: paste the link, format SVG, background #000000, bar colour white, Download.
3. With a downloaded SVG, run one of:
     python code_to_print.py plate code.svg --title "Blinding Lights" --artist "The Weeknd" -o order_0123
     python code_to_print.py tag   code.svg --title "Starboy" --artist "The Weeknd" -o order_0124
     python code_to_print.py tag   code.svg --name "Dimo" -o order_0125
     python code_to_print.py alias --line1 "Dimo" --line2 "Mahtarp" -o order_0126
     python code_to_print.py alias --name "Prathaam" -o order_0127
4. Open preview.png in the order folder. Front: 23 bars and the logo. Back: reads correctly, clear of the hole.
5. Bambu Studio: load every STL in the order folder as ONE object with parts. Colours come from the
   file names: BLACK, IVORY, ACCENT (the customer's colour; red by default).
6. Print: tag and alias face up, back inlay on the bed (first 2 layers). Plate flat, code on top.
   Base bar and strap print on their own plate, black (stripe in the accent colour).
7. Scan the printed code with the Spotify app (Search > camera) before shipping. Never ship one that does not scan.

Limits the script checks
  Plate: title and artist up to 40 characters.  Tag back: title and artist up to 18, or a name up to 14.
  Alias: each line up to 10. Letters, numbers, spaces and . , ' & ! ? ( ) - only.

Sizes
  Plate 140 x 70 x 3, code 120 wide, raised 0.6. Base bar 150 x 30 x 14, slot 3.5 wide leaning back 12 degrees.
  Tag 80 x 30, body 3.0 + rim 1.0, code 58 wide raised 0.6 (sits 0.4 below the rim). Alias 70 x 30, same body.
