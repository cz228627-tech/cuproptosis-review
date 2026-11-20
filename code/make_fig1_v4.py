# -*- coding: utf-8 -*-
"""Figure 1 v4: panel a shows all 21 cancer types with the excluded ones shaded and the six
outlying cells boxed; panels b-d use the 240-pair primary set."""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Rectangle
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
print(f"all {len(raw)} pairs / {raw.disease.nunique()} types; primary {len(prim)} / {prim.disease.nunique()}")

CATEGORY = {
    "MT1X": "buffer", "MT2A": "buffer", "SLC31A1": "import", "ATP7A": "export", "ATP7B": "export",
    "FDX1": "machinery", "LIAS": "machinery", "LIPT1": "machinery", "DLAT": "machinery",
    "DLD": "machinery", "PDHA1": "machinery", "PDHB": "machinery",
    "GPX4": "reference", "SLC7A11": "reference", "CD274": "reference",
}
CMAP_CAT = {"buffer": "#C0392B", "import": "#E67E22", "export": "#8E44AD",
            "machinery": "#2C3E50", "reference": "#95A5A6"}

fig = plt.figure(figsize=(13.6, 13.0))
gs = gridspec.GridSpec(3, 2, height_ratios=[1.6, 1.25, 1.25], hspace=0.62, wspace=0.30,
                       left=0.07, right=0.97, top=0.945, bottom=0.085)

# ---------------- (a) all 21 cancer types
ax = fig.add_subplot(gs[0, :])
mat = raw.pivot(index="gene", columns="disease", values="selectivity_index")
order_rows = mat.median(axis=1).sort_values().index
order_cols = mat.median(axis=0).sort_values(ascending=False).index
mat = mat.loc[order_rows, order_cols]
minn = raw.groupby("disease")["n_normal"].min().reindex(mat.columns)
excluded = [c for c in mat.columns if minn[c] < MIN_N]

im = ax.imshow(mat.values, aspect="auto", cmap="RdBu",
               norm=TwoSlopeNorm(vmin=0.0, vcenter=1.0, vmax=3.0))
ax.set_xticks(range(mat.shape[1]))
ax.set_xticklabels([c + ("" if minn[c] >= MIN_N else "\u2020") for c in mat.columns],
                   rotation=45, ha="right", fontsize=7.0)
ax.set_yticks(range(mat.shape[0]))
ax.set_yticklabels(mat.index, fontsize=7.5)
ax.set_xticks(np.arange(-.5, mat.shape[1], 1), minor=True)
ax.set_yticks(np.arange(-.5, mat.shape[0], 1), minor=True)
ax.grid(which="minor", color="white", linewidth=0.5)
ax.tick_params(which="minor", length=0)

# shade the excluded columns
for j, c in enumerate(mat.columns):
    if minn[c] < MIN_N:
        ax.add_patch(Rectangle((j - .5, -.5), 1, mat.shape[0], facecolor="#D9D9D9", alpha=0.38,
                               edgecolor="none", zorder=0))
# box the six cells that exceed S = 1
nbox = 0
for j, c in enumerate(mat.columns):
    for i, g in enumerate(mat.index):
        v = mat.values[i, j]
        if np.isfinite(v) and v > 1:
            ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False, edgecolor="black", linewidth=1.8,
                                   zorder=5))
            nbox += 1
print("boxed cells:", nbox)

cbar = fig.colorbar(im, ax=ax, fraction=0.016, pad=0.008)
cbar.set_label("S", fontsize=7.5, labelpad=4)
cbar.ax.tick_params(labelsize=7)
cbar.ax.axhline(1.0, color="black", linewidth=1)
ax.set_title("a   Selectivity index by gene and cancer type (315 pairs, 21 cancer types). "
             "Shaded types (\u2020) have fewer than 10 normal samples and are excluded from b\u2013d; "
             "the six boxed cells exceed S = 1 and all lie in shaded types",
             fontsize=8.6, loc="left", pad=6)

# ---------------- (b) primary set only
ax = fig.add_subplot(gs[1, 0])
sig = prim["sig_enriched"].astype(bool)
ax.axhline(1.0, color="#333333", linewidth=0.9, linestyle="--")
ax.axvline(0.5, color="#333333", linewidth=0.9, linestyle="--")
ax.scatter(prim.loc[~sig, "auc"], prim.loc[~sig, "selectivity_index"], s=9, c="#BDBDBD",
           label=f"not significant (n={int((~sig).sum())})", zorder=2)
ax.scatter(prim.loc[sig, "auc"], prim.loc[sig, "selectivity_index"], s=11, c="#2C3E50",
           label=f"enriched, not separable (n={int(sig.sum())})", zorder=3)
ax.set_xlabel("AUC", fontsize=8)
ax.set_ylabel("S", fontsize=8)
ax.set_xlim(0, 1.03)
ax.set_ylim(0, 1.06)
ax.tick_params(labelsize=7)
ax.legend(frameon=False, fontsize=6, loc="upper left")
ax.annotate("no pair reaches S = 1", xy=(0.85, 0.99), xytext=(0.60, 0.66),
            fontsize=6.4, color="#C0392B",
            arrowprops=dict(arrowstyle="->", color="#C0392B", lw=0.7))
ax.text(0.02, 0.62, "the six excluded pairs\nreaching S > 1 are in a", fontsize=6, color="#666666")
ax.set_title("b   Enrichment is not separation (240 primary pairs)", fontsize=9, loc="left", pad=6)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)

# ---------------- (c)
ax = fig.add_subplot(gs[1, 1])
p = prog.sort_values("programme_auc")
ax.barh(range(len(p)), p["programme_auc"],
        color=["#C0392B" if v < 0.5 else "#2C3E50" for v in p["programme_auc"]])
ax.axvline(0.5, color="#333333", linewidth=0.9, linestyle="--")
ax.set_yticks(range(len(p)))
ax.set_yticklabels([d[:32] for d in p["disease"]], fontsize=6.4)
ax.set_xlabel("Programme AUC (12 copper genes)", fontsize=8)
ax.set_xlim(0, 0.85)
ax.tick_params(labelsize=7)
ax.text(0.51, len(p) - 0.4, "label-permutation null: 0.50", fontsize=6, color="#666666")
ax.set_title("c   Coordinated programme, 16 types with n$_{normal}$ \u2265 10", fontsize=9, loc="left", pad=6)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)

# ---------------- (d)
ax = fig.add_subplot(gs[2, :])
ratio = main.groupby("gene")["median_ratio"].median().sort_values()
ax.bar(range(len(ratio)), ratio.values,
       color=[CMAP_CAT.get(CATEGORY.get(g, "reference"), "#2C3E50") for g in ratio.index])
ax.axhline(1.0, color="#333333", linewidth=0.9, linestyle="--")
ax.set_xticks(range(len(ratio)))
ax.set_xticklabels(ratio.index, rotation=30, ha="right", fontsize=7.5)
ax.set_ylabel("median tumour / normal", fontsize=8)
ax.set_ylim(0, max(4.0, ratio.max() * 1.12))
ax.tick_params(labelsize=7)
for i, (g, v) in enumerate(ratio.items()):
    ax.text(i, v + 0.06, f"{v:.2f}", ha="center", fontsize=6.4, color="#333333")
ax.set_title("d   Tumour-to-normal ratio by gene: the metallothioneins are the lowest, "
             "SLC7A11 the outlier", fontsize=9, loc="left", pad=6)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)

handles = [plt.Rectangle((0, 0), 1, 1, color=CMAP_CAT[k]) for k in
           ("buffer", "machinery", "import", "export", "reference")]
ax.legend(handles, ["metal buffering", "cuproptosis machinery", "copper import",
                    "copper export", "reference genes"],
          frameon=False, fontsize=6.6, ncol=5, loc="upper left")

fig.suptitle("Copper-homeostasis genes are not enriched in tumours at the transcript level",
             fontsize=11.5, y=0.975)
fig.text(0.01, 0.012,
         f"TCGA primary tumours vs TCGA adjacent normal, TOIL RSEM, linear TPM. Panel a: all 315 gene\u2013cancer "
         f"pairs; types marked \u2020 (cholangiocarcinoma, glioblastoma, cervical) have 3\u20139 normal samples and are "
         f"excluded from b\u2013d, leaving {len(prim)} pairs in {prim.disease.nunique()} types. S = P5(tumour)/P95"
         f"(normal); S > 1 requires the two distributions not to overlap. Panel d: median of per-gene medians. "
         "Label-permutation null for the programme score: median 0.50 (95% 0.47\u20130.53), 0 of 500 permutations "
         "reached the observed 0.33 (P < 0.002). Descriptive only; see section 5 for limitations.",
         fontsize=6.5, color="#666666")

fig.savefig(os.path.join(OUT, "Fig1_transcript_comparison.png"), dpi=300, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Fig1_transcript_comparison.pdf"), bbox_inches="tight")
print("saved")
