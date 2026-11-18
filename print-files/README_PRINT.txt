NO SKIPS - PRINT FILES, FULL RANGE

Every product in one place: V2 pieces from cad/build.py, the classic range in cad/build2.py, Eject, Standby and Rotary in cad/build3.py, Crate in cad/build4.py.
Nothing here has been test-printed. Weights and hours are model estimates (1.2 mm shell, sparse infill, 19 g an hour
plus 15 minutes a plate). Fit-test every joint before selling and replace the numbers with slicer figures.

Folders
  a1_ready/          Bambu Studio project files for the A1, one per plate, settings saved in the file. Start with
                     a1_ready/PRINT_SETTINGS.md and FIRST_PRINTS.md. Times and grams there are slicer figures.
  stl/<ID>_<name>/   print parts, already in print orientation. The file name ends in the filament colour;
                     _x4 means print four. Load all parts of a folder as ONE object with parts in Bambu Studio.
  blueprints/        drawing sheets, the same ones the site shows.
  order_kit/         per-order files for Track Plate, Track Tag, Alias and Run 50 (real Spotify Codes, names).
  cad/               the scripts that make all of it. pip install manifold3d trimesh shapely matplotlib numpy;
                     renders and blueprints also need Blender's bpy and pillow.
                     python3 build.py && python3 build2.py && python3 build3.py && python3 build4.py, then python3 package.py.
                     Options: NS_SET=07 (Vol. 01 tray number), NS_RAIL='Front Row', NS_TAPE='Side A', NS_ACT='Your Act'.

Colours: BLACK body, IVORY and RED accents. ACCENT means the customer's chosen colour.

====================================================================================================
COLLECTIBLES
====================================================================================================

C1 VOL. 01 TRAY  about 77 g, 4.4 h
  Tray 196 x 124 x 4 with 1 mm locating pockets for the six minis. Set number on the lip: 01/50 (regenerate with NS_SET=07 python3 build2.py C1). The minis are the C2_* folders.
  - C1_1_tray_BLACK.stl  196.0 x 124.0 x 4.0 mm, 76.4 g
  - C1_2_tray_lettering_RED.stl  176.0 x 11.4 x 0.6 mm, 0.3 g

C2_01 STUDIO MINI 01  about 14 g, 1.1 h
  Studio Mini 01/06 (turntable). Print flat, number debossed underneath.
  - C2_01_1_body_BLACK.stl  58.0 x 46.0 x 9.2 mm, 13.6 g
  - C2_01_2_accents_RED.stl  37.0 x 33.2 x 1.8 mm, 0.2 g

C2_02 STUDIO MINI 02  about 11 g, 1.0 h
  Studio Mini 02/06 (synth). Print flat, number debossed underneath.
  - C2_02_1_body_BLACK.stl  62.0 x 30.0 x 10.0 mm, 10.0 g
  - C2_02_2_accents_IVORY.stl  55.6 x 23.7 x 1.0 mm, 0.7 g

C2_03 STUDIO MINI 03  about 15 g, 1.2 h
  Studio Mini 03/06 (drum machine). Print flat, number debossed underneath.
  - C2_03_1_body_BLACK.stl  50.0 x 50.0 x 10.8 mm, 13.0 g
  - C2_03_2_accents_RED.stl  38.7 x 44.2 x 1.2 mm, 1.7 g

C2_04 STUDIO MINI 04  about 14 g, 1.1 h
  Studio Mini 04/06 (mixer). Print flat, number debossed underneath.
  - C2_04_1_body_BLACK.stl  46.0 x 56.0 x 11.0 mm, 13.7 g
  - C2_04_2_accents_IVORY.stl  35.2 x 18.2 x 1.6 mm, 0.1 g

C2_05 STUDIO MINI 05  about 6 g, 0.7 h
  Studio Mini 05/06 (mic). Prints upright, base down, number debossed underneath. Change to red at the band and at the base ring.
  - C2_05_1_body_BLACK.stl  30.0 x 30.0 x 53.5 mm, 5.0 g
  - C2_05_2_accents_RED.stl  26.0 x 26.0 x 36.5 mm, 0.6 g

C2_06 STUDIO MINI 06  about 9 g, 0.9 h
  Studio Mini 06/06 (headphones). Print flat, number debossed underneath. The band prints lying flat; its cups press into the two pockets of the base.
  - C2_06_1_base_BLACK.stl  50.0 x 20.0 x 5.0 mm, 4.0 g
  - C2_06_2_band_BLACK.stl  50.6 x 39.0 x 10.0 mm, 4.9 g
  - C2_06_3_ear_pads_IVORY.stl  50.6 x 10.0 x 6.0 mm, 0.2 g

C3 GIG COIN  about 14 g, 1.4 h
  Rev B. Reeded edge, rim 0.7 mm above a 0.5 mm silhouette, back text as a first-layer inlay. New snap frame with bag loop and a foot that locks the frame shut.
  - C3_1_coin_BLACK.stl  42.0 x 42.0 x 4.0 mm, 5.7 g
  - C3_2_silhouette_RED.stl  25.0 x 26.4 x 0.5 mm, 0.2 g
  - C3_3_back_text_inlay_RED.stl  30.0 x 18.1 x 0.4 mm, 0.0 g
  - C3_4_frame_BLACK.stl  48.8 x 62.7 x 4.0 mm, 2.9 g
  - C3_5_foot_BLACK.stl  40.0 x 18.0 x 9.0 mm, 4.7 g
  - C3_6_foot_mark_RED.stl  26.0 x 1.8 x 0.6 mm, 0.0 g

C4 SIDE A  about 96 g, 5.7 h
  Rev B. The four loose feet become two linking rail sections (132 x 34 x 10, two cassettes each). Sliding dovetail, 0.25 mm clearance a side. Add sections to grow the row. Cassettes unchanged at 60 x 38 x 4.
  - C4_1_cassette_body_BLACK_x4.stl  60.0 x 38.0 x 4.0 mm, 42.1 g
  - C4_2_cassette_face_example_RED_x4.stl  52.0 x 33.9 x 0.6 mm, 2.2 g
  - C4_3_rail_section_BLACK_x2.stl  136.0 x 34.0 x 10.0 mm, 51.3 g
  - C4_4_rail_bar_RED_x2.stl  112.0 x 2.4 x 0.6 mm, 0.3 g

C5 GAIN  about 13 g, 1.1 h
  Base 44 mm, knob 27 mm, 20.8 mm tall. The split post snaps into the knob (head 9.6 mm through a 8.6 mm bore). Print both upright. Test the snap on the first print; if it is too tight, scale the post XY to 98%.
  - C5_1_base_BLACK.stl  44.0 x 44.0 x 16.6 mm, 6.6 g
  - C5_2_level_marks_RED.stl  39.9 x 34.7 x 0.6 mm, 0.1 g
  - C5_3_knob_BLACK.stl  26.9 x 26.9 x 16.2 mm, 6.1 g
  - C5_4_pointer_RED.stl  1.8 x 7.8 x 0.6 mm, 0.0 g

====================================================================================================
LISTEN
====================================================================================================

A1 TRACK PLATE  about 67 g, 4.3 h
  Rev B. One slotted base bar (150 x 30 x 14) replaces the two feet. Plate unchanged at 140 x 70 x 3. Slot 3.5 mm wide, leans back 12 degrees. Wave version: print the wave and title in red instead of the code part.
  - A1_1_plate_BLACK.stl  140.0 x 70.0 x 3.0 mm, 36.1 g
  - A1_2_code_and_title_IVORY.stl  120.0 x 47.5 x 0.6 mm, 0.9 g
  - A1_3_base_bar_BLACK.stl  150.0 x 30.0 x 14.0 mm, 30.0 g
  - A1_4_base_stripe_RED.stl  120.0 x 3.0 x 0.6 mm, 0.3 g

A5 TRACK TAG  about 10 g, 1.1 h
  Rev B. Print face up. Rim 1.0 mm, code 0.6 mm, so the code sits 0.4 mm below the rim. Back text is a first-layer inlay: reads correctly when the tag is turned over.
  - A5_1_tag_body_BLACK.stl  80.0 x 30.0 x 4.0 mm, 8.9 g
  - A5_2_front_code_IVORY.stl  56.0 x 9.9 x 0.6 mm, 0.1 g
  - A5_3_back_text_inlay_RED.stl  30.7 x 12.7 x 0.4 mm, 0.1 g
  - A5_4_loop_strap_BLACK.stl  118.8 x 12.2 x 1.2 mm, 0.8 g

A3 RAIL  about 45 g, 2.8 h
  Rail 200 x 36 x 8 printed face up, name 'Front Row' (NS_RAIL to change). Pegs print cap down; three crush ribs make them press-fit into the 6.3 mm sockets. Screw holes countersunk for 4 mm screws, 120 mm apart.
  - A3_1_rail_BLACK.stl  200.0 x 36.0 x 8.0 mm, 38.7 g
  - A3_2_name_and_wave_RED.stl  177.9 x 12.0 x 0.6 mm, 0.3 g
  - A3_3_peg_RED_x5.stl  13.0 x 13.0 x 22.2 mm, 6.2 g

A4 45S  about 113 g, 6.6 h  [COMING SOON (heat test)]
  Coming soon. 90 mm, 4.6 mm thick, flush label inlay, ribbed underside. Print 2 labels red and 2 ivory per set. Release only after a PETG print and a hot-cup test.
  - A4_1_coaster_BLACK_x4.stl  90.0 x 90.0 x 4.6 mm, 111.1 g
  - A4_2_label_RED_x4.stl  26.0 x 26.0 x 0.6 mm, 1.6 g

====================================================================================================
MAKE
====================================================================================================

B1 STACK  about 84 g, 5.1 h
  70 x 35 x 74. Base prints on its back, head upside down, drawer on its front panel, knobs and handle as they are. Pins 3.9 mm into 4.1 mm sockets; knob stems and handle pins press into nominal holes.
  - B1_1_base_BLACK.stl  70.0 x 34.0 x 35.0 mm, 25.4 g
  - B1_2_head_BLACK.stl  70.0 x 35.0 x 43.2 mm, 37.1 g
  - B1_3_drawer_BLACK.stl  66.0 x 31.0 x 34.8 mm, 19.2 g
  - B1_4_knob_IVORY_x3.stl  10.4 x 10.4 x 10.4 mm, 2.0 g
  - B1_5_handle_IVORY.stl  26.0 x 7.0 x 6.9 mm, 0.9 g

B2 LIFT  about 105 g, 5.9 h
  Two identical wedges, 150 x 41 x 44.2, 14 degree slope, 18 mm front lip. Print lying on a side: the waveform is a flush inlay in the first layers, so it shows on the outer face of each wedge.
  - B2_1_wedge_BLACK_x2.stl  150.0 x 43.9 x 41.0 mm, 104.1 g
  - B2_2_wave_inlay_IVORY_x2.stl  58.8 x 18.0 x 0.6 mm, 0.8 g

B3 ALIAS  about 9 g, 0.9 h
  Rev B. Same body as the Track Tag, 10 mm shorter. Name is raised 0.6 mm inside a 1.0 mm rim.
  - B3_1_tag_body_BLACK.stl  70.0 x 30.0 x 4.0 mm, 7.8 g
  - B3_2_front_name_RED.stl  40.4 x 21.0 x 0.6 mm, 0.2 g
  - B3_3_loop_strap_BLACK.stl  118.8 x 12.2 x 1.2 mm, 0.8 g

B5 RUN 50  about 441 g, 24.8 h
  Fifty Alias tags with one line 'Your Act' (NS_ACT to change, or use the order kit: alias --name). Same body as B3. Fill the A1 plate: 12 tags per plate.
  - B5_1_tag_body_BLACK_x50.stl  70.0 x 30.0 x 4.0 mm, 391.9 g
  - B5_2_front_name_RED_x50.stl  43.7 x 18.5 x 0.6 mm, 8.5 g
  - B5_3_loop_strap_BLACK_x50.stl  118.8 x 12.2 x 1.2 mm, 40.1 g

B6 CRATE  about 78 g, 5.2 h  [COMING SOON]
  102 x 18 x 49 mm shell, 71 mm with the hood on. Four slots, 24.2 mm pitch. Sticks stand connector down in a sealed pocket on a shoulder; a window in front of each pocket shows the silver connector when the stick is home and the red spine foot when the slot is empty. Takes sticks 52 to 66 mm long, 12 to 22 wide, 6 to 13 thick, USB A or C. Shell prints upright, spine back face down, hood front face down with the lockup inlaid flush, tags front face down with the word inlaid. Slide the spine in from the top, press the tags in, drop the sticks in, press the hood on.
  - B6_1_shell_BLACK.stl  103.4 x 18.5 x 49.0 mm, 27.3 g
  - B6_2_spine_RED.stl  98.5 x 47.8 x 6.8 mm, 22.1 g
  - B6_3_hood_BLACK.stl  105.7 x 27.6 x 21.7 mm, 17.2 g
  - B6_4_hood_mark_IVORY.stl  66.8 x 7.6 x 0.6 mm, 0.1 g
  - B6_5_hood_bar_RED.stl  1.9 x 7.6 x 0.6 mm, 0.0 g
  - B6_6_tag_main_IVORY.stl  17.0 x 10.0 x 0.9 mm, 0.2 g
  - B6_7_tag_main_word_BLACK.stl  9.6 x 2.6 x 0.4 mm, 0.0 g
  - B6_8_tag_backup_IVORY.stl  17.0 x 10.0 x 0.9 mm, 0.2 g
  - B6_9_tag_backup_word_BLACK.stl  14.0 x 2.5 x 0.4 mm, 0.0 g
  - B6_10_tag_rec_IVORY.stl  17.0 x 10.0 x 0.9 mm, 0.2 g
  - B6_11_tag_rec_word_BLACK.stl  6.9 x 2.7 x 0.4 mm, 0.0 g
  - B6_12_tag_spare_IVORY.stl  17.0 x 10.0 x 0.9 mm, 0.2 g
  - B6_13_tag_spare_word_BLACK.stl  11.5 x 2.7 x 0.4 mm, 0.0 g
  - B6_14_fit_shim_RED_x4.stl  19.5 x 36.0 x 3.0 mm, 10.4 g

====================================================================================================
DAILY
====================================================================================================

D10 EJECT  about 23 g, 1.8 h
  91 x 67 x 7.4 mm. Holds up to 6 flat cards (embossed cards take two slots). Push the red tab on the back up 18 mm: the ramp lifts the front card highest so the stack fans out. Tray prints back down, face plate face down with the ivory eject mark inlaid, slider as it is. Drop the slider in tab first, press the face plate on (side lips are a 0.05 mm press fit).
  - D10_1_tray_BLACK.stl  90.8 x 66.6 x 6.2 mm, 10.4 g
  - D10_2_face_plate_BLACK.stl  90.8 x 66.6 x 2.0 mm, 9.1 g
  - D10_3_eject_inlay_IVORY.stl  9.0 x 7.9 x 0.6 mm, 0.0 g
  - D10_4_slider_RED.stl  83.6 x 8.1 x 11.0 mm, 3.4 g

D12 ROTARY  about 9 g, 0.9 h
  82 x 20 mm plates, 2 mm thick. Two posts snap through: short posts for 2 to 4 keys, long posts for 4 to 7, spacers fill the gaps so the keys stay stiff when you swing them out. The loop takes a car fob. Plates print outer face down (red pointer inlay on plate B).
  - D12_1_plate_a_BLACK.stl  82.0 x 20.0 x 2.0 mm, 3.8 g
  - D12_2_plate_b_BLACK.stl  82.0 x 20.0 x 2.0 mm, 3.7 g
  - D12_3_pointer_inlay_RED.stl  29.6 x 1.6 x 0.6 mm, 0.0 g
  - D12_4_post_short_BLACK_x2.stl  6.0 x 6.0 x 10.0 mm, 0.3 g
  - D12_5_post_long_BLACK_x2.stl  6.0 x 6.0 x 14.0 mm, 0.4 g
  - D12_6_loop_BLACK.stl  34.0 x 14.0 x 2.4 mm, 0.9 g
  - D12_7_spacer_BLACK_x6.stl  8.0 x 8.0 x 1.0 mm, 0.3 g

D11 STANDBY  about 228 g, 12.4 h
  Base 230 x 110 x 12 with a dovetail channel; three fins 92 x 130 slide in from either end and hold by a sprung split key. Set the gaps to your laptops (10 to 30 mm), slide a fin in, done. Base and fins print upright. Cable notches at the back.
  - D11_1_base_BLACK.stl  230.0 x 110.0 x 12.0 mm, 114.0 g
  - D11_2_standby_dot_RED.stl  4.4 x 4.4 x 0.6 mm, 0.0 g
  - D11_3_fin_BLACK_x3.stl  18.0 x 92.0 x 123.8 mm, 114.5 g

D1 HORN  about 120 g, 7.0 h
  Rev C rebuilt. Stand 70 x 50 x 108 prints front face up, plate 70 x 133 x 4 flat. Dovetail rail 20/24 x 5, socket 0.25 mm a side. Seat at 29 mm, ramp 71 degrees, phones 7 to 11.5 mm. Two 5.5 x 19.5 slits feed the chamber, D29 mouth. Cable shaft 11 x 11 runs down and out the back, walled off from the chamber.
  - D1_1_stand_BLACK.stl  70.0 x 108.0 x 50.0 mm, 81.8 g
  - D1_2_speaker_rings_RED.stl  45.5 x 45.0 x 0.6 mm, 0.2 g
  - D1_3_plate_BLACK.stl  70.0 x 133.0 x 9.0 mm, 38.3 g
  - D1_4_plate_mark_RED.stl  12.8 x 21.8 x 0.6 mm, 0.1 g

D6 FOLD  about 145 g, 8.3 h
  Four flat parts, 6 mm thick. Ribs press down onto the two braces with half-lap notches (6.35 mm slot for a 6.0 mm plate). 16 degree tilt, 36 mm front lip. Print every part flat, 4 walls, 25% infill.
  - D6_1_side_rib_BLACK_x2.stl  236.0 x 82.8 x 6.0 mm, 93.4 g
  - D6_2_cross_brace_BLACK_x2.stl  240.0 x 24.0 x 6.0 mm, 50.8 g
  - D6_3_brace_bar_RED_x2.stl  120.0 x 4.0 x 0.6 mm, 0.7 g

D7 CHANNEL  about 149 g, 8.6 h
  Three modules, 60 mm deep: tall cup 60 x 100, mid cup 60 x 60, tray 120 x 24. Each has a male dovetail on its right side and a socket on its left, 20 mm tall, 0.25 mm clearance. Lower one module beside the next to link. Print upright, no supports. The rim band is the last 1.2 mm: one filament change.
  - D7_1_tall_cup_BLACK.stl  66.6 x 61.6 x 98.8 mm, 64.4 g
  - D7_2_tall_cup_rim_RED.stl  60.0 x 60.0 x 1.2 mm, 0.7 g
  - D7_3_mid_cup_BLACK.stl  66.6 x 61.6 x 58.8 mm, 42.2 g
  - D7_4_mid_cup_rim_IVORY.stl  60.0 x 60.0 x 1.2 mm, 0.7 g
  - D7_5_tray_BLACK.stl  126.6 x 60.0 x 22.8 mm, 39.7 g
  - D7_6_tray_rim_RED.stl  120.0 x 60.0 x 1.2 mm, 1.0 g

D8 B-SIDE  about 88 g, 5.0 h
  One piece, 160 mm across, 20 mm rim. Grooves are cut 0.45 mm into the floor so the raised centre label is the only second colour: one filament change. Print as is, no supports.
  - D8_1_tray_BLACK.stl  160.0 x 160.0 x 20.0 mm, 86.3 g
  - D8_2_label_RED.stl  52.0 x 52.0 x 0.6 mm, 1.5 g

D2 TAPE CASE  about 51 g, 3.1 h
  100 x 64 x 21 closed. Tray 17.5 tall, compartments 34 x 59 and 58 x 59, 16 deep. Lid prints art face down: the label 'Side A' (NS_TAPE) and lines are a 0.6 mm red inlay, hubs and screws debossed. Plug rim 0.25 mm clearance a side.
  - D2_1_tray_BLACK.stl  100.0 x 64.0 x 17.5 mm, 25.7 g
  - D2_2_lid_BLACK.stl  100.0 x 64.0 x 6.7 mm, 24.4 g
  - D2_3_label_inlay_RED.stl  88.0 x 50.5 x 0.6 mm, 0.8 g

D4 SLEEVE  about 105 g, 6.2 h
  Feet: two 8 mm record shapes (left and right are mirror parts, grooves inlaid on the outer face, printed face down). Ledge 170 x 34 x 6 face up. Ledge slots 6.4 mm wide, 10 deep. Sleeve rests on the 14 mm base and leans back 15 degrees.
  - D4_1_foot_left_BLACK.stl  130.0 x 119.9 x 8.0 mm, 38.9 g
  - D4_2_foot_left_inlay_RED.stl  84.6 x 109.2 x 0.6 mm, 1.3 g
  - D4_3_foot_right_BLACK.stl  130.0 x 119.9 x 8.0 mm, 38.9 g
  - D4_4_foot_right_inlay_RED.stl  84.6 x 109.2 x 0.6 mm, 1.3 g
  - D4_5_ledge_BLACK.stl  170.0 x 34.0 x 6.0 mm, 23.8 g
  - D4_6_ledge_art_RED.stl  152.1 x 20.1 x 0.6 mm, 0.6 g

D5 HOLD  about 158 g, 9.0 h
  116 mm base, 253.3 mm tall, saddle 108 mm wide. Post 30 x 10 x 227 prints on its back, saddle on its front face (red stripe inlay), base upright. Slot and socket 0.1 mm clearance a side: tight press fit.
  - D5_1_base_BLACK.stl  116.0 x 116.0 x 20.0 mm, 74.4 g
  - D5_2_dial_RED.stl  106.7 x 90.4 x 0.6 mm, 0.2 g
  - D5_3_post_BLACK.stl  30.0 x 227.0 x 10.0 mm, 43.4 g
  - D5_4_fader_and_scale_RED.stl  20.5 x 157.4 x 3.0 mm, 0.7 g
  - D5_5_saddle_BLACK.stl  108.2 x 44.1 x 34.0 mm, 39.0 g
  - D5_6_saddle_stripe_RED.stl  96.4 x 33.1 x 0.6 mm, 0.1 g

D9 PERCH  about 293 g, 16.3 h  [COMING SOON (heat test)]
  Concept, not released. Table 122 x 240 with a 9 mm rim and a cup well, two hinged slats a side, four 3 mm hinge pins that slide in by hand. Needs a PETG print and a hot-cup test before sale.
  - D9_1_table_BLACK.stl  130.0 x 240.0 x 16.9 mm, 138.6 g
  - D9_2_table_mark_RED.stl  60.0 x 3.2 x 0.6 mm, 0.1 g
  - D9_3_inner_slat_BLACK_x2.stl  46.0 x 240.0 x 8.0 mm, 79.5 g
  - D9_4_outer_slat_BLACK_x2.stl  37.0 x 240.0 x 8.0 mm, 66.2 g
  - D9_5_hinge_pin_BLACK_x4.stl  6.8 x 238.0 x 6.8 mm, 8.5 g

D13 DRUMROLL  about 42 g PLA plus a 7 g TPU belt, 1.9 h PLA (sliced) plus about 0.7 h a belt
  Hand rolling machine for king size slim papers (up to 110 mm). 126 x 35.2 x 32.7 mm. cad/build5.py.
  Belt runs round roller A (front, fixed, flanged), roller B (rear, slides 10 mm back in a J slot and drops
  1.2 mm into a seat to lock shut) and a capstan under the pocket. Rollers 10 mm, 2 mm apart when closed.
  Belts: 7 mm roll = 112.9 mm loop, 8 mm = 116.2, 9 mm = 119.5; 110.6 wide, 0.45 wall. Start with the 8 mm belt.
  BELTS ARE TPU 95A: external spool (not the AMS Lite), one 0.45 mm wall, no top or bottom, about 25 mm/s.
  The three rods print lying on their flats, 4 walls. Hubs and caps print face down, pin up. No supports.
  Build: loop the belt round the three rods, lower them between the end plates, push a black cap into each
  end of the capstan, a red hub into each end of roller A (round hole) and roller B (slot). Poker slides into
  the square hole. Checked in CAD only (no clashes over the full travel). Not printed.

D14 DOCK  about 84 g model (about 98 g expected after slicing), about 4.5 h (estimate, not sliced)
  Two-controller dock for D5 Hold. Drops over the post before the saddle, rests on the base.
  - D14_1_dock_BLACK.stl  226.7 x 60.0 x 36.0 mm, print lying on its side, chevron up, 4 walls, 25% infill
  - D14_2_cap_RED_x2.stl  8.0 x 22.0 x 36.0 mm, print 2, on the side, 100% infill
  CAD: print-files/cad/build6.py (fit checks against Hold built in). Projects: a1_ready/D14_dock/.
