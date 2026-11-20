# -*- coding: utf-8 -*-
"""GDSC elesclomol figure + cross-database overlap check against the TCGA programme AUC."""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GDSC = r"C:\work\depmap\GDSC2_fitted_dose_response.xlsx"
TCGA = r"C:\work\xena\per_cancer_programme.csv"
OUT = r"C:\work\figures"
os.makedirs(OUT, exist_ok=True)

df = pd.read_excel(GDSC)
e = df[df.DRUG_NAME == "Elesclomol"].copy()

# ---------------------------------------------------------------- Figure 4
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3),
                         gridspec_kw={"width_ratios": [1, 1.25]})

ax = axes[0]
ax.hist(e["AUC"], bins=28, color="#95A5A6", edgecolor="white")
ax.axvline(e["AUC"].median(), color="#C0392B", linewidth=1.6)
ax.axvline(0.7, color="#2C3E50", linewidth=1, linestyle="--")
ax.set_xlabel("AUC (dose–response area; higher = less killing)", fontsize=9)
ax.set_ylabel("Cell lines", fontsize=9)
ax.set_title("a  Elesclomol in 225 cancer cell lines", fontsize=10, loc="left")
ax.text(e["AUC"].median() + 0.01, ax.get_ylim()[1] * 0.9,
        f"median {e['AUC'].median():.2f}", color="#C0392B", fontsize=8)
ax.text(0.705, ax.get_ylim()[1] * 0.75, "AUC 0.7\n(21.8% below)", fontsize=7.5, color="#2C3E50")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

ax = axes[1]
g = (e.groupby("TCGA_DESC")["LN_IC50"]
     .agg(["count", "median"]).query("count >= 10").sort_values("median"))
labels = [f"{i} (n={int(r['count'])})" for i, r in g.iterrows()]
ax.barh(range(len(g)), g["median"], color="#2C3E50")
ax.set_yticks(range(len(g)))
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("Median LN(IC50)  —  lower = more sensitive", fontsize=9)
ax.set_title("b  Sensitivity by tissue", fontsize=10, loc="left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.suptitle("Elesclomol has limited in vitro activity: median AUC 0.85, only 1.8% of lines below 0.5",
             fontsize=10.5, y=1.03)
fig.text(0.01, 0.01, "GDSC2 fitted dose–response (release 8.5). AUC and LN(IC50) are model-fitted; "
                     "high values may reflect extrapolation beyond tested concentrations.",
         fontsize=7, color="#555555")
fig.tight_layout(rect=[0, 0.02, 1, 1])
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"Fig4_GDSC_elesclomol.{ext}"), dpi=300, bbox_inches="tight")
plt.close(fig)
print("Fig4 saved")

# ---------------------------------------------------------------- overlap check
tc = pd.read_csv(TCGA).set_index("disease")["programme_auc"]
NAME = {
    "Lung Adenocarcinoma": "LUAD",
    "Head & Neck Squamous Cell Carcinoma": "HNSC",
    "Kidney Clear Cell Carcinoma": "KIRC",
    "Stomach Adenocarcinoma": "STAD",
    "Skin Cutaneous Melanoma": "SKCM",
    "Bladder Urothelial Carcinoma": "BLCA",
    "Breast Invasive Carcinoma": "BRCA",
}
gdsc_t = e.groupby("TCGA_DESC")["LN_IC50"].agg(["count", "median"]).query("count >= 10")

pairs = []
for disease, auc in tc.items():
    code = NAME.get(disease)
    if code and code in gdsc_t.index:
        pairs.append((disease, code, auc, gdsc_t.loc[code, "median"], int(gdsc_t.loc[code, "count"])))

print("\n=== overlap between TCGA programme table and GDSC tissues (n>=10) ===")
for p in pairs:
    print(f"  {p[0]:45s} {p[1]:5s}  TCGA AUC={p[2]:.3f}   GDSC median LN(IC50)={p[3]:.2f}  (n={p[4]})")
print(f"  -> overlapping cancer types: {len(pairs)}")
if len(pairs) >= 3:
    x = np.array([p[3] for p in pairs])
    y = np.array([p[2] for p in pairs])
    print(f"  Pearson r = {np.corrcoef(x, y)[0,1]:.3f}  (n={len(pairs)})")
