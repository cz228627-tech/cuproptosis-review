# -*- coding: utf-8 -*-
"""Figure 3: conceptual framework — from unstratified copper loading to a testable strategy."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = r"C:\work\figures"
os.makedirs(OUT, exist_ok=True)

NAVY = "#1F3864"
RED = "#C0392B"
GREY = "#7F8C8D"
GREEN = "#1E6B3A"

fig, ax = plt.subplots(figsize=(11.2, 5.6))
ax.set_xlim(0, 11.2)
ax.set_ylim(0, 5.6)
ax.axis("off")


def box(x, y, w, h, text, fc, ec, fs=8.6, tc="#1a1a1a", bold=False, alpha=0.10):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=fc, edgecolor=ec, linewidth=1.1, alpha=alpha))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="none", edgecolor=ec, linewidth=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.35)


def arrow(x1, y1, x2, y2, color="#555555", style="-|>", lw=1.3, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=13, color=color, linewidth=lw,
                                 linestyle=ls, shrinkA=2, shrinkB=2))


# ---------------- left: current paradigm
ax.text(0.15, 5.30, "A  Current paradigm: unstratified copper loading",
        fontsize=10.5, color=GREY, fontweight="bold")

box(0.15, 4.05, 2.55, 0.85, "Copper ionophore\n+ copper, unselected", "white", GREY, bold=True)

box(0.15, 2.55, 2.55, 0.85, "Systemic exposure\n(plasma CuET measurable)", "white", GREY, fs=8.2)
box(0.15, 1.05, 2.55, 0.85, "Tumour compartment:\nexposure not shown (n = 3)", "white", RED, fs=7.8)

box(3.05, 2.55, 1.85, 0.85, "Liver\nneuro-\ntoxicity", "white", RED, fs=8.2)
box(3.05, 1.05, 1.85, 0.85, "No selective\ntumour effect", "white", RED, fs=8.2)

arrow(1.42, 4.02, 1.42, 3.45, GREY)
arrow(1.42, 2.52, 1.42, 1.95, RED)
arrow(2.72, 2.97, 3.02, 2.97, RED)
arrow(2.72, 1.47, 3.02, 1.47, RED)

box(0.15, 0.20, 4.75, 0.60, "Therapeutic window: never demonstrated", "white", RED, fs=10, tc=RED, bold=True, alpha=0.06)

# ---------------- divider
ax.plot([5.25, 5.25], [0.15, 5.15], color="#DDDDDD", linewidth=1.2, linestyle="--")

# ---------------- right: proposed strategy
ax.text(5.55, 5.30, "B  Proposed framework: create the window, then test it",
        fontsize=10.5, color=GREEN, fontweight="bold")

box(5.55, 3.95, 2.35, 0.95, "1  Metabolic priming\n(force OXPHOS;\nreverse the Warburg shift)", "white", GREEN, fs=8.2, bold=False)
box(5.55, 2.55, 2.35, 0.95, "2  Stratify\n(low LDH / high OXPHOS /\nhigh FDX1, low MT buffer)", "white", GREEN, fs=8.2)
box(5.55, 1.15, 2.35, 0.95, "3  Then load copper\n(sequence matters)", "white", GREEN, fs=8.2)

box(8.30, 2.55, 2.65, 0.95, "Selective vulnerability\n(proposed, untested)", "white", GREEN, fs=9, tc=GREEN, bold=True, alpha=0.12)
box(8.30, 1.15, 2.65, 0.95, "Falsifiable readouts\nOCR/ECAR ratio; LDH;\nlipoylated DLAT; MT1/2", "white", "#333333", fs=7.8)

arrow(6.72, 3.92, 6.72, 3.53, GREEN)
arrow(6.72, 2.52, 6.72, 2.13, GREEN)
arrow(7.92, 1.62, 8.27, 1.62, "#333333")
arrow(8.05, 3.02, 8.27, 3.02, GREEN)

ax.text(5.55, 0.62, "Labelled as Proposed Framework — not validated. "
                    "Any of the three steps failing in vitro should falsify the strategy.",
        fontsize=7.6, color="#555555")

fig.text(0.01, 0.005,
         "Panel A summarises human and preclinical evidence reviewed here; panel B is a hypothesis with explicit falsification criteria.",
         fontsize=6.8, color="#777777")

fig.tight_layout(rect=[0, 0.01, 1, 1])
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"Fig4_framework.{ext}"), dpi=300, bbox_inches="tight")
print("saved")
