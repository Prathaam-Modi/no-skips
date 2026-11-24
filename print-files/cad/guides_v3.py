"""V3 build-guide pictures: Patched In (click) and Ripple (press the dot in). Run: python3 guides_v3.py render|annotate"""
import sys
import render
from annotate import annotate
SH = {"patched": dict(az=-24, el=36, zoom=1.0), "patched_clicked": dict(az=-24, el=34, zoom=1.0), "ripple_black": dict(az=-24, el=40, zoom=1.0)}
render.SHOTS.update(SH)
import annotate as A
A.SHOTS.update(SH) if hasattr(A, "SHOTS") else None
G = {
 "patched": dict(banner="Patched In: plug and socket", labels=[
    dict(text="Plug", sub="black, with the red collar", tag="A", at=(10, -12, 14), to=(-170, 60)),
    dict(text="Pin", sub="this end goes in the socket", tag="P", at=(44, -12, 7), to=(150, 120)),
    dict(text="Socket", sub="ivory, jaws at the open end", tag="B", at=(10, 14, 14), to=(-150, -110)),
    dict(text="Split top", sub="two jaws that grip the pin", tag="J", at=(24, 14, 14), to=(160, -80)),
 ], arrows=[]),
 "patched_clicked": dict(banner="Patched In: pushed together", labels=[
    dict(text="Socket", tag="B", at=(-20, 0, 14), to=(-120, -120)),
    dict(text="Plug", tag="A", at=(25, 0, 14), to=(130, -110)),
    dict(text="Click", sub="you hear and feel it seat", tag="", at=(0, 0, 8), to=(10, 130)),
 ], arrows=[dict(pts=[(38, 0, 20), (12, 0, 20)], step=2, text="push", text_off=(0, -22))]),
 "ripple_black": dict(banner="Ripple: press the red dot in", labels=[
    dict(text="Red dot", sub="the centre of the ripples", tag="A", at=(0, 4, 3.8), to=(160, -120)),
    dict(text="Name lip", sub="front edge, your name", tag="B", at=(0, -44, 18), to=(-150, 100)),
 ], arrows=[dict(pts=[(0, 4, 30), (0, 4, 6)], step=1, text="press", text_off=(14, -10))]),
}
if __name__ == "__main__":
    if sys.argv[1] == "render":
        for s in sys.argv[2].split(","): render.render(s)
    else:
        for n, g in G.items(): print(annotate(n, g["labels"], g["arrows"], banner=g["banner"]))
