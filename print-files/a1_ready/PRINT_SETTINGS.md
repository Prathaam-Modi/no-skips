# No Skips - A1 ready print settings

Sliced 17 November 2026 with Bambu Studio 2.02 (command line) for the Bambu Lab A1, 0.4 mm nozzle, Textured PEI plate, Bambu PLA Basic. Every plate below sliced without errors. Nothing here has been printed yet, so treat times and grams as slicer figures, not measured ones.

## How to use these files

- Each product folder holds one `.3mf` project per plate. Open it in Bambu Studio, check the plate, press Slice, then Print. Parts are already placed, oriented and assigned to filament slots, and the process settings are saved in the file.
- AMS Lite slots are the same for the whole range: slot 1 Black, slot 2 Red, slot 3 Ivory (Jade White), slot 4 free.
- Ready-sliced `.gcode.3mf` plates are in the zip sent in chat (not in git, about 45 MB). They were sliced for generic slots 1 to 3, so re-slicing from the project file on your own machine is the safer route for the first prints.
- Bed: Textured PEI, PLA Basic defaults. Bambu Studio shows a note that the plate temperature is above the filament's soft limit. That is normal for an open A1; leave it.
- Solid parts use zig-zag (rectilinear) infill because gyroid is refused at 100%.
- Drumroll belts are TPU 95A: feed from the external spool, not the AMS Lite. See the Drumroll note.

## Range table

| ID | Product | Plates | Layer (mm) | Walls | Infill | Supports | Brim | Slots | Colour changes | Time (h) | Model (g) | With purge (g) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 00 | Fit coupon | 1 | 0.20 | 3 | 20% | None | None | 1 Black | 0 | 1.4 | 39 | 39 |
| C3 | Gig Coin | 1 | 0.12 | 3/4 | 15%/20% | None | None | 1 Black, 2 Red | 8 | 1.4 | 13 | 17 |
| C2_01 | Mini 01 turntable | 1 | 0.16 | 2 | 15% | None | None | 1 Black, 2 Red | 7 | 0.8 | 11 | 15 |
| C2_02 | Mini 02 synth | 1 | 0.16 | 2 | 15% | None | None | 1 Black, 3 Ivory | 6 | 0.7 | 9 | 13 |
| C2_03 | Mini 03 drum machine | 1 | 0.16 | 2 | 15% | None | None | 1 Black, 2 Red | 8 | 0.9 | 12 | 16 |
| C2_04 | Mini 04 mixer | 1 | 0.16 | 2 | 15% | None | None | 1 Black, 3 Ivory | 10 | 0.9 | 11 | 17 |
| C2_05 | Mini 05 mic | 1 | 0.16 | 2 | 15% | Tree, auto | None | 1 Black, 2 Red | 6 | 1.1 | 5 | 12 |
| C2_06 | Mini 06 headphones | 1 | 0.16 | 2/3 | 15%/30% | None | None | 1 Black, 3 Ivory | 38 | 1.7 | 8 | 26 |
| C1 | Vol. 01 tray | 1 | 0.20 | 2 | 15% | None | None | 1 Black, 2 Red | 1 | 1.7 | 62 | 63 |
| A3 | Rail | 2 | 0.20 | 3/4 | 25%/100% | None | None | 1 Black, 2 Red | 1 | 1.8 | 39 | 41 |
| D2 | Tape Case | 1 | 0.20 | 3 | 15% | None | None | 1 Black, 2 Red | 4 | 1.3 | 44 | 46 |
| D5 | Hold | 2 | 0.20 | 4 | 20%/25%/30% | None | None | 1 Black, 2 Red | 9 | 7.8 | 176 | 182 |
| A5 | Track Tag | 1 | 0.12 | 3 | 100% | None | None | 1 Black, 2 Red, 3 Ivory | 9 | 0.8 | 10 | 14 |
| A1 | Track Plate | 1 | 0.16 | 3 | 15%/100% | None | None | 1 Black, 2 Red, 3 Ivory | 5 | 3.1 | 66 | 70 |
| C4 | Side A | 1 | 0.20 | 3 | 20%/100% | None | None | 1 Black, 2 Red | 5 | 4.1 | 90 | 93 |
| B1 | Stack | 2 | 0.20 | 3/4 | 15%/100% | None | None | 1 Black, 3 Ivory | 0 | 2.5 | 84 | 84 |
| D8 | B-Side | 1 | 0.20 | 3 | 15% | None | None | 1 Black, 2 Red | 4 | 2.2 | 80 | 82 |
| C5 | Gain | 1 | 0.16 | 4 | 30%/100% | None | None | 1 Black, 2 Red | 7 | 1.3 | 15 | 19 |
| B3 | Alias | 1 | 0.16 | 3 | 100% | None | None | 1 Black, 2 Red | 4 | 0.5 | 9 | 11 |
| D12 | Rotary | 1 | 0.16 | 3 | 100% | None | 5 mm on tall parts | 1 Black, 2 Red | 5 | 0.7 | 9 | 11 |
| D10 | Eject | 2 | 0.16 | 3 | 100% | None | None | 1 Black, 2 Red, 3 Ivory | 4 | 1.0 | 22 | 24 |
| D13 | Drumroll (PLA parts only) | 2 | 0.20 | 4 | 25%/100% | None | None | 1 Black, 2 Red, 3 Ivory | 6 | 1.9 | 42 | 45 |
| B6 | Crate | 3 | 0.12/0.20 | 3 | 20%/30%/100% | Tree, auto | None | 1 Black, 2 Red, 3 Ivory | 9 | 3.4 | 71 | 76 |
| B2 | Lift | 1 | 0.20 | 4 | 20% | None | None | 1 Black, 3 Ivory | 4 | 4.2 | 138 | 140 |
| D1 | Horn | 1 | 0.20 | 3 | 15%/25% | Tree, auto | None | 1 Black, 2 Red | 5 | 4.7 | 119 | 127 |
| D4 | Sleeve | 2 | 0.20 | 3 | 20% | None | None | 1 Black, 2 Red | 4 | 3.0 | 87 | 89 |
| D6 | Fold | 2 | 0.20 | 4 | 25% | None | None | 1 Black, 2 Red | 1 | 4.3 | 133 | 134 |
| D7 | Channel | 1 | 0.20 | 3 | 15% | None | None | 1 Black, 2 Red, 3 Ivory | 13 | 3.9 | 141 | 157 |
| D11 | Standby | 2 | 0.20 | 3/4 | 15%/20% | Tree, auto | 5 mm on tall parts | 1 Black, 2 Red | 1 | 8.2 | 247 | 249 |
| B5 | Run 50 (12 tags + 25 straps sliced) | 2 | 0.20 | 3 | 100% | None | None | 1 Black, 2 Red | 4 | 3.4 | 115 | 117 |
| A4 | 45s | 1 | 0.20 | 3 | 20% | None | None | 1 Black, 2 Red | 3 | 2.6 | 81 | 83 |
| D9 | Perch | 3 | 0.20 | 3 | 15%/100% | Tree, auto | 5 mm on tall parts | 1 Black, 2 Red | 4 | 7.7 | 265 | 267 |
| D14 | Dock | 2 | 0.20 | 4/3 | 25%/100% | None | None | 1 Black / 2 Red (separate plates) | 0 | 2.6 | 88 | 88 |

Where two values are shown (for example 15%/100%), the first is the plate default and the second is set on a single object such as a snap frame, pin or thin plate. Top and bottom shells: 4 and 3 at 0.20 mm, slicer defaults at finer layers. Infill pattern gyroid unless solid. Seam aligned. No ironing: the textured plate face is the show face.

## Per plate

| File | Layer | Plate default (walls, infill) | Object overrides | Time (h) | Grams by slot (model / with purge) | Changes |
|---|---|---|---|---|---|---|
| C3_gig_coin/C3_gig_coin.3mf | 0.12 | 3, 15% | sparse_infill_density 20%, wall_loops 4 | 1.37 | 1 Black: 12.2 / 14.3; 2 Red: 0.4 / 2.5 | 8 |
| C2_05_studio_mini_mic/C2_05_studio_mini_mic.3mf | 0.16 | 2, 15% | enable_support 1, support_type tree(auto) | 1.11 | 1 Black: 5.0 / 10.3; 2 Red: 0.3 / 2.1 | 6 |
| C1_studio_tray/C1_studio_tray.3mf | 0.20 | 2, 15% | - | 1.67 | 1 Black: 61.4 / 62.2; 2 Red: 0.3 / 0.7 | 1 |
| 00_fit_coupon/00_fit_coupon.3mf | 0.20 | 3, 20% | - | 1.40 | 1 Black: 38.9 / 38.9 | 0 |
| C2_01_studio_mini_turntable/C2_01_studio_mini_turntable.3mf | 0.16 | 2, 15% | - | 0.80 | 1 Black: 11.1 / 13.0; 2 Red: 0.2 / 2.1 | 7 |
| C2_02_studio_mini_synth/C2_02_studio_mini_synth.3mf | 0.16 | 2, 15% | - | 0.74 | 1 Black: 8.1 / 9.9; 3 Ivory: 0.7 / 2.9 | 6 |
| C2_03_studio_mini_drum_machine/C2_03_studio_mini_drum_machine.3mf | 0.16 | 2, 15% | - | 0.89 | 1 Black: 9.8 / 11.8; 2 Red: 1.9 / 3.9 | 8 |
| C2_04_studio_mini_mixer/C2_04_studio_mini_mixer.3mf | 0.16 | 2, 15% | - | 0.94 | 1 Black: 11.3 / 13.5; 3 Ivory: 0.1 / 3.9 | 10 |
| C2_06_studio_mini_headphones/C2_06_studio_mini_headphones.3mf | 0.16 | 2, 15% | sparse_infill_density 30%, wall_loops 3 | 1.66 | 1 Black: 8.0 / 11.9; 3 Ivory: 0.2 / 14.5 | 38 |
| A3_rail/A3_rail_plate1_rail.3mf | 0.20 | 3, 25% | - | 1.28 | 1 Black: 32.5 / 33.7; 2 Red: 0.3 / 0.7 | 1 |
| A3_rail/A3_rail_plate2_pegs_red.3mf | 0.20 | 4, 100% | - | 0.48 | 2 Red: 6.2 / 6.2 | 0 |
| D2_tape_case/D2_tape_case.3mf | 0.20 | 3, 15% | - | 1.26 | 1 Black: 43.6 / 44.2; 2 Red: 0.8 / 1.9 | 4 |
| D5_hold/D5_hold_plate1_base_saddle.3mf | 0.20 | 4, 25% | sparse_infill_density 20% | 6.20 | 1 Black: 133.4 / 136.4; 2 Red: 0.3 / 2.4 | 8 |
| D5_hold/D5_hold_plate2_post.3mf | 0.20 | 4, 30% | - | 1.59 | 1 Black: 41.3 / 42.7; 2 Red: 0.6 / 1.0 | 1 |
| A5_track_tag/A5_track_tag.3mf | 0.12 | 3, 100% | - | 0.78 | 1 Black: 9.6 / 10.9; 2 Red: 0.1 / 0.8; 3 Ivory: 0.1 / 2.4 | 9 |
| A1_track_plate/A1_track_plate.3mf | 0.16 | 3, 15% | sparse_infill_density 100% | 3.07 | 1 Black: 64.9 / 67.3; 2 Red: 0.3 / 0.7; 3 Ivory: 0.7 / 2.2 | 5 |
| C4_side_a/C4_side_a.3mf | 0.20 | 3, 20% | sparse_infill_density 100% | 4.10 | 1 Black: 87.4 / 89.1; 2 Red: 2.4 / 3.8 | 5 |
| C5_gain/C5_gain.3mf | 0.16 | 4, 30% | sparse_infill_density 100% | 1.31 | 1 Black: 14.5 / 17.3; 2 Red: 0.1 / 2.0 | 7 |
| A4_45s/A4_45s.3mf | 0.20 | 3, 20% | - | 2.57 | 1 Black: 79.4 / 80.4; 2 Red: 1.6 / 2.5 | 3 |
| B1_stack/B1_stack_plate1_black.3mf | 0.20 | 3, 15% | - | 2.27 | 1 Black: 80.8 / 80.8 | 0 |
| B1_stack/B1_stack_plate2_ivory.3mf | 0.20 | 4, 100% | - | 0.27 | 3 Ivory: 2.9 / 2.9 | 0 |
| B2_lift/B2_lift.3mf | 0.20 | 4, 20% | - | 4.22 | 1 Black: 137.5 / 138.0; 3 Ivory: 0.8 / 2.3 | 4 |
| B3_alias_tag/B3_alias_tag.3mf | 0.16 | 3, 100% | - | 0.52 | 1 Black: 8.8 / 9.8; 2 Red: 0.1 / 1.2 | 4 |
| B5_run_50/B5_run_50_plate_tags_x12.3mf | 0.20 | 3, 100% | - | 2.47 | 1 Black: 93.5 / 94.5; 2 Red: 2.0 / 3.0 | 4 |
| B5_run_50/B5_run_50_plate_straps_x25.3mf | 0.20 | 3, 100% | - | 0.90 | 1 Black: 20.0 / 20.0 | 0 |
| B6_crate/B6_crate_plate1_black.3mf | 0.20 | 3, 20% | enable_support 1, support_type tree(auto) | 2.30 | 1 Black: 47.2 / 47.7; 2 Red: 0.1 / 1.0; 3 Ivory: 0.2 / 1.5 | 6 |
| B6_crate/B6_crate_plate2_red.3mf | 0.20 | 3, 30% | - | 0.81 | 2 Red: 23.1 / 23.1 | 0 |
| B6_crate/B6_crate_plate3_tags_ivory.3mf | 0.12 | 3, 100% | - | 0.29 | 1 Black: 0.1 / 0.6; 3 Ivory: 0.6 / 2.1 | 3 |
| D10_eject/D10_eject_plate1_black.3mf | 0.16 | 3, 100% | - | 0.69 | 1 Black: 18.8 / 19.3; 3 Ivory: 0.0 / 1.6 | 4 |
| D10_eject/D10_eject_plate2_slider_red.3mf | 0.16 | 3, 100% | - | 0.29 | 2 Red: 3.5 / 3.5 | 0 |
| D12_rotary/D12_rotary.3mf | 0.16 | 3, 100% | brim_type outer_only, brim_width 5 | 0.72 | 1 Black: 9.2 / 9.8; 2 Red: 0.1 / 1.2 | 5 |
| D11_standby/D11_standby_plate1_base.3mf | 0.20 | 3, 15% | - | 2.92 | 1 Black: 107.4 / 109.1; 2 Red: 0.0 / 0.4 | 1 |
| D11_standby/D11_standby_plate2_fins.3mf | 0.20 | 4, 20% | enable_support 1, support_type tree(auto), brim_type outer_only, brim_width 5 | 5.25 | 1 Black: 139.3 / 139.3 | 0 |
| D1_horn/D1_horn.3mf | 0.20 | 3, 15% | enable_support 1, support_type tree(auto), sparse_infill_density 25% | 4.73 | 1 Black: 119.2 / 125.1; 2 Red: 0.3 / 1.6 | 5 |
| D7_channel/D7_channel.3mf | 0.20 | 3, 15% | - | 3.93 | 1 Black: 138.6 / 150.8; 2 Red: 1.6 / 3.5; 3 Ivory: 0.7 / 2.9 | 13 |
| D8_b_side/D8_b_side.3mf | 0.20 | 3, 15% | - | 2.21 | 1 Black: 78.8 / 79.7; 2 Red: 1.5 / 2.5 | 4 |
| D9_perch/D9_perch_plate1_table.3mf | 0.20 | 3, 15% | - | 3.26 | 1 Black: 123.0 / 124.4; 2 Red: 0.1 / 1.1 | 4 |
| D9_perch/D9_perch_plate2_slats.3mf | 0.20 | 3, 15% | - | 3.69 | 1 Black: 130.4 / 130.4 | 0 |
| D9_perch/D9_perch_plate3_pins.3mf | 0.20 | 3, 100% | enable_support 1, support_type tree(auto), brim_type outer_only, brim_width 5 | 0.71 | 1 Black: 11.4 / 11.4 | 0 |
| D6_fold/D6_fold_plate1_ribs.3mf | 0.20 | 4, 25% | - | 2.75 | 1 Black: 86.3 / 86.3 | 0 |
| D6_fold/D6_fold_plate2_braces.3mf | 0.20 | 4, 25% | - | 1.58 | 1 Black: 45.7 / 46.7; 2 Red: 0.7 / 1.1 | 1 |
| D4_sleeve/D4_sleeve_plate1_feet.3mf | 0.20 | 3, 20% | - | 2.18 | 1 Black: 63.2 / 63.7; 2 Red: 2.6 / 3.2 | 3 |
| D4_sleeve/D4_sleeve_plate2_ledge.3mf | 0.20 | 3, 20% | - | 0.77 | 1 Black: 20.2 / 21.2; 2 Red: 0.6 / 1.0 | 1 |
| D13_drumroll/D13_drumroll_plate1_black.3mf | 0.20 | 4, 25% | - | 1.53 | 1 Black: 37.9 / 38.4; 2 Red: 0.1 / 1.0; 3 Ivory: 0.1 / 1.5 | 6 |
| D13_drumroll/D13_drumroll_plate2_red.3mf | 0.20 | 4, 100% | - | 0.36 | 2 Red: 4.4 / 4.4 | 0 |

## What the slicer showed that the estimates did not

- Print time is lower than the old model estimates for most products (for example Vol. 01 tray 1.7 h against 4.4 h, Tape Case 1.3 h against 3.1 h, Rail 1.8 h against 2.8 h). The old rule of 19 g an hour was too slow for the A1.
- Some products are heavier than estimated: Lift 138 g (was 105), Hold 176 g (was 158), Standby 247 g (was 229).
- Purge waste matters only on the small multi-colour pieces. Mini 06 headphones is the outlier: 8 g of model, 26 g with purge, 38 colour changes, because the ivory ear pads run through many layers. Print the ear pads as their own single-colour job, or accept the waste.
- Supports are needed on four products that were described as support-free: Mini 05 mic, Crate hood, Horn stand, Standby fins (plus Perch pins). They are set to tree supports in the files. Check the scars on the first print.

## Changes made to the print files in this pass

1. Accent parts now sit on their bodies. Before this pass every STL was centred on the origin by itself, so loading a folder as one object put the inlays in the wrong place. ns.py now exports each accent in the coordinate system of its body (GROUPS table). 60 accent STLs were regenerated; the shapes are unchanged.
2. Stack knobs and handle print face down with their pins up (they had been stem down, with the cap hanging in the air).
3. Gain knob: the bore now breaks through into the head pocket. A 0.01 mm skin had sealed the pocket, so the post could never have snapped in.
4. Standby base is now solid underneath. The hollow underside needed 45 mm bridges under the show face. Sparse infill does the lightening. NS_STANDBY_POCKETS=1 brings the pockets back.
5. Rotary folder: two stale duplicate files removed (old numbering of plate B and its pointer inlay).
6. Fold and Sleeve are split over two plates each so the prime tower fits.
7. New: 00_fit_coupon, a one-colour test piece for the range's fits (see FIRST_PRINTS.md).

## Things to look at on the first prints

- Fine text is close to one nozzle line wide: Gig Coin back text, Crate tag words, Track Tag back text. If it prints faint or broken, the text needs to be made bolder in CAD.
- Press fits to measure: Hold tongue 30.0 x 10.0 into a 30.2 x 10.2 socket; Rail pegs 6.35 over ribs into 6.3 sockets; Stack pins 3.9 into 4.1; Gain post head 9.5 through an 8.6 bore; Rotary posts 3.6 in 3.9 holes; Tape Case lid plug 0.35 a side.
- Drumroll: the TPU belts are sliced by hand, not in these files. Settings: TPU 95A from the external spool, 0.2 mm layers, one wall of 0.45 mm, no top or bottom layers, no infill (or spiral vase, one belt at a time), about 25 mm/s, no retraction tuning needed for a single wall. Start with the 8 mm belt.
- PETG products (45s, Perch; Fold and Standby on request): the project files are PLA. For PETG pick the PETG filament profile in Bambu Studio, keep the Textured PEI plate (no glue), and expect slower, slightly stringier prints.

## D14 Dock (added and sliced 18 November 2026)

Sliced on GitHub by the "Slice print files" workflow (Bambu Studio 2.02.02.56 command line, A1, Textured PEI, PLA Basic). The sliced plates are in git and ready to send to the printer.
- D14_dock/D14_dock_plate1_dock.gcode.3mf: the Dock on its side, chevron face up, 4 walls, 25% gyroid, slot 1 Black. 1.92 h, 75.6 g. No supports.
- D14_dock/D14_dock_plate2_caps_red.gcode.3mf: two red caps on their side, 3 walls, 100% zig-zag, slot 2 Red. 0.72 h, 12.6 g.
- The project files (.3mf without gcode) are kept for re-slicing. Only warning: the usual bed temperature note (normal on an open A1).
- To slice anything again on GitHub: list it in SLICE_QUEUE.json and push; results land in SLICED.json and next to the project.
