"""Build-guide annotations for every product: which parts get which label, and which way things move.
Run: python3 guides.py [scene ...]   (renders must exist in NS_OUT/r, from render.py)"""
import sys, math
from annotate import annotate, arc

X = 30.0; T = 2.0
G = {}

# ---------------------------------------------------------------- Rotary (D12)
G["rotary_s1"] = dict(banner="1  Pick your parts", labels=[
    dict(text="Plate B", sub="red line on top", tag="B", at=(0, 0, 40), to=(-250, -70)),
    dict(text="Plate A", sub="plain", tag="A", at=(-30, 0, 2), to=(-250, 40)),
    dict(text="Short posts", sub="2 to 4 keys", tag="1", at=(-14, -28, 4), to=(-260, 135)),
    dict(text="Long posts", sub="4 to 7 keys", tag="2", at=(14, -28, 6), to=(255, 140)),
    dict(text="Loop", sub="for a car fob", tag="L", at=(0, 32, 1.5), to=(-160, -90)),
    dict(text="Spacers", sub="fill any gap", tag="S", at=(49, 32, 0.5), to=(150, -80)),
])

G["rotary_s2"] = dict(banner="2  Stack the keys on the posts", labels=[
    dict(text="Plate A", tag="A", at=(-38, -8, 1), to=(-60, 120)),
    dict(text="Post", sub="pushed up from below", tag="P", at=(-30, 0, 9), to=(-120, -90)),
    dict(text="Keys already on", sub="one from each post", tag="K", at=(30, -8, 3), to=(150, 70)),
    dict(text="Next key", sub="bow over the post", tag="K", at=(38, 0, 15), to=(170, -20)),
    dict(text="Spacer", sub="goes on last", tag="S", at=(30, 0, 24.5), to=(150, -110)),
], arrows=[
    dict(pts=[(30, 6, 40), (30, 6, 26.5)]),
    dict(pts=[(34, 12, 23), (34, 12, 7.8)]),
])
G["rotary_s3"] = dict(banner="3  Press plate B on until it clicks", labels=[
    dict(text="Plate B", sub="red line facing up", tag="B", at=(-30, 0, 32), to=(-150, -90)),
    dict(text="Click", sub="each post head snaps in", tag="", at=(30, 0, 12), to=(165, -10)),
    dict(text="Keys stay between the plates", tag="K", at=(-30, -8, 5), to=(-80, 135)),
], arrows=[
    dict(pts=[(-30, 0, 44), (-30, 0, 14)]),
    dict(pts=[(30, 0, 44), (30, 0, 14)]),
])
G["rotary_s4"] = dict(banner="4  Swing a key out, fold it back", labels=[
    dict(text="Pivot post", tag="P", at=(30, 0, 10), to=(160, 70)),
    dict(text="Key swings out", tag="K", at=(40, 25, 6), to=(165, -20)),
    dict(text="Fold back flat", sub="between the plates", tag="", at=(-20, 0, 9), to=(-150, 90)),
], arrows=[
    dict(pts=arc((30, 0), 46, 172, 70, 11), kind="turn"),
])

# ---------------------------------------------------------------- the rest of the range. One labelled image per product,
# built on the exploded "build" scene. Arrow badges match the numbered steps on the site.
G["amp_build"] = dict(banner="Stack: how it goes together", labels=[
    dict(text="Head", tag="A", at=(35, 0, 100), to=(150, -60)),
    dict(text="Base", tag="B", at=(35, 0, 20), to=(140, 40)),
    dict(text="Drawer", tag="C", at=(-33, -60, 18), to=(-150, 60)),
    dict(text="Knobs x3", sub="ivory", tag="D", at=(-16, -44, 100), to=(-150, -60)),
    dict(text="Handle", sub="ivory", tag="E", at=(0, -103, 17), to=(-140, 105)),
], arrows=[
    dict(pts=[(-16, -62, 108), (-16, -26, 108)], step=1),
    dict(pts=[(0, -125, 17), (0, -86, 17)], step=2),
    dict(pts=[(-40, 0, 112), (-40, 0, 44)], step=3),
    dict(pts=[(30, -42, 8), (30, -20, 8)], step=4),
])
G["plate_build"] = dict(banner="Track Plate: how it goes together", labels=[
    dict(text="Plate", sub="code or sound wave", tag="A", at=(-50, 40, 3), to=(-120, 90)),
    dict(text="Base bar", tag="B", at=(-70, -55, 14), to=(-100, -120)),
    dict(text="Red stripe faces you", at=(30, -60, 15), to=(130, -110)),
], arrows=[
    dict(pts=[(-110, -60, 8), (-110, -60, 8)] if False else [(0, -8, 6), (0, -12, 34), (0, -48, 24)], step=2),
])
G["standee_build"] = dict(banner="Side A: how it goes together", labels=[
    dict(text="Rail section 1", tag="A", at=(-100, 12, 10), to=(-110, 120)),
    dict(text="Rail section 2", sub="dovetail on its end", tag="B", at=(110, 5, 10), to=(110, 130)),
    dict(text="Cassettes x4", sub="track one on the left", tag="C", at=(-40, -52, 5), to=(-130, -90)),
], arrows=[
    dict(pts=[(60, 10, 36), (6, 10, 36), (6, 10, 14)], step=1),
    dict(pts=[(-40, -30, 16), (-40, -2, 20)], step=2),
])
G["knob_build"] = dict(banner="Gain: how it goes together", labels=[
    dict(text="Knob", sub="the cap", tag="A", at=(0, -13, 40), to=(150, -40)),
    dict(text="Base", sub="post inside", tag="B", at=(22, 0, 8), to=(150, 90)),
], arrows=[
    dict(pts=[(0, 0, 66), (0, 0, 22)], step=1),
    dict(pts=arc((0, 0), 30, 200, 20, 50), kind="turn", step=2),
])
G["rail_build"] = dict(banner="Rail: how it goes together", labels=[
    dict(text="Rail", tag="A", at=(-95, -4, 70), to=(-70, -110)),
    dict(text="Pegs x5", sub="red, press in by hand", tag="B", at=(86, -40, 56), to=(120, 100)),
    dict(text="Screw heads sit below the face", at=(-60, -9, 68), to=(-120, 90)),
], arrows=[
    dict(pts=[(-100, -40, 92), (-100, -2, 92)], step=1),
    dict(pts=[(0, -56, 68), (0, -8, 68)], step=2),
    dict(pts=[(40, -56, 68), (40, -8, 68)], step=2),
    dict(pts=[(80, -56, 68), (80, -8, 68)], step=2),
])
G["coin"] = dict(banner="Gig Coin: how it goes together", labels=[
    dict(text="Coin", tag="A", at=(-16, 8, 40), to=(150, -100)),
    dict(text="Frame", sub="split at the bottom", tag="B", at=(-30, 12, 50), to=(-130, -60)),
    dict(text="Foot", sub="holds the split shut", tag="C", at=(34, -20, 3), to=(130, 100)),
], arrows=[
    dict(pts=[(36, -38, 18), (12, -10, 14)], step=2),
])
G["cassettebox_open"] = dict(banner="Tape Case: how it opens", labels=[
    dict(text="Tray", sub="narrow side for picks", tag="A", at=(0, 0, 18), to=(-60, -130)),
    dict(text="Lid", sub="label with your text", tag="B", at=(110, 0, 7), to=(60, -140)),
    dict(text="Thumb notch", sub="front edge", at=(110, -32, 5), to=(120, 110)),
], arrows=[
    dict(pts=[(110, 0, 40), (24, 0, 28)], step=2),
])
G["vinylstand_build"] = dict(banner="Sleeve: how it goes together", labels=[
    dict(text="Foot, left", sub="grooves face out", tag="A", at=(-67, 30, 110), to=(-170, -60)),
    dict(text="Foot, right", tag="B", at=(67, 30, 110), to=(170, -60)),
    dict(text="Ledge", sub="Now Spinning", tag="C", at=(0, -71, 61), to=(0, 150)),
], arrows=[
    dict(pts=[(-110, -71, 100), (-110, -71, 62)], step=2),
    dict(pts=[(-67, -90, 112), (-67, -60, 112)], step=1) if False else dict(pts=[(110, -71, 100), (110, -71, 62)], step=2),
])
G["headphonestand_build"] = dict(banner="Hold: how it goes together", labels=[
    dict(text="Saddle", sub="red arc faces front", tag="C", at=(54, 0, 290), to=(150, -60)),
    dict(text="Post", sub="fader faces the pointer", tag="B", at=(15, 0, 150), to=(150, 40)),
    dict(text="Base", tag="A", at=(58, 0, 10), to=(150, 130)),
], arrows=[
    dict(pts=[(0, 0, 250), (0, 0, 40)] if False else [(-30, 0, 80), (-30, 0, 24)], step=1),
    dict(pts=[(-70, 0, 350), (-70, 0, 318)], step=2),
])
G["fold_flat"] = dict(banner="Fold: how it goes together", labels=[
    dict(text="Brace x2", sub="notches up, red bars to you", tag="A", at=(-60, 70, 6), to=(-190, 140)),
    dict(text="Rib x2", sub="tall end at the back", tag="B", at=(60, -2, 9), to=(160, -110)),
], arrows=[
    dict(pts=[(-100, -2, 70), (-100, -2, 14)], step=2),
    dict(pts=[(100, 2, 70), (100, 2, 14)], step=3),
])
G["channel_build"] = dict(banner="Channel: how it links", labels=[
    dict(text="Tall cup", tag="A", at=(-110, 10, 99), to=(-100, -110)),
    dict(text="Mid cup", tag="B", at=(-30, 0, 90), to=(0, -150)),
    dict(text="Tray", sub="dovetail on its right", tag="C", at=(130, -10, 23), to=(100, 140)),
], arrows=[
    dict(pts=[(-30, 0, 130), (-30, 0, 98)] if False else [(-50, 0, 110), (-50, 0, 96)], step=2),
])
G["eject_build"] = dict(banner="Eject: how it goes together", labels=[
    dict(text="Tray", tag="A", at=(45, 3, 40), to=(150, 0)),
    dict(text="Face plate", sub="eject mark bottom right", tag="B", at=(45, -40, 30), to=(150, 140)),
    dict(text="Slider", sub="red tab pokes out the back", tag="C", at=(42, -16, 76), to=(150, -110)),
], arrows=[
    dict(pts=[(0, -16, 112), (0, -16, 86)], step=1),
    dict(pts=[(0, -80, 34), (0, -48, 34)] if False else [(0, -80, 34), (0, -50, 34)], step=2),
])
G["standby_build"] = dict(banner="Standby: how it goes together", labels=[
    dict(text="Base", sub="dovetail channel", tag="A", at=(115, 0, 8), to=(-20, 180)),
    dict(text="Fins x3", sub="slide in from either end", tag="B", at=(40, 0, 100), to=(150, -80)),
], arrows=[
    dict(pts=[(-150, 0, 20), (-100, 0, 20)], step=1),
    dict(pts=[(-12, 62, 20), (-12, 62, 20)]) if False else dict(pts=[(30, 62, 4), (60, 62, 4)], step=2),
])
G["nametag"] = dict(banner="Alias: how the loop goes on", labels=[
    dict(text="Tag", tag="A", at=(30, 12, 4), to=(140, -80)),
    dict(text="Loop strap", sub="T-bar end first", tag="B", at=(60, -26, 1), to=(120, 110)),
], arrows=[
    dict(pts=[(-60, -26, 6), (-30, 4, 12)], step=1),
])

# ---- second pass, after checking each against its render
G["amp_build"] = dict(banner="Stack: how it goes together", labels=[
    dict(text="Head", tag="A", at=(35, 0, 100), to=(120, -95)),
    dict(text="Base", tag="B", at=(35, 0, 20), to=(140, 40)),
    dict(text="Drawer", tag="C", at=(-33, -60, 18), to=(-150, 60)),
    dict(text="Knobs x3", sub="ivory", tag="D", at=(21, -44, 96), to=(165, 20)),
    dict(text="Handle", sub="ivory", tag="E", at=(0, -103, 17), to=(-140, 105)),
], arrows=[
    dict(pts=[(-16, -66, 96), (-16, -30, 96)], step=1),
    dict(pts=[(0, -125, 17), (0, -86, 17)], step=2),
    dict(pts=[(-44, 0, 114), (-44, 0, 44)], step=3),
    dict(pts=[(30, -42, 8), (30, -20, 8)], step=4),
])
G["plate_build"] = dict(banner="Track Plate: how it goes together", labels=[
    dict(text="Plate", sub="code or sound wave", tag="A", at=(55, 45, 3), to=(60, 125)),
    dict(text="Base bar", sub="red stripe faces you", tag="B", at=(-70, -55, 14), to=(-90, -120)),
    dict(text="Slot", sub="plate leans back 12 degrees", at=(30, -46, 14), to=(110, -130)),
], arrows=[
    dict(pts=[(0, 6, 20), (0, -24, 54), (0, -44, 20)], step=2),
])
G["standee_build"] = dict(banner="Side A: how it goes together", labels=[
    dict(text="Rail section 1", tag="A", at=(-100, 12, 10), to=(-100, 125)),
    dict(text="Rail section 2", sub="dovetail on its end", tag="B", at=(110, 5, 10), to=(120, 125)),
    dict(text="Cassette", sub="x4, track one on the left", tag="C", at=(-40, -52, 5), to=(-110, -125)),
], arrows=[
    dict(pts=[(60, 10, 40), (6, 10, 40), (6, 10, 14)], step=1),
    dict(pts=[(-40, -40, 30), (-40, -8, 30), (-40, -2, 12)], step=2),
])
G["knob_build"] = dict(banner="Gain: how it goes together", labels=[
    dict(text="Knob", sub="the cap", tag="A", at=(0, -13, 40), to=(160, -60)),
    dict(text="Base", sub="post inside", tag="B", at=(22, 0, 8), to=(150, 90)),
], arrows=[
    dict(pts=[(0, 0, 64), (0, 0, 22)], step=1),
    dict(pts=arc((0, 0), 19, 215, 30, 50), kind="turn", step=2),
])
G["rail_build"] = dict(banner="Rail: how it goes together", labels=[
    dict(text="Rail", tag="A", at=(-95, -4, 70), to=(-60, -115)),
    dict(text="Pegs x5", sub="red, press in by hand", tag="B", at=(86, -40, 56), to=(110, 100)),
    dict(text="Wall side", sub="2 screws or mounting tape", at=(-100, -4, 50), to=(-30, 120)),
], arrows=[
    dict(pts=[(-6, -56, 68), (-6, -26, 68)], step=2),
    dict(pts=[(40, -56, 68), (40, -26, 68)], step=2),
    dict(pts=[(80, -56, 68), (80, -26, 68)], step=2),
])
G["coin_build"] = dict(banner="Gig Coin: how it goes together", labels=[
    dict(text="Coin", sub="back text facing down", tag="A", at=(0, 12, 36), to=(150, -80)),
    dict(text="Frame", sub="split at the bottom", tag="B", at=(-22, 12, 3), to=(-150, 20)),
    dict(text="Foot", sub="holds the split shut", tag="C", at=(14, -52, 9), to=(150, 110)),
], arrows=[
    dict(pts=[(0, 0, 66), (0, 0, 26)], step=1),
    dict(pts=[(0, -62, 14), (0, -36, 14)], step=2),
])
G["cassettebox_open"] = dict(banner="Tape Case: how it opens", labels=[
    dict(text="Tray", sub="narrow side for picks", tag="A", at=(0, 0, 18), to=(-60, -130)),
    dict(text="Lid", sub="label with your text", tag="B", at=(110, 10, 7), to=(110, -130)),
    dict(text="Thumb notch", sub="front edge", at=(110, -32, 4), to=(120, 120)),
], arrows=[
    dict(pts=[(96, 0, 48), (24, 0, 34)], step=2),
])
G["vinylstand_build"] = dict(banner="Sleeve: how it goes together", labels=[
    dict(text="Foot, left", sub="grooves face out", tag="A", at=(-67, 30, 110), to=(-170, -60)),
    dict(text="Foot, right", tag="B", at=(67, 30, 110), to=(170, -60)),
    dict(text="Ledge", sub="Now Spinning", tag="C", at=(0, -71, 61), to=(0, 150)),
], arrows=[
    dict(pts=[(-77, -71, 110), (-77, -71, 82)], step=2),
    dict(pts=[(77, -71, 110), (77, -71, 82)], step=2),
])
G["headphonestand_build"] = dict(banner="Hold: how it goes together", labels=[
    dict(text="Saddle", sub="red arc faces front", tag="C", at=(54, 0, 290), to=(150, -60)),
    dict(text="Post", sub="fader faces the pointer", tag="B", at=(15, 0, 150), to=(150, 40)),
    dict(text="Base", tag="A", at=(58, 0, 10), to=(150, 130)),
], arrows=[
    dict(pts=[(-30, 0, 90), (-30, 0, 26)], step=1),
    dict(pts=[(-70, 0, 330), (-70, 0, 296)], step=2),
])
G["fold_flat"] = dict(banner="Fold: how it goes together", labels=[
    dict(text="Brace x2", sub="notches up, red bars to you", tag="A", at=(-60, 70, 6), to=(-170, 135)),
    dict(text="Rib x2", sub="tall end at the back", tag="B", at=(60, -2, 9), to=(150, -120)),
    dict(text="Notches", sub="press each rib down onto them", at=(-110, 85, 6), to=(-110, 175)),
])
G["eject_build"] = dict(banner="Eject: how it goes together", labels=[
    dict(text="Tray", tag="A", at=(-44, 3, 55), to=(-150, -60)),
    dict(text="Face plate", sub="eject mark bottom right", tag="B", at=(30, -40, 18), to=(150, 130)),
    dict(text="Slider", sub="red tab pokes out the back", tag="C", at=(42, -16, 76), to=(150, -110)),
], arrows=[
    dict(pts=[(-30, -16, 100), (-30, -16, 86)], step=1),
    dict(pts=[(-60, -80, 34), (-60, -48, 34)], step=2),
])
G["nametag"] = dict(banner="Alias: how the loop goes on", labels=[
    dict(text="Tag", tag="A", at=(30, 12, 4), to=(140, -80)),
    dict(text="Loop strap", sub="T-bar end through the hole first", tag="B", at=(40, -26, 1), to=(110, 120)),
], arrows=[
    dict(pts=[(-60, -26, 6), (-30, 4, 12)], step=1),
])

G["plate_build"] = dict(banner="Track Plate: how it goes together", labels=[
    dict(text="Plate", sub="code or sound wave", tag="A", at=(-55, 45, 3), to=(-120, -70)),
    dict(text="Base bar", sub="red stripe faces you", tag="B", at=(-70, -55, 14), to=(-90, -120)),
    dict(text="Slot", sub="plate leans back 12 degrees", at=(30, -46, 14), to=(110, -135)),
], arrows=[
    dict(pts=[(0, 6, 20), (0, -24, 54), (0, -44, 20)], step=2),
])
G["headphonestand_build"] = dict(banner="Hold: how it goes together", labels=[
    dict(text="Saddle", sub="step 2: press down, red arc faces front", tag="C", at=(54, 0, 290), to=(120, -75)),
    dict(text="Post", sub="fader faces the pointer", tag="B", at=(15, 0, 150), to=(150, 40)),
    dict(text="Base", tag="A", at=(58, 0, 10), to=(150, 130)),
], arrows=[
    dict(pts=[(-30, 0, 90), (-30, 0, 26)], step=1),
])
G["fold_flat"] = dict(banner="Fold: how it goes together", labels=[
    dict(text="Brace x2", sub="notches up, red bars to you", tag="A", at=(-60, 70, 6), to=(-110, 165)),
    dict(text="Rib x2", sub="tall end at the back", tag="B", at=(60, -2, 9), to=(150, -120)),
])

G["studio_set"] = dict(banner="Vol. 01: where each piece goes", labels=[
    dict(text="Turntable", sub="front left", tag="1", at=(-53, -14, 12), to=(-120, 140)),
    dict(text="Drum machine", sub="front centre", tag="2", at=(6, -14, 14), to=(0, 190)),
    dict(text="Mixer", sub="front right", tag="3", at=(60, -14, 14), to=(150, 130)),
    dict(text="Mic", sub="back left", tag="4", at=(-60, 38, 52), to=(-110, -80)),
    dict(text="Headphones", sub="press the cups into their pockets", tag="5", at=(-2, 38, 40), to=(10, -130)),
    dict(text="Synth", sub="back right", tag="6", at=(50, 38, 13), to=(150, -80)),
    dict(text="Set number on the front lip", at=(-30, -52, 5), to=(-70, 175)),
])

import os
SRC = "/home/claude/no-skips/img"
def run(names):
    for n in names or G:
        g = G[n]
        src = f"{SRC}/{n}.webp" if (n in ("amp_build","plate_build","standee_build","knob_build","rail_build","coin","cassettebox_open","vinylstand_build","headphonestand_build","fold_flat","studio_set","channel_build","eject_build","standby_build","nametag") and os.path.exists(f"{SRC}/{n}.webp")) else None
        print(annotate(n, g.get("labels", ()), g.get("arrows", ()), banner=g.get("banner"), src=src))
if __name__ == "__main__": run(sys.argv[1:])
