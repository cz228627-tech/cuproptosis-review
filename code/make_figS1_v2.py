# -*- coding: utf-8 -*-
"""Supplementary Figure S1 v2: tighter layout, larger type, no empty band."""

import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

GDSC = r"C:\work\depmap\GDSC2_fitted_dose_response.xlsx"
OUT = r"C:\work\figures"

df = pd.read_excel(GDSC)
e = df[df.DRUG_NAME == "Elesclomol"].copy()
cols = ["CELL_LINE_NAME", "MIN_CONC", "MAX_CONC", "LN_IC50", "AUC"]
sub = e[cols].head(14).copy()
sub["LN_IC50"] = sub["LN_IC50"].round(3)
sub["AUC"] = sub["AUC"].round(3)

MINC, MAXC = e["MIN_CONC"].iloc[0], e["MAX_CONC"].iloc[0]
n = len(e)
nmax = int((e["MAX_CONC"] == MAXC).sum())
beyond = int((e["LN_IC50"] > math.log(MAXC)).sum())

fig = plt.figure(figsize=(10.6, 6.0))
ax = fig.add_axes([0.04, 0.30, 0.92, 0.56])
ax.axis("off")

tbl = ax.table(cellText=sub.astype(str).values, colLabels=cols, loc="center",
               cellLoc="center", colLoc="center", bbox=[0, 0, 1, 1])
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
for j in range(len(cols)):
    c = tbl[0, j]
    c.set_facecolor("#1F3864")
    c.set_text_props(color="white", fontweight="bold")
    c.set_height(0.10)
for i in range(1, len(sub) + 1):
    for j in range(len(cols)):
        tbl[i, j].set_height(0.064)
        if i % 2 == 0:
            tbl[i, j].set_facecolor("#F2F3F4")

fig.text(0.04, 0.955, "Supplementary Figure S1", fontsize=12, fontweight="bold")
fig.text(0.04, 0.915,
         "GDSC2 fitted dose\u2013response: the fields behind the dose-range statement",
         fontsize=10, color="#333333")

fig.text(0.04, 0.22, f"Rows for elesclomol: {n}", fontsize=9.6, fontweight="bold")
fig.text(0.04, 0.175,
         f"MIN_CONC = {MINC}   and   MAX_CONC = {MAXC}   (identical across {nmax}/{n} rows)",
         fontsize=9.6)
fig.text(0.04, 0.125,
         f"LN_IC50 above ln({MAXC}) = {beyond}/{n}  ({100 * beyond / n:.1f}%) \u2014 these IC50 values lie beyond "
         f"the highest concentration screened",
         fontsize=9.4, color="#922B21")
fig.text(0.04, 0.035,
         "Source: GDSC2_fitted_dose_response.xlsx (GDSC2 release 8.5), DRUG_NAME = Elesclomol. "
         "Columns shown are those supplied by the resource; no values were transformed.",
         fontsize=7.6, color="#666666")

fig.savefig(os.path.join(OUT, "FigS1_GDSC2_fields.png"), dpi=300)
print(f"saved; rows {n}; beyond {beyond}")
