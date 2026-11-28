"""Renders for P6A Deck box, using the studio set-up in render.py. Writes img/deckbox_closed.webp and img/deckbox_open.webp.
Usage (from the repo root, after build_p6a_deckbox.py with the same NS_OUT): NS_OUT=/tmp/p6a python3 print-files/cad/render_p6a.py [--draft]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from PIL import Image

R.SHOTS.update({
    "deckbox_closed": dict(az=-30, el=30, zoom=1.0, soft=0.8),     # Night in front, Bone behind it to the right
    "deckbox_open": dict(az=-34, el=40, zoom=1.0, soft=0.8),       # Night with the lid slid half out, deck inside
})
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "img")

if __name__ == "__main__":
    draft = "--draft" in sys.argv
    for sc in ("deckbox_closed", "deckbox_open"):
        if [a for a in sys.argv[1:] if not a.startswith("--")] and sc not in sys.argv: continue
        R.render(sc, draft)
        if not draft:
            Image.open(f"{R.OUT}/r/{sc}.jpg").save(os.path.join(IMG, sc.replace("deckbox_", "deckbox_") + ".webp"), quality=86)
