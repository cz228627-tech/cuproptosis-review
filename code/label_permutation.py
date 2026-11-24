# -*- coding: utf-8 -*-
"""Label-permutation null for the programme AUC (audit item H2)."""

import numpy as np
import pandas as pd

BASE = r"C:\work\xena"
mat = pd.read_csv(BASE + r"\target_genes_tpm.tsv", sep="\t")
ids = mat["sample"].tolist()
X = mat.drop(columns=["sample"]).values.astype(float)      # genes x samples (log2 TPM)
samples = list(mat.columns[1:])

pm = pd.read_csv(BASE + r"\probemap.tsv", sep="\t", dtype=str)
pm.columns = [c.strip() for c in pm.columns]
idcol = [c for c in pm.columns if "id" in c.lower()][0]
symcol = "gene"
mp = dict(zip(pm[idcol].str.split(".").str[0], pm[symcol]))
symbols = [mp.get(i.split(".")[0], i) for i in ids]
print("genes:", symbols)

ph = pd.read_csv(BASE + r"\phenotype.tsv", sep="\t", dtype=str, low_memory=False)
ph = ph[["sample", "_sample_type", "primary disease or tissue", "_study"]]
ph.columns = ["sample", "type", "disease", "study"]
tl = ph["type"].str.lower()
ph["tum"] = tl.str.contains("tumor") & ~tl.str.contains("normal")
ph["nor"] = tl.str.contains("normal")

COPPER = ["MT1X", "MT2A", "FDX1", "ATP7A", "DLD", "LIAS", "DLAT", "PDHB", "LIPT1", "SLC31A1", "ATP7B", "PDHA1"]
idx = [symbols.index(g) for g in COPPER]

idx_of = {s: i for i, s in enumerate(samples)}
meta = ph.set_index("sample")
groups = []
for disease, g in meta.groupby("disease"):
    if not isinstance(disease, str):
        continue
    tum = [idx_of[s] for s in g.index[(g.tum == True) & (g.study.str.upper() == "TCGA")] if s in idx_of]
    nor = [idx_of[s] for s in g.index[(g.nor == True) & (g.study.str.upper() == "TCGA")] if s in idx_of]
    if len(tum) >= 20 and len(nor) >= 10:
        groups.append((np.array(tum), np.array(nor)))
print("cancer types:", len(groups))


def auc_of(a, b):
    n1, n2 = len(a), len(b)
    r = pd.Series(np.concatenate([a, b])).rank(method="average").values
    return (r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n2)


def programme(idx_genes, tum, nor, seed=None):
    sub = X[idx_genes][:, np.concatenate([tum, nor])]
    z = (sub - sub.mean(axis=1, keepdims=True)) / np.clip(sub.std(axis=1, keepdims=True), 1e-9, None)
    sc = z.mean(axis=0)
    return sc[:len(tum)], sc[len(tum):]


obs = []
for tum, nor in groups:
    a, b = programme(idx, tum, nor)
    obs.append(auc_of(a, b))
obs = np.array(obs)
print(f"\nobserved median AUC: {np.median(obs):.3f}  (per-cancer range {obs.min():.2f}-{obs.max():.2f})")

rng = np.random.default_rng(20261120)
null = []
for _ in range(500):
    aucs = []
    for tum, nor in groups:
        a, b = programme(idx, tum, nor)
        allv = np.concatenate([a, b])
        perm = rng.permutation(len(allv))
        aucs.append(auc_of(allv[perm][:len(a)], allv[perm][len(a):]))
    null.append(np.median(aucs))
null = np.array(null)
print(f"label-permutation null: median {null.mean():.3f} (SD {null.std():.3f}), "
      f"2.5-97.5% {np.percentile(null,2.5):.3f}-{np.percentile(null,97.5):.3f}")
print(f"empirical P (null <= observed): {(null <= np.median(obs)).mean():.3f}")
