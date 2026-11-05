"""Side cut through the coaster's edge: the 2D Chamfer with the 3.175 mm 90 deg bit, tip offset 0.2 vs 0.5."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as P, Rectangle as R

D, H = 3.175, 3.175 / 2          # bit diameter, height of the V (90 deg)
CH = 1.2                         # chamfer


def panel(ax, off, title, good):
    zt = -(CH + off); xt = -CH - zt          # tip: the left flank passes through the chamfer's bottom (0, -CH)
    ax.add_patch(R((-6, -4), 6, 4, fc="#d9c3a0", ec="none"))                 # coaster
    ax.add_patch(R((0, -4), 4, 4, fc="#efe6d6", ec="none", hatch="//", alpha=0.6))   # scrap
    # material removed by the bit: the cone, and the shank below the surface if any
    zc = zt + H                                                             # top of the V
    cut = [(xt, zt), (xt - min(H, -zt), zt + min(H, -zt)), (xt + min(H, -zt), zt + min(H, -zt))]
    if zc < 0:
        cut = [(xt, zt), (xt - H, zc), (xt - H, 0), (xt + H, 0), (xt + H, zc)]
    ax.add_patch(P(cut, fc="white", ec="none"))
    # the bit
    ax.add_patch(P([(xt, zt), (xt - H, zc), (xt - H, 4.5), (xt + H, 4.5), (xt + H, zc)], fc="#9aa3ad", ec="#333", lw=1.2, alpha=0.85))
    ax.plot([0, 0], [-4, 1.2], color="#e68a00", lw=2, ls="--")
    ax.text(0.08, 1.3, "orange line\n(coaster edge)", color="#c06a00", fontsize=10, va="bottom")
    ax.text(-3.0, -2.8, "COASTER", fontsize=13, weight="bold", color="#6b4a20", ha="center")
    ax.text(3.0, -3.45, "scrap (cut away later)", fontsize=10, color="#777", ha="center")
    ax.plot(xt, zt, "o", color="#c33", ms=7)
    ax.annotate(f"tip {CH + off:.1f} deep", (xt, zt), (xt + 0.9, zt - 0.6), fontsize=11, color="#c33",
                arrowprops=dict(arrowstyle="->", color="#c33"))
    ax.annotate("", (-0.05, zt), (-0.05, -CH), arrowprops=dict(arrowstyle="<->", color="#333"))
    ax.text(-0.15, (zt - CH) / 2, f"offset {off}", fontsize=10, ha="right", va="center")
    if good:
        ax.plot([-CH, 0], [0, -CH], color="#1a8f3a", lw=4)
        ax.text(-1.25, -0.55, "clean bevel 1.2", color="#1a8f3a", fontsize=12, weight="bold", ha="right")
        ax.text(xt + H + 0.1, zc + 0.2, "V fits\n(bit is 1.6 tall)", fontsize=10, color="#1a8f3a")
    else:
        ax.plot([xt - H, xt - H], [zc, 0], color="#d00", lw=4)
        ax.text(xt - H - 0.15, zc / 2 - 0.6, "shank rubs:\nstep in the edge", color="#d00", fontsize=11, weight="bold", ha="right")
    ax.set_title(title, fontsize=14, color="#1a8f3a" if good else "#d00", weight="bold")
    ax.set_xlim(-5, 4); ax.set_ylim(-3.6, 4.5); ax.set_aspect("equal"); ax.axis("off")
    ax.axhline(0, xmin=0, xmax=1, color="#444", lw=0.8)
    ax.text(-4.9, 0.1, "top", fontsize=9, color="#444")


fig, axs = plt.subplots(1, 2, figsize=(13, 6.2), dpi=130)
panel(axs[0], 0.2, "Tip offset 0.2  ✓", True)
panel(axs[1], 0.5, "Tip offset 0.5  ✗", False)
fig.suptitle("2D Chamfer 1.2 with the 3.175 mm 90° bit (side cut through the edge)", fontsize=13)
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "chamfer_offset.png"), bbox_inches="tight")
