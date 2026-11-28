"""Renders for P6B Hand rack, using the shared studio setup in render.py (not edited: shots and the card colour are added here).
Usage: NS_OUT=/tmp/p6b python3 render_p6b.py [--draft] [scene,scene]   -> img/handrack.webp, img/handrack_stack.webp"""
import os, sys
from PIL import Image
import render as R

R.COL["card"] = (0.74, 0.72, 0.67, 0.42)           # plain card blank, warm white
R.SHOTS.update({
    "handrack": dict(az=-26, el=24, zoom=1.0, soft=0.7),         # the player's view: faces of a 13 card hand on the arc
    "handrack_stack": dict(az=-32, el=24, zoom=1.0, soft=0.7),   # four racks stacked, one standing in front
})
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "img")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for s in (args[0].split(",") if args else ["handrack", "handrack_stack"]):
        R.render(s, "--draft" in sys.argv)
        Image.open(f"{R.OUT}/r/{s}.jpg").save(os.path.join(IMG, s + ".webp"), quality=84, method=6)
        print("saved", s + ".webp", flush=True)
