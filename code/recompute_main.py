# -*- coding: utf-8 -*-
"""D1+D2+D3: restrict to well-powered cohorts, report median ratio and S side by side,
and separate copper genes from reference genes."""

import math
import os
import numpy as np
import pandas as pd

BASE = r"C:\work\xena"
MIN_N = 10

COPPER = ["SLC31A1", "ATP7A", "ATP7B", "MT1X", "MT2A",
          "FDX1", "LIAS", "LIPT1", "DLAT", "DLD", "PDHA1", "PDHB"]
FERRO = ["GPX4", "SLC7A11"]
NEG = ["CD274"]
CAT = {**{g: "copper" for g in COPPER}, **{g: "ferroptosis_ref" for g in FERRO},
       **{g: "immune_negctrl" for g in NEG}}


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    r = p[o] * n / (np.arange(n) + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.clip(r, 0, 1)
    return out


def mw_auc(t, n):
    n1, n2 = len(t), len(n)
    ranks = pd.Series(np.concatenate([t, n])).rank(method="average").values
    U = ranks[:n1].sum() - n1 * (n1 + 1) / 2.0
    auc = U / (n1 * n2)
    sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    z = (U - n1 * n2 / 2.0) / sd if sd else 0.0
    return auc, 0.5 * (1 - math.erf(z / math.sqrt(2)))


ph = pd.read_csv(os.path.join(BASE, "phenotype.tsv"), sep="\t", dtype=str, low_memory=False)
ph = ph[["sample", "_sample_type", "primary disease or tissue", "_study"]]
ph.columns = ["sample", "type", "disease", "study"]
ph["tum"] = ph["type"].str.lower().str.contains("tumor") & ~ph["type"].str.lower().str.contains("normal")
ph["nor"] = ph["type"].str.lower().str.contains("normal")

ex = pd.read_csv(os.path.join(BASE, "target_genes_tpm.tsv"), sep="\t", index_col=0)
ex.index = [i.split(".")[0] for i in ex.index]
pm = pd.read_csv(os.path.join(BASE, "probemap.tsv"), sep="\t")
pm["id"] = pm["id"].str.split(".").str[0]
ex.index = [dict(zip(pm.id, pm.gene)).get(i, i) for i in ex.index]
ex = ex[~ex.index.duplicated()]

meta = ph.set_index("sample").reindex(ex.columns)
tpm = lambda v: np.clip(np.power(2.0, v) - 0.001, 0, None)

rows = []
for disease, g in meta.groupby("disease"):
    if not isinstance(disease, str):
        continue
    tum = g.index[(g.tum == True) & (g.study.str.upper() == "TCGA")]
    nor = g.index[(g.nor == True) & (g.study.str.upper() == "TCGA")]
    if len(tum) < 20 or len(nor) < 3:
        continue
    for gene in ex.index:
        t, n = to_tpm = None, None
        t = tpm(ex.loc[gene, tum].astype(float).values)
        n = tpm(ex.loc[gene, nor].astype(float).values)
        p95 = np.percentile(n, 95)
        if p95 <= 0:
            continue
        medt, medn = np.median(t), np.median(n)
        auc, p = mw_auc(t, n)
        rows.append({
            "disease": disease, "gene": gene, "category": CAT.get(gene, "other"),
            "n_tumour": len(tum), "n_normal": len(nor),
            "median_tumour": medt, "median_normal": medn,
            "median_ratio": medt / medn if medn > 0 else np.nan,
            "selectivity_index": np.percentile(t, 5) / p95,
            "auc": auc, "p_onesided": p,
        })

df = pd.DataFrame(rows)
df["q_fdr"] = bh(df["p_onesided"].values)
df["sig_enriched"] = (df["q_fdr"] < 0.05) & (df["auc"] > 0.5)

main = df[df.n_normal >= MIN_N].copy()
expl = df[df.n_normal < MIN_N].copy()

df.to_csv(os.path.join(BASE, "selectivity_all_pairs.csv"), index=False, encoding="utf-8-sig")
main.to_csv(os.path.join(BASE, "selectivity_main_n10.csv"), index=False, encoding="utf-8-sig")
expl.to_csv(os.path.join(BASE, "selectivity_exploratory_small_n.csv"), index=False, encoding="utf-8-sig")


def report(tag, d):
    print(f"\n=== {tag} (n={len(d)} pairs) ===")
    print(f"  S > 1            : {int((d.selectivity_index>1).sum())}")
    print(f"  S < 1            : {100*(d.selectivity_index<1).mean():.1f}%")
    print(f"  median S         : {d.selectivity_index.median():.3f}")
    print(f"  median ratio > 1 : {int((d.median_ratio>1).sum())} ({100*(d.median_ratio>1).mean():.1f}%)")
    print(f"  significant enriched: {int(d.sig_enriched.sum())}")
    print(f"  both ratio>1 and S>1: {int(((d.median_ratio>1)&(d.selectivity_index>1)).sum())}")


report("MAIN: n_normal >= %d" % MIN_N, main)
report("EXPLORATORY: n_normal < %d" % MIN_N, expl)

# per-gene table on main
gt = (main.groupby(["category", "gene"])
      .agg(pairs=("disease", "nunique"),
           median_ratio=("median_ratio", "median"),
           median_S=("selectivity_index", "median"),
           pct_ratio_gt1=("median_ratio", lambda s: round(100 * (s > 1).mean(), 1)),
           pct_S_gt1=("selectivity_index", lambda s: round(100 * (s > 1).mean(), 1)),
           n_sig=("sig_enriched", "sum"))
      .reset_index()
      .sort_values(["category", "median_ratio"], ascending=[True, False]))
gt.to_csv(os.path.join(BASE, "gene_summary_main.csv"), index=False, encoding="utf-8-sig")

print("\n=== per-gene (main) ===")
print(gt.round(2).to_string(index=False))

# copper only
cop = main[main.category == "copper"]
print(f"\ncopper genes only (main): {len(cop)} pairs, "
      f"S>1 = {int((cop.selectivity_index>1).sum())}, "
      f"ratio>1 = {int((cop.median_ratio>1).sum())}, "
      f"sig enriched = {int(cop.sig_enriched.sum())}")
