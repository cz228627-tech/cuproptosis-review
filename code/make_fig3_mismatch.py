# -*- coding: utf-8 -*-
"""Figure 3: glioblastoma — four independent mismatches with the requirements of cuproptosis."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = r"C:\work\figures"
os.makedirs(OUT, exist_ok=True)

NAVY, RED, GREY, GREEN = "#1F3864", "#C0392B", "#7F8C8D", "#1E6B3A"

ROWS = [
    ("Requires respiratory flux\n(cuproptosis is OXPHOS-dependent)",
     "Among the most hypoxic solid tumours;\nHIF \u2192 PDK1 suppresses PDH, shifting to glycolysis"),
    ("Requires target cells that\ncan actually be killed",
     "Stem cells are reported to resist:\ncircadian copper control; DLD lactylation"),
    ("Requires a margin over\nthe dose-limiting tissue",
     "The brain is both the target organ\nand the tissue at risk"),
    ("Requires sensitivity that\npersists to treatment",
     "Resistance is acquired by recurrence,\nwhen systemic therapy is actually given"),
]

fig, ax = plt.subplots(figsize=(11.6, 6.0))
ax.set_xlim(0, 11.6)
ax.set_ylim(0, 6.0)
ax.axis("off")


def box(x, y, w, h, text, edge, fill, fs=8.4, bold=False, tc="#1a1a1a"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor=fill, edgecolor=edge, linewidth=1.15, alpha=0.10))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="none", edgecolor=edge, linewidth=1.15))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.35)


ax.text(0.25, 5.68, "A", fontsize=12, fontweight="bold", color=NAVY)
ax.text(0.62, 5.68, "what cuproptosis requires", fontsize=10, color=NAVY, fontweight="bold")
ax.text(5.05, 5.68, "B", fontsize=12, fontweight="bold", color=RED)
ax.text(5.42, 5.68, "what glioblastoma provides", fontsize=10, color=RED, fontweight="bold")

ys = [4.35, 3.15, 1.95, 0.75]
h = 0.95
for i, ((req, gbm), y) in enumerate(zip(ROWS, ys), 1):
    box(0.25, y, 4.25, h, f"{i}.  {req}", GREY, "white", fs=8.3)
    ax.text(4.85, y + h / 2, "\u2260", fontsize=20, color=RED, ha="center", va="center")
    box(5.55, y, 5.80, h, gbm, RED, "white", fs=8.3, tc="#7B241C")

# side arrow showing accumulation
ax.annotate("", xy=(11.42, 0.75), xytext=(11.42, 5.30),
            arrowprops=dict(arrowstyle="-|>", color="#D5D8DC", lw=3))

# bottom audit strip
ax.add_patch(FancyBboxPatch((0.25, 0.02), 11.10, 0.50,
                            boxstyle="round,pad=0.01,rounding_size=0.05",
                            facecolor="#F4F6F7", edgecolor="#D5D8DC", linewidth=0.9))
ax.text(0.25, 0.64, "What the glioma literature has tested", fontsize=8.4,
        color="#333333", fontweight="bold")
ax.text(5.80, 0.27,
        "115 primary studies   \u2192   4 mention neurons/astrocytes   \u2192   "
        "1 tests parenchymal toxicity   \u2192   0 selectivity ratios",
        fontsize=8.0, color="#7B241C", va="center", ha="center")

fig.text(0.012, 0.005,
         "Each mismatch is independent: correcting one does not remove the others. Panel B summarises published findings; "
         "the audit counts are from Box 1.",
         fontsize=6.8, color="#777777")

fig.tight_layout(rect=[0, 0.02, 1, 1])
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"Fig3_GBM_mismatches.{ext}"), dpi=300, bbox_inches="tight")
print("saved")
