# -*- coding: utf-8 -*-
"""Supplementary Table S1 (v2): add the estimator-bias check — how close P95 sits to the sample maximum."""

import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE = r"C:\work\xena"
rng = np.random.default_rng(20261120)

mat = pd.read_csv(BASE + r"\target_genes_tpm.tsv", sep="\t")
ids = mat["sample"].tolist()
X = mat.drop(columns=["sample"]).values.astype(float)
samples = list(mat.columns[1:])
pm = pd.read_csv(BASE + r"\probemap.tsv", sep="\t", dtype=str)
mp = dict(zip(pm["id"].str.split(".").str[0], pm["gene"]))
symbols = [mp.get(i.split(".")[0], i) for i in ids]
gidx = {g: i for i, g in enumerate(symbols)}

ph = pd.read_csv(BASE + r"\phenotype.tsv", sep="\t", dtype=str, low_memory=False)
ph = ph[["sample", "_sample_type", "primary disease or tissue", "_study"]]
ph.columns = ["sample", "type", "disease", "study"]
tl = ph["type"].str.lower()
ph["tum"] = tl.str.contains("tumor") & ~tl.str.contains("normal")
ph["nor"] = tl.str.contains("normal")
ph = ph[ph.study.str.upper() == "TCGA"]

lin = lambda v: np.clip(np.power(2.0, v) - 0.001, 0, None)
pos = {s: i for i, s in enumerate(samples)}

PAIRS = [("Cholangiocarcinoma", "SLC7A11"), ("Cholangiocarcinoma", "ATP7A"),
         ("Cholangiocarcinoma", "LIPT1"), ("Glioblastoma Multiforme", "SLC31A1"),
         ("Glioblastoma Multiforme", "FDX1"), ("Cervical & Endocervical Cancer", "PDHA1")]

rows = []
for disease, gene in PAIRS:
    g = ph[ph.disease == disease]
    t = lin(X[gidx[gene]][[pos[s] for s in g.loc[g.tum, "sample"] if s in pos]])
    n = lin(X[gidx[gene]][[pos[s] for s in g.loc[g.nor, "sample"] if s in pos]])
    p5t, p95n, mx = np.percentile(t, 5), np.percentile(n, 95), n.max()
    boots = [p5t / np.percentile(rng.choice(n, len(n), replace=True), 95) for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    rows.append({"cancer": disease.replace(" Multiforme", "").replace(" & Endocervical", ""),
                 "gene": gene, "n_normal": len(n), "P95": round(p95n, 2), "max": round(mx, 2),
                 "P95/max": round(p95n / mx, 2), "S": round(p5t / p95n, 2),
                 "CI": f"{lo:.2f}\u2013{hi:.2f}"})

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv(BASE + r"\supp_table_S1_six_pairs.csv", index=False)

doc = Document()
h = doc.add_heading("Supplementary Table S1. The six gene\u2013cancer pairs that exceed S = 1 in the unfiltered matrix", level=2)
doc.add_paragraph(
    "All six pairs lie in cancer types with fewer than ten adjacent normal samples and are therefore excluded from "
    "the primary analysis. The bootstrap interval resamples the normal samples within the same small set and so "
    "captures sampling variation but not the bias that matters here: with 3\u20139 normals, the 95th percentile is "
    "estimated from the top one or two observations (P95/max close to 1), so it understates the population P95 and "
    "inflates S. The ratio is stable; the denominator is not estimable at this sample size.")

t = doc.add_table(rows=1, cols=7)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = ["Cancer type", "Gene", "n normal", "P95(normal), TPM", "Sample maximum", "P95 / max",
       "S (bootstrap 95% CI)"]
for i, x in enumerate(hdr):
    c = t.rows[0].cells[i]
    c.text = ""
    r = c.paragraphs[0].add_run(x)
    r.bold = True
    r.font.size = Pt(8)
for _, row in df.iterrows():
    cells = t.add_row().cells
    vals = [row["cancer"], row["gene"], str(row["n_normal"]), f"{row['P95']:.2f}", f"{row['max']:.2f}",
            f"{row['P95/max']:.2f}", f"{row['S']:.2f} ({row['CI']})"]
    for c, v in zip(cells, vals):
        c.text = ""
        r = c.paragraphs[0].add_run(v)
        r.font.size = Pt(8)

doc.add_paragraph(
    "Reading the table: every interval lies above 1, so the six ratios are not noise. What is in doubt is whether "
    "the population P95 is as low as the sample maximum suggests. With n = 3 a single low normal would move P95 and "
    "S would fall below 1; the bootstrap cannot show this because it resamples the same three values.")
doc.save(r"C:\work\cuproptosis_review\05_documents\Supplementary_Table_S1.docx")
print("\nsaved Supplementary_Table_S1.docx")
