# -*- coding: utf-8 -*-
"""Figure 2 v2: ln axis label, dose-range markers, and an explicit note on the extrapolated tail."""

import math
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GDSC = r"C:\work\depmap\GDSC2_fitted_dose_response.xlsx"
OUT = r"C:\work\figures"

df = pd.read_excel(GDSC)
e = df[df.DRUG_NAME == "Elesclomol"].copy()
MINC, MAXC = e["MIN_CONC"].iloc[0], e["MAX_CONC"].iloc[0]
ln_max, ln_min = math.log(MAXC), math.log(MINC)
in_range = int((e["LN_IC50"] <= ln_max).sum())
pct = 100 * in_range / len(e)
top_ic50 = math.exp(e["LN_IC50"].max())
print(f"range {MINC}-{MAXC} uM; in range {in_range}/{len(e)} ({pct:.1f}%); max extrapolated IC50 {top_ic50:.1f} uM")

fig = plt.figure(figsize=(12.6, 4.9))
gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.30)

# ---- a
ax = fig.add_subplot(gs[0, 0])
ax.hist(e["LN_IC50"], bins=26, color="#95A5A6", edgecolor="white")
ax.axvspan(ln_max, e["LN_IC50"].max() + 0.3, color="#F5B7B1", alpha=0.35)
ax.axvline(ln_max, color="#C0392B", linewidth=1.6, linestyle="--")
ax.axvline(ln_min, color="#7F8C8D", linewidth=1.1, linestyle=":")
ax.set_xlabel("ln IC50 (µM)", fontsize=9)
ax.set_ylabel("Cell lines", fontsize=9)
ax.set_title("a  Elesclomol in 225 cancer cell lines (GDSC2)", fontsize=10, loc="left")
ymax = ax.get_ylim()[1]
ax.text(ln_max - 0.25, ymax * 1.02, f"top dose {MAXC} µM", fontsize=7, color="#922B21", ha="right")
ax.text(ln_min + 0.1, ymax * 0.80, f"lowest dose\n{MINC} µM", fontsize=6.6, color="#566573")
ax.text(ln_max + 0.15, ymax * 0.60,
        f"{100 - pct:.0f}% of lines ({len(e) - in_range}/225)\nfitted beyond the top dose",
        fontsize=7.4, color="#922B21")
ax.annotate(f"fitted IC50 up to {top_ic50:.0f} µM,\n~{top_ic50 / MAXC:.0f}\u00d7 the top dose",
            xy=(e["LN_IC50"].max(), 1.5), xytext=(e["LN_IC50"].max() - 2.4, ymax * 0.30),
            fontsize=6.6, color="#7B241C",
            arrowprops=dict(arrowstyle="->", color="#7B241C", lw=0.7))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# ---- b
ax = fig.add_subplot(gs[0, 1])
STAGES = [
    ("primary anticancer studies\n(excluding reviews, errata,\nnon-cancer records)", 287, "#2C3E50"),
    ("\u2026mention a non-malignant\ncell type", 11, "#5D6D7E"),
    ("\u2026use it as a cytotoxicity\ncomparator for a tumour line", 1, "#C0392B"),
    ("\u2026report a paired\nnormal-vs-tumour IC50", 0, "#7B241C"),
]
ax.set_xlim(0, 10); ax.set_ylim(-0.2, len(STAGES) + 0.45); ax.axis("off")
X0, MAXW = 2.5, 3.4
for i, (lab, n, col) in enumerate(STAGES):
    y = len(STAGES) - i - 0.5
    w = max(MAXW * math.sqrt(n / 287.0), 0.10)
    ax.barh(y, w, left=X0, height=0.5, color=col, edgecolor="none", alpha=0.92)
    ax.text(X0 - 0.15, y, str(n), ha="right", va="center", fontsize=13, fontweight="bold", color=col)
    ax.text(X0 + MAXW + 0.3, y, lab, ha="left", va="center", fontsize=8.2, color="#333333")
    if i < len(STAGES) - 1:
        ax.annotate("", xy=(X0 + 0.2, y - 0.40), xytext=(X0 + 0.2, y - 0.29),
                    arrowprops=dict(arrowstyle="-|>", color="#AAAAAA", lw=1.0))
ax.text(X0 + MAXW / 2, len(STAGES) + 0.12, "287 \u2192 11 \u2192 1 \u2192 0",
        ha="center", fontsize=11, color="#1F3864", fontweight="bold")
ax.set_title("b  Preclinical selectivity blind spot", fontsize=10, loc="left")

fig.text(0.01, 0.01,
         "a: GDSC2 fitted dose\u2013response. Screening range 0.0002\u20130.2 \u00b5M with no additional copper; "
         f"{len(e) - in_range} of 225 IC50 values lie above the top dose and are extrapolated by the fitted model, "
         f"the highest to {top_ic50:.0f} \u00b5M. "
         "b: PubMed, 17 November 2026; the 11 records were classified from abstracts and, where available, full texts.",
         fontsize=6.8, color="#666666")
fig.tight_layout(rect=[0, 0.03, 1, 1])
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"Fig2_pharmacology.{ext}"), dpi=300, bbox_inches="tight")
print("saved Fig2_pharmacology")
