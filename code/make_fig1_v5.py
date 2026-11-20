# -*- coding: utf-8 -*-
"""Figure 2 (CTR) v5: cleaner layout — short in-figure titles, shading key inside panel a, less whitespace."""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Rectangle, Patch
import matplotlib.gridspec as gridspec

BASE = r"C:\work\xena"
OUT = r"C:\work\figures"
MIN_N = 10

raw = pd.read_csv(os.path.join(BASE, "selectivity_index_stats.csv"))
base = pd.read_csv(os.path.join(BASE, "selectivity_index.csv"))
prog = pd.read_csv(os.path.join(BASE, "per_cancer_programme.csv"))
main = pd.read_csv(os.path.join(BASE, "selectivity_main_n10.csv"))

med = base[["disease", "gene", "median_tumour", "median_normal"]]
raw = raw.merge(med, on=["disease", "gene"], how="left", suffixes=("", "_dup"))
if "median_tumour_dup" in raw.columns:
    raw["median_tumour"] = raw["median_tumour_dup"]
    raw["median_normal"] = raw["median_normal_dup"]
prim = raw[raw["n_normal"] >= MIN_N].copy()

CAT = {"MT1X": "buffer", "MT2A": "buffer", "SLC31A1": "import", "ATP7A": "export", "ATP7B": "export",
       "FDX1": "machinery", "LIAS": "machinery", "LIPT1": "machinery", "DLAT": "machinery",
       "DLD": "machinery", "PDHA1": "machinery", "PDHB": "machinery",
       "GPX4": "reference", "SLC7A11": "reference", "CD274": "reference"}
CC = {"buffer": "#C0392B", "import": "#E67E22", "export": "#8E44AD", "machinery": "#2C3E50",
      "reference": "#95A5A6"}

fig = plt.figure(figsize=(13.0, 12.2))
gs = gridspec.GridSpec(3, 2, height_ratios=[2.0, 1.30, 1.00], hspace=0.50, wspace=0.30,
                       left=0.075, right=0.975, top=0.965, bottom=0.075)

# ---------------- a
ax = fig.add_subplot(gs[0, :])
mat = raw.pivot(index="gene", columns="disease", values="selectivity_index")
order_r = mat.median(axis=1).sort_values().index
order_c = mat.median(axis=0).sort_values(ascending=False).index
mat = mat.loc[order_r, order_c]
minn = raw.groupby("disease")["n_normal"].min().reindex(mat.columns)

im = ax.imshow(mat.values, aspect="auto", cmap="RdBu",
               norm=TwoSlopeNorm(vmin=0.0, vcenter=1.0, vmax=3.0))
ax.set_xticks(range(mat.shape[1]))
ax.set_xticklabels(mat.columns, rotation=40, ha="right", fontsize=7.4)
ax.set_yticks(range(mat.shape[0]))
ax.set_yticklabels(mat.index, fontsize=8)
ax.set_xticks(np.arange(-.5, mat.shape[1], 1), minor=True)
ax.set_yticks(np.arange(-.5, mat.shape[0], 1), minor=True)
ax.grid(which="minor", color="white", linewidth=0.6)
ax.tick_params(which="minor", length=0)

for j, c in enumerate(mat.columns):
    if minn[c] < MIN_N:
        ax.add_patch(Rectangle((j - .5, -.5), 1, mat.shape[0], facecolor="#BFBFBF", alpha=0.42,
                               edgecolor="none", zorder=0))
for j, c in enumerate(mat.columns):
    for i, g in enumerate(mat.index):
        v = mat.values[i, j]
        if np.isfinite(v) and v > 1:
            ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False, edgecolor="black",
                                   linewidth=1.9, zorder=5))

cb = fig.colorbar(im, ax=ax, fraction=0.014, pad=0.006)
cb.set_label("S", fontsize=8, labelpad=6)
cb.ax.tick_params(labelsize=7)
cb.ax.axhline(1.0, color="black", linewidth=1)
ax.set_title("a   Selectivity index by gene and cancer type   (grey shading: n$_{normal}$ < 10, excluded;   black boxes: S > 1)", fontsize=9.2, loc="left", pad=7)

handles = [Patch(facecolor="#BFBFBF", alpha=0.42, edgecolor="none", label="n$_{normal}$ < 10 (excluded)"),
           Patch(facecolor="none", edgecolor="black", linewidth=1.9, label="S > 1")]


# ---------------- b
ax = fig.add_subplot(gs[1, 0])
sig = prim["sig_enriched"].astype(bool)
ax.axhline(1.0, color="#333333", linewidth=0.9, linestyle="--")
ax.axvline(0.5, color="#333333", linewidth=0.9, linestyle="--")
ax.scatter(prim.loc[~sig, "auc"], prim.loc[~sig, "selectivity_index"], s=10, c="#BDBDBD",
           label=f"not significant (n={int((~sig).sum())})", zorder=2)
ax.scatter(prim.loc[sig, "auc"], prim.loc[sig, "selectivity_index"], s=12, c="#2C3E50",
           label=f"enriched, not separable (n={int(sig.sum())})", zorder=3)
ax.set_xlabel("AUC", fontsize=8.5)
ax.set_ylabel("S", fontsize=8.5)
ax.set_xlim(0, 1.03)
ax.set_ylim(0, 1.06)
ax.tick_params(labelsize=7.5)
ax.text(0.02, 0.96, f"not significant (n={int((~sig).sum())})", fontsize=6.6, color="#666666", va="top")
ax.text(0.02, 0.88, f"enriched, not separable (n={int(sig.sum())})", fontsize=6.6, color="#2C3E50", va="top")
ax.annotate("no copper-gene pair reaches S = 1", xy=(0.82, 0.985), xytext=(0.05, 0.86),
            fontsize=6.8, color="#C0392B",
            arrowprops=dict(arrowstyle="->", color="#C0392B", lw=0.7))
ax.set_title("b   Enrichment is not separation", fontsize=9.5, loc="left", pad=8)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)

# ---------------- c
ax = fig.add_subplot(gs[1, 1])
p = prog.sort_values("programme_auc")
ax.barh(range(len(p)), p["programme_auc"],
        color=["#C0392B" if v < 0.5 else "#2C3E50" for v in p["programme_auc"]], height=0.72)
ax.axvline(0.5, color="#333333", linewidth=0.9, linestyle="--")
ax.set_yticks(range(len(p)))
ax.set_yticklabels([d[:24] for d in p["disease"]], fontsize=6.6)
ax.set_xlabel("Programme AUC (12 copper genes)", fontsize=8.5)
ax.set_xlim(0, 0.85)
ax.tick_params(labelsize=7.5)
ax.annotate("null median 0.50", xy=(0.5, 1.0), xytext=(0.55, 2.2),
            fontsize=6.4, color="#666666",
            arrowprops=dict(arrowstyle="->", color="#999999", lw=0.6))
ax.set_title("c   Programme score by cancer type", fontsize=9.5, loc="left", pad=8)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)

# ---------------- d
ax = fig.add_subplot(gs[2, :])
ratio = main.groupby("gene")["median_ratio"].median().sort_values()
ax.bar(range(len(ratio)), ratio.values,
       color=[CC.get(CAT.get(g, "reference"), "#2C3E50") for g in ratio.index], width=0.72)
ax.axhline(1.0, color="#333333", linewidth=0.9, linestyle="--")
ax.set_xticks(range(len(ratio)))
ax.set_xticklabels(ratio.index, rotation=30, ha="right", fontsize=8)
ax.set_ylabel("median tumour / normal", fontsize=8.5)
ax.set_ylim(0, 3.75)
ax.tick_params(labelsize=7.5)
for i, (g, v) in enumerate(ratio.items()):
    ax.text(i, v + 0.07, f"{v:.2f}", ha="center", fontsize=6.6, color="#333333")
ax.set_title("d   Tumour-to-normal ratio by gene", fontsize=9.5, loc="left", pad=7)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
handles = [Patch(facecolor=CC[k]) for k in ("buffer", "machinery", "import", "export", "reference")]
ax.legend(handles, ["metal buffering", "machinery", "import", "export", "reference"],
          frameon=False, fontsize=7, ncol=5, loc="upper left")

fig.savefig(os.path.join(OUT, "Fig1_transcript_comparison.png"), dpi=300, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Fig1_transcript_comparison.pdf"), bbox_inches="tight")
print("saved figure 2 (transcript)")
