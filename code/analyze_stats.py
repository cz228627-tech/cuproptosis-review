# -*- coding: utf-8 -*-
"""P0: add statistical inference to the selectivity analysis.

For every gene x cancer-type pair:
  - S = P5(tumour TPM) / P95(adjacent normal TPM)
  - bootstrap 95% CI for S (1000 resamples)
  - one-sided Mann-Whitney (tumour > normal) via normal approximation, BH-FDR across pairs
  - AUC (probability that a random tumour sample exceeds a random normal sample)
"""

import math
import os
import numpy as np
import pandas as pd

BASE = r"C:\work\xena"
OUT = os.path.join(BASE, "selectivity_index_stats.csv")
rng = np.random.default_rng(20261117)
NBOOT = 1000


def bh_fdr(p):
    p = np.asarray(p, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(ranked, 0, 1)
    return out


def mw_auc(t, n):
    """AUC and one-sided p (tumour > normal) by normal approximation."""
    t = np.asarray(t, float)
    n = np.asarray(n, float)
    n1, n2 = len(t), len(n)
    allv = np.concatenate([t, n])
    ranks = pd.Series(allv).rank(method="average").values
    R1 = ranks[:n1].sum()
    U = R1 - n1 * (n1 + 1) / 2.0
    auc = U / (n1 * n2)
    mu = n1 * n2 / 2.0
    sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    z = (U - mu) / sd if sd > 0 else 0.0
    p = 0.5 * (1 - math.erf(z / math.sqrt(2)))
    return auc, p


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
to_tpm = lambda v: np.clip(np.power(2.0, v) - 0.001, 0, None)

rows = []
for disease, g in meta.groupby("disease"):
    if not isinstance(disease, str):
        continue
    tum = g.index[(g.tum == True) & (g.study.str.upper() == "TCGA")]
    nor = g.index[(g.nor == True) & (g.study.str.upper() == "TCGA")]
    if len(tum) < 20 or len(nor) < 3:
        continue
    for gene in ex.index:
        t = to_tpm(ex.loc[gene, tum].astype(float).values)
        n = to_tpm(ex.loc[gene, nor].astype(float).values)
        p95n = np.percentile(n, 95)
        if p95n <= 0:
            continue
        s = np.percentile(t, 5) / p95n
        boots = []
        for _ in range(NBOOT):
            ts = rng.choice(t, len(t), replace=True)
            ns = rng.choice(n, len(n), replace=True)
            d = np.percentile(ns, 95)
            boots.append(np.percentile(ts, 5) / d if d > 0 else np.nan)
        boots = np.array(boots, float)
        lo, hi = np.nanpercentile(boots, [2.5, 97.5])
        auc, p = mw_auc(t, n)
        rows.append({
            "disease": disease, "gene": gene,
            "n_tumour": len(t), "n_normal": len(n),
            "selectivity_index": round(s, 3),
            "S_ci_low": round(lo, 3), "S_ci_high": round(hi, 3),
            "ci_upper_below_1": bool(hi < 1),
            "auc": round(auc, 3), "p_onesided": p,
        })

df = pd.DataFrame(rows)
df["q_fdr"] = bh_fdr(df["p_onesided"].values)
df["sig_enriched"] = (df["q_fdr"] < 0.05) & (df["auc"] > 0.5)
df.to_csv(OUT, index=False, encoding="utf-8-sig")

n = len(df)
print(f"pairs: {n}")
print(f"S CI upper < 1: {(df.ci_upper_below_1).sum()} ({df.ci_upper_below_1.mean()*100:.1f}%)")
print(f"FDR<0.05 and tumour>normal: {df.sig_enriched.sum()} ({df.sig_enriched.mean()*100:.1f}%)")
print(f"median S: {df.selectivity_index.median():.3f}")
print(f"median AUC: {df.auc.median():.3f}")
print("\nAUC distribution:")
print(df.auc.describe().round(3).to_string())
print("\nPairs where tumours are significantly enriched:")
if df.sig_enriched.any():
    print(df[df.sig_enriched][["disease", "gene", "auc", "q_fdr", "selectivity_index"]].round(3).to_string(index=False))
else:
    print("  none")
print("\nTop 8 by AUC:")
print(df.nlargest(8, "auc")[["disease", "gene", "auc", "q_fdr", "selectivity_index"]].round(3).to_string(index=False))
