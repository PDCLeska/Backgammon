"""Drawing of the pin-test setup on the Carvera Air bed (top view + side cut). Out: art/pintest_setup.png"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as R, Circle as C, Polygon as P, FancyArrowPatch as A
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(ROOT, "cad")]
import pintest as pt

L, W, T = pt.L, pt.W, pt.T
BX, BY = 360, 240            # bed drawn (schematic)
OX, OY = 30, 30              # blank's front-left corner on the bed (against the bracket)
fig = plt.figure(figsize=(13, 9.2), dpi=130)
ax = fig.add_axes([0.03, 0.30, 0.94, 0.66])
ax.add_patch(R((0, 0), BX, BY, fc="#c9ccd1", ec="#666"))                       # aluminium bed
for x in range(20, BX, 40):
    for y in range(20, BY, 40):
        ax.add_patch(C((x, y), 3, fc="#9aa0a8", ec="none"))                    # bed holes
ax.add_patch(R((6, 6), BX - 12, BY - 12, fc="#c8a97e", ec="#8a6d45", alpha=0.85))   # spoil board
# L bracket (front-left)
ax.add_patch(P([(OX - 14, OY - 14), (OX + 110, OY - 14), (OX + 110, OY), (OX, OY), (OX, OY + 80), (OX - 14, OY + 80)],
               fc="#3d4652", ec="k"))
for x, y in ((OX - 7, OY + 15), (OX - 7, OY + 60), (OX + 30, OY - 7), (OX + 90, OY - 7)):
    ax.add_patch(C((x, y), 2.6, fc="#bbb", ec="k", lw=0.5))
ax.text(OX - 7, OY + 37, "L bracket\n(Anchor 1)\npins + screws", color="w", fontsize=7, rotation=90, ha="center", va="center")
# far end of the spoil board held down
for x, y in ((BX - 20, 20), (BX - 20, BY - 20)):
    ax.add_patch(C((x, y), 5, fc="#444", ec="k")); ax.text(x - 9, y, "screw /\nclamp", fontsize=6.5, ha="right", va="center")
# blank (setup 1: back up) with tape
ax.add_patch(R((OX, OY), L, W, fc="#bfe4e6", ec="#1f7f86", lw=1.4, alpha=0.95))
for k in range(4):
    ax.add_patch(R((OX + 8 + k * 36, OY + 3), 26, W - 6, fc="#4a90d9", alpha=0.10, ec="#4a90d9", ls=":", lw=0.6))
bm = pt.back_map()
for l in bm["lines"]:
    p = np.array(l["pts"]); ax.plot(p[:, 0] + OX + L / 2, p[:, 1] + OY + W / 2, color="#1d3b4a", lw=0.4)
for px in pt.PIN_X:
    x, y = pt.setup_xy(px, 0, 1)
    ax.add_patch(C((x + OX, y + OY), 2.0, fc="#d33", ec="k", lw=0.6))
ax.plot([OX - 5, OX + L + 5], [OY + W / 2] * 2, color="#d33", ls=":", lw=0.9)
ax.text(OX + L + 7, OY + W / 2, "flip line\n(through the pins)", color="#d33", fontsize=8, va="center")
for wx, wy in pt.WIT:
    x, y = pt.setup_xy(wx, wy, 1); a = pt.WIT_BACK
    ax.add_patch(R((x + OX - a / 2, y + OY - a / 2), a, a, fc="#555"))
ax.plot(OX, OY, "o", ms=9, mfc="none", mec="#e60", mew=2)
ax.annotate("XY zero = blank's front-left corner\n(against the bracket)", (OX, OY), (OX + 118, OY - 20), fontsize=8,
            color="#e60", arrowprops=dict(arrowstyle="->", color="#e60"))
x1, y1 = pt.setup_xy(pt.PIN_X[0], 0, 1); x2, _ = pt.setup_xy(pt.PIN_X[1], 0, 1)
ax.annotate(f"pin hole 4 mm\nX {x1:.0f}, Y {y1:.1f}", (x1 + OX, y1 + OY), (x1 + OX + 8, y1 + OY + 30), fontsize=7.5, bbox=dict(fc="w", ec="none", alpha=0.85),
            arrowprops=dict(arrowstyle="->"))
ax.annotate(f"pin hole 4 mm\nX {x2:.0f}, Y {y1:.1f}", (x2 + OX, y1 + OY), (x2 + OX - 30, y1 + OY + 30), fontsize=7.5, bbox=dict(fc="w", ec="none", alpha=0.85),
            arrowprops=dict(arrowstyle="->"))
ax.text(OX + L / 2, OY + W + 15, f"epoxy blank {L:.0f} x {W:.0f} x {T:.0f}, BACK UP (setup 1): map, witness squares, pin holes",
        ha="center", fontsize=8.5, color="#1f7f86")
ax.text(OX + 55, OY + 5, "painter's tape + CA (under the blank)", fontsize=6.5, color="#2a5d99")
ax.text(BX - 10, 12, "2 mm MDF spoil board", ha="right", fontsize=8, color="#5b4422")
ax.text(BX - 10, BY - 3, "Carvera Air bed (drawn schematic; the blank is to scale)", ha="right", va="top", fontsize=7, color="#555")
ax.annotate("", (OX + L, OY + W + 6), (OX, OY + W + 6), arrowprops=dict(arrowstyle="<->", lw=0.7))
ax.text(OX + L / 2, OY + W + 8, "X  150", ha="center", fontsize=7.5)
ax.annotate("", (OX + L + 40, OY + W), (OX + L + 40, OY), arrowprops=dict(arrowstyle="<->", lw=0.7))
ax.text(OX + L + 43, OY + 20, "Y  101", fontsize=7.5)
ax.set_xlim(-5, BX + 5); ax.set_ylim(-5, BY + 5); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Top view: setup on the bed", fontsize=11)

# side cut through the pins
bx = fig.add_axes([0.06, 0.03, 0.88, 0.22])
z_bed, z_sp = -6, 0
bx.add_patch(R((-10, z_bed), L + 20, 6, fc="#c9ccd1", ec="#666"))
bx.add_patch(R((-10, 0), L + 20, 2, fc="#c8a97e", ec="#8a6d45"))
bx.add_patch(R((0, 2.15), L, T, fc="#bfe4e6", ec="#1f7f86"))
bx.add_patch(R((0, 2.0), L, 0.15, fc="#4a90d9"))
bx.add_patch(R((-10, 2), 10, 14, fc="#3d4652"))
for px in pt.PIN_X:
    x = px + L / 2
    bx.add_patch(R((x - 2, 1.0), 4, T + 1.15, fc="#d33", ec="k", lw=0.5))
bx.text(L / 2, 7, "epoxy blank 10 (measure)", ha="center", fontsize=8)
bx.text(L / 2, 0.6, "spoil board 2 mm", ha="center", fontsize=7.5)
bx.text(L / 2, -3.5, "aluminium bed", ha="center", fontsize=7.5)
bx.text(-5, 9, "bracket", color="w", fontsize=7, ha="center", rotation=90, va="center")
x = pt.PIN_X[1] + L / 2
bx.annotate("pin hole: through the blank + 1 mm into the spoil board\n(1 mm of MDF left above the aluminium)",
            (x + 2, 1.5), (x + 12, -4.5), fontsize=7.5, arrowprops=dict(arrowstyle="->"))
bx.annotate("tape + CA", (40, 2.07), (50, 13.5), fontsize=7.5, color="#2a5d99", arrowprops=dict(arrowstyle="->", color="#2a5d99"))
bx.set_xlim(-15, L + 50); bx.set_ylim(-7, 15); bx.set_aspect(2.0); bx.axis("off")
bx.set_title("Side cut through the pins (height x2)", fontsize=10)
fig.savefig(os.path.join(HERE, "pintest_setup.png"), bbox_inches="tight")
print("art/pintest_setup.png")
