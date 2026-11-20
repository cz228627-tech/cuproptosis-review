# -*- coding: utf-8 -*-
"""Per-cancer analysis with a coordinated 'copper programme' score.

Pre-committed decision rule (fixed before running):
  A cancer type is called 'window-positive' only if
    programme AUC >= 0.70  AND  FDR < 0.05  AND  direction = tumour higher.
  If no cancer meets all three -> the conclusion is 'no cancer type shows a window'.
"""

import math
import os
import numpy as np
import pandas as pd

BASE = r"C:\work\xena"
MIN_N = 10
COPPER = ["SLC31A1", "ATP7A", "ATP7B", "MT1X", "MT2A",
          "FDX1", "LIAS", "LIPT1", "DLAT", "DLD", "PDHA1", "PDHB"]


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    r = p[np.argsort(o)] if False else p[o] * n / (np.arange(n) + 1)
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
ex = ex.loc[[g for g in COPPER if g in ex.index]]
lin = np.clip(np.power(2.0, ex.astype(float)) - 0.001, 0, None)
logx = np.log2(lin + 1.0)

meta = ph.set_index("sample").reindex(logx.columns)
rows = []
for disease, g in meta.groupby("disease"):
    if not isinstance(disease, str):
        continue
    tum = g.index[(g.tum == True) & (g.study.str.upper() == "TCGA")]
    nor = g.index[(g.nor == True) & (g.study.str.upper() == "TCGA")]
    if len(tum) < 20 or len(nor) < MIN_N:
        continue
    sub = logx[tum.union(nor)]
    z = sub.sub(sub.mean(axis=1), axis=0).div(sub.std(axis=1).replace(0, np.nan), axis=0)
    score = z.mean(axis=0)
    auc, p = mw_auc(score[tum].values, score[nor].values)
    # descriptive: best single-gene S in this cancer
    ss = []
    for gene in logx.index:
        t = lin.loc[gene, tum].values
        n = lin.loc[gene, nor].values
        p95 = np.percentile(n, 95)
        if p95 > 0:
            ss.append((gene, np.percentile(t, 5) / p95))
    best_gene, best_s = max(ss, key=lambda x: x[1])
    rows.append({"disease": disease, "n_tumour": len(tum), "n_normal": len(nor),
                 "programme_auc": auc, "p": p,
                 "median_score_tumour": float(np.median(score[tum])),
                 "median_score_normal": float(np.median(score[nor])),
                 "best_gene": best_gene, "best_S": best_s})

d = pd.DataFrame(rows).sort_values("programme_auc", ascending=False)
d["q_fdr"] = bh(d["p"].values)
d["window_positive"] = (d.programme_auc >= 0.70) & (d.q_fdr < 0.05)

pd.set_option("display.width", 200)
print(d[["disease", "n_tumour", "n_normal", "programme_auc", "q_fdr",
         "median_score_tumour", "median_score_normal", "best_gene", "best_S", "window_positive"]]
      .round(3).to_string(index=False))
print()
print("cancer types analysed:", len(d))
print("window-positive:", int(d.window_positive.sum()))
print("max programme AUC:", round(d.programme_auc.max(), 3), "|", d.iloc[0]["disease"])
print("max single-gene S across all cancers:", round(d.best_S.max(), 3))

d.to_csv(os.path.join(BASE, "per_cancer_programme.csv"), index=False, encoding="utf-8-sig")
