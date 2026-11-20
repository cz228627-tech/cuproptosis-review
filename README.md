# cuproptosis-review

Analysis code and derived tables for a critical review of copper-ionophore selectivity in cancer.

**Manuscript:** *Copper ionophores in cancer therapy: efficacy claims without a selectivity baseline*
(Chao Zhang, First Hospital of Jilin University; ORCID 0009-0000-6639-8638)

## What this repository contains

| Folder | Contents |
|---|---|
| `code/` | Every script used to produce the figures, the supplementary table and the literature audit |
| `data/` | Derived tables (selectivity indices, programme scores, permutation null, the six-pair table) |

## Data sources

All primary data are public and are **not** redistributed here.

- **TCGA / GTEx** — TOIL RSEM gene expression (log2[TPM+0.001]), via UCSC Xena
  (`TcgaTargetGtex_rsem_gene_tpm.gz`, https://xenabrowser.net/datapages/)
- **GDSC2** — fitted dose–response, release 8.5, file `GDSC2_fitted_dose_response.xlsx`
  (https://www.cancerrxgene.org/downloads)

## Reproducing the figures

```
python code/make_fig1_v6.py            # Figure 2  (transcript comparison)
python code/make_fig3_v2.py            # Figure 1  (glioblastoma mismatches)
python code/make_fig2_v2.py            # Figure 3  (pharmacology / GDSC2)
python code/make_fig_framework.py      # Figure 4  (framework)
python code/make_figS1_v2.py           # Supplementary Figure S1 (GDSC2 fields)
python code/supp_table_s2_v2.py        # Supplementary Table S2
python code/label_permutation.py       # label-permutation null (AUC 0.50 vs observed 0.33, P < 0.002)
python code/analyze_xena.py            # selectivity index and programme scores from the raw matrix
```

Scripts expect the raw downloads in `C:\work\xena\` and `C:\work\depmap\`; edit the `BASE` constants
at the top of each file to point elsewhere.

## Key derived numbers

| Quantity | Value | File |
|---|---|---|
| Pairs in the primary analysis | 240 (15 genes x 16 cancer types, n_normal >= 10) | `data/selectivity_main_n10.csv` |
| Copper-gene pairs reaching S > 1 | 0 of 192 | `data/selectivity_main_n10.csv` |
| Pairs exceeding S > 1 in the unfiltered matrix | 6 of 315, all with n_normal 3-9 | `data/supp_table_S2_six_pairs.csv` |
| Median programme AUC | 0.33 (label-permutation null 0.50; P < 0.002) | `data/per_cancer_programme.csv` |
| GDSC2 IC50 values beyond the top dose | 100 of 225 (44.4%) | `data/` + Figure 3 |

## Literature audit

The audit counts reported in the manuscript (385 records, 287 primary anticancer studies, 11 mentioning a
non-malignant cell, 1 comparator, 0 paired IC50) are reproducible from the search strings recorded in Box 1
of the manuscript; the screening scripts are in `code/audits/`.

## License

Code: MIT (see `LICENSE`).
Derived tables in `data/`: CC BY 4.0.

## Citation

If you use these scripts or tables, please cite the manuscript (reference to be added on publication) and this
archive.
