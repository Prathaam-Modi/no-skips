"""Renders for P6C Dealer button. Run build_p6c_dealer.py first (same NS_OUT), then: python3 render_p6c.py [--draft]
Writes img/dealer_set.webp (the set of three on a table) and img/dealer_close.webp (close-up of the dealer button, front and back)."""
import os, sys
os.environ.setdefault("NS_OUT", "/tmp/p6c_out")
import render as R
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "..", "img")
R.SHOTS.update({
    "dealer_set": dict(az=-18, el=46, zoom=1.25, soft=0.75, focus=("ivory", "red", "black")),
    "dealer_close": dict(az=-20, el=40, zoom=1.15, soft=0.75, focus=("ivory", "red")),
})
if __name__ == "__main__":
    for s in ("dealer_set", "dealer_close"):
        R.render(s, "--draft" in sys.argv)
        Image.open(f"{R.OUT}/r/{s}.jpg").save(os.path.join(IMG, f"{s}.webp"), quality=86)
        print("saved", s, flush=True)
