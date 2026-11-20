"""Build-guide annotations for every product: which parts get which label, and which way things move.
Run: python3 guides.py [scene ...]   (renders must exist in NS_OUT/r, from render.py)"""
import sys, math
from annotate import annotate, arc

X = 30.0; T = 2.0
G = {}

G["rotary_s5"] = dict(banner="Step 5: add the loop (car fob)", labels=[
    dict(text="Loop", sub="takes the place of one key", tag="L", at=(-30, 0, 25), to=(-150, -80)),
    dict(text="Slot", sub="your fob ring goes through here", tag="S", at=(-19, 0, 25), to=(150, -110)),
    dict(text="Post", sub="loop drops over this post", tag="P", at=(-30, 0, 8), to=(-120, 120)),
], arrows=[dict(pts=[(-30, 0, 45), (-30, 0, 28)], step=1)])
G["rotary_s6"] = dict(banner="Swing the loop out, fob on a ring", labels=[
    dict(text="Loop", sub="swings out like a key", tag="L", at=(-27, 12, 7), to=(-150, 90)),
    dict(text="Split ring", sub="through the slot", tag="R", at=(-35, 17, 8), to=(-30, -120)),
    dict(text="Car fob", sub="hangs off the ring", tag="F", at=(-60, 20, 6), to=(-150, -60)),
])

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
    dict(text="Front", sub="one piece, eject mark on the face", tag="A", at=(-45, -4, 30), to=(60, 235)),
    dict(text="Slider", sub="red tab points out the back", tag="B", at=(0, -22, 72), to=(150, -150)),
    dict(text="Back plate", sub="four noses click into the pockets", tag="C", at=(30, -40, 22), to=(140, 130)),
], arrows=[
    dict(pts=[(-34, -18, 96), (-34, -4, 72)], step=1),
    dict(pts=[(34, -68, 74), (34, -46, 74)], step=2),
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

# ---------------------------------------------------------------- "how it works" pictures (name_use.webp), drawn on the finished-product
# renders. Same labels and arrows, so each step of each guide can show what the customer will actually do.
U = {}
U["eject_open"] = dict(banner="Eject: push the tab, cards fan out", labels=[
    dict(text="Cards", sub="up to six, flat", tag="A", at=(0, -3, 80), to=(150, -60)),
    dict(text="Red slider tab", sub="push up with your thumb", tag="B", at=(0, -8, 22), to=(150, 130)),
    dict(text="Front and back plate", sub="spring bars grip the cards", tag="C", at=(-44, -3, 40), to=(-150, 80)),
], arrows=[
    dict(pts=[(16, -8, 14), (16, -8, 52)], step=3),
])
U["standby"] = dict(banner="Standby: set the gaps to your laptops", labels=[
    dict(text="Closed laptop", sub="stands upright in its bay", tag="A", at=(-10, 0, 200), to=(-150, -60)),
    dict(text="Fin", sub="slide it until it just touches", tag="B", at=(20, 0, 120), to=(150, -80)),
    dict(text="Base", sub="fins stay where you leave them", tag="C", at=(100, 20, 10), to=(140, 110)),
], arrows=[
    dict(pts=[(60, 0, 100), (33, 0, 100)], step=2),
])
U["fold"] = dict(banner="Fold: built, with a laptop on it", labels=[
    dict(text="Rib", sub="waveform slots let air through", tag="A", at=(100, 0, 60), to=(150, -70)),
    dict(text="Brace", sub="ribs press down onto its notches", tag="B", at=(0, -78, 20), to=(-150, 90)),
    dict(text="Laptop", sub="front edge rests on the lips", tag="C", at=(-80, 0, 150), to=(-150, -60)),
], arrows=[
    dict(pts=[(-100, 0, 100), (-100, 0, 150)] if False else [(100, 100, 96), (100, 100, 140)], step=5),
])
U["amp_open"] = dict(banner="Stack: drawer and knobs", labels=[
    dict(text="Drawer", sub="slides in tray first", tag="A", at=(0, -40, 18), to=(-150, 60)),
    dict(text="Knobs x3", sub="pressed in flush", tag="B", at=(16, -17, 66), to=(150, -40)),
    dict(text="Pick slot", sub="stand your picks on top", tag="C", at=(0, 0, 74), to=(0, -150)),
    dict(text="Handle", tag="D", at=(0, -44, 17), to=(-110, 140)),
], arrows=[
    dict(pts=[(0, -80, 12), (0, -46, 12)], step=4),
])
U["channel"] = dict(banner="Channel: link, change, lift out", labels=[
    dict(text="Tall cup", tag="A", at=(-110, 0, 99), to=(-100, -140)),
    dict(text="Mid cup", tag="B", at=(-30, 0, 59), to=(-10, -150)),
    dict(text="Tray", tag="C", at=(90, 0, 23), to=(120, 100)),
    dict(text="Dovetail joint", sub="each module's right side slides into the next one's left", at=(0, 28, 20), to=(30, 170)),
], arrows=[
    dict(pts=[(60, 0, 40), (60, 0, 80)], step=3),
])
U["plate"] = dict(banner="Track Plate: scan it", labels=[
    dict(text="Spotify Code", sub="Spotify app, Search, camera icon, scan", tag="A", at=(0, 10, 52), to=(0, -150)),
    dict(text="Title and artist", tag="B", at=(0, 5, 22), to=(-130, 80)),
    dict(text="Base bar", sub="plate leans back, holds itself", tag="C", at=(60, -10, 10), to=(140, 100)),
])
U["songtag"] = dict(banner="Track Tag: both sides", labels=[
    dict(text="Front", sub="Spotify Code, scans from the strap", tag="A", at=(0, 12, 4), to=(120, -100)),
    dict(text="Loop strap", sub="through the hole, round your strap", tag="B", at=(20, -26, 1), to=(120, 110)),
])
U["rail"] = dict(banner="Rail: hang the bands", labels=[
    dict(text="Peg", sub="loop two or three bands over each", tag="A", at=(-80, -20, 56), to=(-60, 140)),
    dict(text="Wide cap", sub="stops bands sliding off", tag="B", at=(80, -22, 56), to=(120, 120)),
    dict(text="Rail", sub="fixed to the wall", tag="C", at=(95, -4, 76), to=(60, -120)),
])
U["headphonestand"] = dict(banner="Hold: in use", labels=[
    dict(text="Saddle", sub="headband rests here", tag="A", at=(50, 0, 250), to=(130, -120)),
    dict(text="Post", sub="press fit, fader faces the pointer", tag="B", at=(15, 0, 120), to=(140, 20)),
    dict(text="Base", sub="keep on a flat surface", tag="C", at=(58, 0, 10), to=(140, 130)),
])
U["vinylstand_record"] = dict(banner="Sleeve: add the record", labels=[
    dict(text="Ledge", sub="holds the record from the front", tag="A", at=(0, -41, 30), to=(130, 130)),
    dict(text="Feet", sub="left and right, grooves face out", tag="B", at=(55, 30, 100), to=(150, -80)),
    dict(text="Record sleeve", sub="lean it back on the cut edges", tag="C", at=(0, 30, 200), to=(-130, -80)),
])
U["cassettebox"] = dict(banner="Tape Case: opening it", labels=[
    dict(text="Lid", sub="label lines up with the notch", tag="A", at=(0, 0, 21), to=(0, -150)),
    dict(text="Thumb notch", sub="push your thumb in, lift", at=(0, -32, 16), to=(140, 100)),
], arrows=[
    dict(pts=[(0, -40, 8), (0, -40, 36)], step=2),
])
U["phonestand"] = dict(banner="Horn: where everything is", labels=[
    dict(text="Phone seat", sub="71 degrees, upright or sideways", tag="A", at=(0, 5, 100), to=(-130, -110)),
    dict(text="Sound slits", sub="under the phone's bottom speaker", tag="B", at=(17, -12, 32), to=(-160, 60)),
    dict(text="Horn mouth", sub="sound comes out here", tag="C", at=(0, -25, 20), to=(150, 90)),
    dict(text="Cable opening", sub="runs out the back", tag="D", at=(0, 26, 16), to=(150, 160)),
])
U["phonestand_horn_exploded"] = dict(banner="Horn: stand slides onto the plate", labels=[
    dict(text="Stand", sub="has a groove underneath", tag="A", at=(0, -60, 100), to=(-140, -80)),
    dict(text="Plate", sub="long tail stops it tipping back", tag="B", at=(0, 90, 5), to=(140, 90)),
    dict(text="Dovetail rail", sub="groove slides over it", tag="C", at=(0, 40, 8), to=(-140, 130)),
])
U["riser"] = dict(banner="Lift: how it sits", labels=[
    dict(text="Wedge", sub="two in the box, 14 degrees", tag="A", at=(-75, 70, 22), to=(-130, 120)),
    dict(text="Front lip", sub="stops the controller sliding", tag="B", at=(0, -49, 30), to=(120, 130)),
    dict(text="Controller", sub="rests across both wedges", tag="C", at=(0, 0, 70), to=(0, -150)),
])


# ---------------------------------------------------------------- Crate (B6)
G["crate_build"] = dict(banner="Crate: how it goes together", labels=[
    dict(text="Hood", sub="lockup on the front", tag="A", at=(40, -11, 128), to=(150, -40)),
    dict(text="Spine", sub="red, with 4 feet", tag="B", at=(-30, 8, 85), to=(-190, -40)),
    dict(text="Shell", sub="4 slots, numbered", tag="C", at=(-45, -9, 25), to=(-190, 60)),
    dict(text="Fit shims x4", sub="thin sticks only", tag="D", at=(20, -55, 18), to=(170, 150)),
    dict(text="Role tags x4", sub="flip for the other side", tag="E", at=(-20, -85, 10), to=(-170, 150)),
], arrows=[
    dict(pts=[(0, 8, 105), (0, 8, 52)], step=1),
    dict(pts=[(0, -80, 6), (0, -30, 22)], step=2),
    dict(pts=[(-60, -11, 160), (-60, -11, 138)], step=4),
])
G["crate_s1"] = dict(banner="1  Pick your parts", labels=[
    dict(text="Shell", tag="C", at=(0, 0, 25), to=(-60, -140)),
    dict(text="Spine", tag="B", at=(-128, 8, 25), to=(-120, 150)),
    dict(text="Hood", tag="A", at=(128, -9, 55), to=(100, -130)),
    dict(text="Shims", tag="D", at=(-55, -52, 18), to=(-80, 150)),
    dict(text="Tags", tag="E", at=(52, -52, 10), to=(110, 150)),
])
G["crate_s2"] = dict(banner="2  Drop the red spine in from the top", labels=[
    dict(text="Spine", sub="feet point down, into the pockets", tag="B", at=(0, 8, 70), to=(-190, -80)),
    dict(text="Shell", tag="C", at=(-45, -9, 20), to=(-190, 120)),
], arrows=[dict(pts=[(0, 8, 105), (0, 8, 52)], step=1)])
G["crate_s3"] = dict(banner="3  Press a tag into each recess", labels=[
    dict(text="Role tag", sub="Main, Backup, Rec, Spare", tag="E", at=(36, -9, 19), to=(150, -110)),
    dict(text="Red window", sub="red means the stick is missing", tag="", at=(-36, -9, 6), to=(-190, 130)),
], arrows=[dict(pts=[(36, -40, 19), (36, -12, 19)], step=2)])
G["crate_s4"] = dict(banner="4  Drop the sticks in, connector down", labels=[
    dict(text="Stick", sub="connector goes down first", tag="F", at=(-12, -1, 70), to=(-170, -80)),
    dict(text="Silver in the window", sub="means it is home", tag="", at=(-12, -9, 6), to=(-190, 130)),
], arrows=[dict(pts=[(-12, -1, 100), (-12, -1, 62)], step=3)])
G["crate_s5"] = dict(banner="5  Press the hood on until it clicks", labels=[
    dict(text="Hood", sub="detent bumps click it shut", tag="A", at=(0, -10, 85), to=(150, 170)),
], arrows=[dict(pts=[(-40, 0, 115), (-40, 0, 76)], step=4)])
U["crate_open"] = dict(banner="Crate: what is home", labels=[
    dict(text="Silver", sub="connector home, stick is in", tag="A", at=(-36, -9, 6), to=(-190, 120)),
    dict(text="Red", sub="foot shows, stick is missing", tag="B", at=(36, -9, 6), to=(150, 140)),
    dict(text="Role tag", sub="flip it, relabel it", tag="C", at=(0, -9, 19), to=(140, -120)),
])

import os
from annotate import OUT
OUT_DIR = OUT + "/r"
SRC = "/home/claude/no-skips/img"
def run(names):
    for n in names or G:
        g = G[n]
        src = f"{SRC}/{n}.webp" if (n in ("amp_build","plate_build","standee_build","knob_build","rail_build","coin","cassettebox_open","vinylstand_build","headphonestand_build","fold_flat","studio_set","channel_build","eject_build","standby_build","nametag") and os.path.exists(f"{SRC}/{n}.webp")) else None
        print(annotate(n, g.get("labels", ()), g.get("arrows", ()), banner=g.get("banner"), src=src))

def run_use(names):
    for n in names or U:
        g = U[n]; src = f"{SRC}/{n}.webp"
        print(annotate(n, g.get("labels", ()), g.get("arrows", ()), banner=g.get("banner"), src=src, out=f"{OUT_DIR}/{n}_use"))

if __name__ == "__main__":
    if sys.argv[1:2] == ["use"]: run_use(sys.argv[2:])
    else: run(sys.argv[1:])
