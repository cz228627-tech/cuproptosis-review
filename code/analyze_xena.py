# -*- coding: utf-8 -*-
"""Compute tumour-vs-normal separation for copper-homeostasis genes from the Xena TOIL matrix."""

import gzip
import os
import numpy as np
import pandas as pd

BASE = r"C:\work\xena"
EXPR = os.path.join(BASE, "target_genes_tpm.tsv")
PHENO = os.path.join(BASE, "phenotype.tsv")
OUT_CSV = os.path.join(BASE, "selectivity_index.csv")
OUT_XLSX = os.path.join(BASE, "selectivity_index.xlsx")

print("reading phenotype ...", flush=True)
ph = pd.read_csv(PHENO, sep="\t", dtype=str, low_memory=False)
cols = {c.lower(): c for c in ph.columns}


def pick(*names):
    for n in names:
        for lc, c in cols.items():
            if n in lc:
                return c
    return None


c_sample = pick("sample")
c_type = pick("sample_type")
c_dis = "primary disease or tissue" if "primary disease or tissue" in ph.columns else pick("disease", "tissue")
c_study = pick("study")
print("columns:", c_sample, "|", c_type, "|", c_dis, "|", c_study, flush=True)

ph = ph[[c_sample, c_type, c_dis, c_study]].copy()
ph.columns = ["sample", "type", "disease", "study"]

# normalise
ph["type"] = ph["type"].fillna("").str.lower()
ph["is_tumour"] = ph["type"].str.contains("tumor") & ~ph["type"].str.contains("normal")
ph["is_normal"] = ph["type"].str.contains("normal")
ph.loc[ph["study"].str.upper() == "GTEX", "is_normal"] = True

print("reading expression (transposed) ...", flush=True)
ex = pd.read_csv(EXPR, sep="\t", index_col=0)
ex.index = [i.split(".")[0] for i in ex.index]

# map ensembl -> symbol via probemap
pm = pd.read_csv(os.path.join(BASE, "probemap.tsv"), sep="\t")
pm["id"] = pm["id"].str.split(".").str[0]
sym = dict(zip(pm["id"], pm["gene"]))
ex.index = [sym.get(i, i) for i in ex.index]
ex = ex[~ex.index.duplicated()]

samples = list(ex.columns)
meta = ph.set_index("sample").reindex(samples)
print(f"samples in matrix: {len(samples)}, matched metadata: {meta['type'].notna().sum()}", flush=True)

rows = []
genes = list(ex.index)
for disease, grp in meta.groupby("disease"):
    if not isinstance(disease, str):
        continue
    tum = grp.index[(grp["is_tumour"] == True) & (grp["study"].str.upper() == "TCGA")]
    nor = grp.index[(grp["is_normal"] == True) & (grp["study"].str.upper() == "TCGA")]
    if len(tum) < 20 or len(nor) < 3:
        continue
    for g in genes:
        # TOIL stores log2(TPM + 0.001); back-transform to linear TPM before ratios
        t = np.power(2.0, ex.loc[g, tum].astype(float).values) - 0.001
        n = np.power(2.0, ex.loc[g, nor].astype(float).values) - 0.001
        t = np.clip(t, 0, None)
        n = np.clip(n, 0, None)
        p5t, medt = np.percentile(t, 5), np.median(t)
        p95n, medn = np.percentile(n, 95), np.median(n)
        rows.append({
            "disease": disease,
            "gene": g,
            "n_tumour": len(tum),
            "n_normal": len(nor),
            "median_tumour": round(medt, 3),
            "p5_tumour": round(p5t, 3),
            "median_normal": round(medn, 3),
            "p95_normal": round(p95n, 3),
            "selectivity_index": round(p5t / p95n, 3) if p95n > 0 else np.nan,
            "median_ratio": round(medt / medn, 3) if medn > 0 else np.nan,
        })

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"rows written: {len(df)} -> {OUT_CSV}", flush=True)

if len(df):
    print("\n=== overall ===")
    print(df["selectivity_index"].describe())
    print("\nfraction S<1:", round((df["selectivity_index"] < 1).mean(), 3))
    print("\n=== by gene (median S) ===")
    print(df.groupby("gene")["selectivity_index"].median().sort_values().to_string())
    print("\n=== top 10 highest S ===")
    print(df.nlargest(10, "selectivity_index")[["disease", "gene", "selectivity_index"]].to_string(index=False))

    # heatmap-ready matrix
    mat = df.pivot(index="gene", columns="disease", values="selectivity_index")
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="long", index=False)
        mat.to_excel(xw, sheet_name="matrix")
    from openpyxl import load_workbook
    from openpyxl.formatting.rule import ColorScaleRule
    wb = load_workbook(OUT_XLSX)
    ws = wb["matrix"]
    rng = f"B2:{chr(64+min(ws.max_column,26))}{ws.max_row}"
    ws.conditional_formatting.add(
        rng, ColorScaleRule(start_type="num", start_value=0.2, start_color="F8696B",
                            mid_type="num", mid_value=1, mid_color="FFEB84",
                            end_type="num", end_value=2.5, end_color="63BE7B"))
    wb.save(OUT_XLSX)
    print(f"\nxlsx -> {OUT_XLSX}")
