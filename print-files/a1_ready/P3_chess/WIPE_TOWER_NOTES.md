# Wipe tower on two-colour chess plates (26 Nov 2026)

Measured on the solid queen plate (red dot in the last 3 layers), A1, Bambu Studio 02.02.02.56:

| Variant | Time | Plate weight | Tower |
| --- | --- | --- | --- |
| Baseline (current P3_test_queen) | 1 h 06 | 30.8 g | prints in all 240 layers |
| No sparse layers (wipe_tower_no_sparse_layers=1) | 0 h 53 | 25.7 g | only layers 238 to 240 |
| Narrow tower (prime_tower_width 20) | 1 h 06 | 30.8 g | no change (setting had no effect) |
| Half flush (flush_multiplier 0.5) | 1 h 05 | 30.2 g | same tower, red purge halved |
| All three | 0 h 52 | 25.1 g | only layers 238 to 240 |

- Waste on the baseline is about 6 g: tower about 3.2 g plus the purge at each colour change. The queen itself is about 24.3 g.
- "No sparse layers" saves 5 g and 13 min but prints the tower in mid-air at z 47 mm (layers 238 to 240 only, nothing under it). Not used: it risks a stringy blob and a failed swap. The full-height tower is what gives the swap a solid column to purge on.
- Half flush saves only 0.6 g and raises the risk of ivory tint in the red dot. Not used.
- Decision: keep the default tower. Single-colour plates have no tower. To cut waste in production, put several two-colour pieces of the same colour pair on one plate so they share one tower (for example ivory queen and ivory king together).
