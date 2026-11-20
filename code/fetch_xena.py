# -*- coding: utf-8 -*-
"""Resumable download of the UCSC Xena TCGA/GTEx TOIL matrix + extraction of copper genes."""

import gzip
import os
import time
import urllib.request
from urllib.error import URLError, HTTPError

BASE = r"C:\work\xena"
os.makedirs(BASE, exist_ok=True)
LOG = os.path.join(BASE, "fetch.log")

PROBEMAP = "https://toil.xenahubs.net/download/probeMap/gencode.v23.annotation.gene.probemap"
PHENO = "https://toil.xenahubs.net/download/TcgaTargetGTEX_phenotype.txt.gz"
EXPR = "https://toil.xenahubs.net/download/TcgaTargetGtex_rsem_gene_tpm.gz"

TARGETS = {
    "SLC31A1", "ATP7A", "ATP7B", "MT1X", "MT2A",
    "FDX1", "LIAS", "LIPT1", "DLAT", "DLD", "PDHA1", "PDHB",
    "GPX4", "SLC7A11", "CD274",
}


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def remote_size(url):
    r = urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60)
    return int(r.headers.get("Content-Length", "0"))


def download_resumable(url, dest, tries=8):
    total = remote_size(url)
    log(f"remote size: {total/1024**2:.1f} MB -> {dest}")
    for attempt in range(1, tries + 1):
        pos = os.path.getsize(dest) if os.path.exists(dest) else 0
        if total and pos >= total:
            return total
        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=180) as r, \
                 open(dest, "ab" if pos else "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    pos += len(chunk)
                    if pos % (100 << 20) < (1 << 20):
                        log(f"  {pos/1024**2:.0f} / {total/1024**2:.0f} MB")
            if not total or os.path.getsize(dest) >= total:
                return total
            log(f"  short read, retry ({attempt})")
        except (URLError, HTTPError, ConnectionError, OSError) as e:
            log(f"  attempt {attempt} failed: {type(e).__name__}: {e}")
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError("download failed after retries")


# ---------- 1. probemap
pm = os.path.join(BASE, "probemap.tsv")
download_resumable(PROBEMAP, pm)

ens_to_symbol = {}
with open(pm, encoding="utf-8") as f:
    f.readline()
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            ens_to_symbol.setdefault(p[0].split(".")[0], p[1])

wanted = {e for e, s in ens_to_symbol.items() if s in TARGETS}
log(f"target genes mapped: {len(wanted)} / {len(TARGETS)}")

# ---------- 2. phenotype
ph_gz = os.path.join(BASE, "phenotype.txt.gz")
try:
    download_resumable(PHENO, ph_gz)
    with gzip.open(ph_gz, "rt", encoding="utf-8", errors="replace") as src, \
         open(os.path.join(BASE, "phenotype.tsv"), "w", encoding="utf-8") as dst:
        dst.write(src.read())
    log("phenotype ready")
except Exception as e:
    log(f"phenotype skipped: {e}")

# ---------- 3. expression matrix
expr_gz = os.path.join(BASE, "TcgaTargetGtex_rsem_gene_tpm.gz")
if os.path.getsize(expr_gz) if os.path.exists(expr_gz) else 0:
    pass
download_resumable(EXPR, expr_gz)

# ---------- 4. extract target rows
out_path = os.path.join(BASE, "target_genes_tpm.tsv")
log("extracting target rows")
kept = 0
with gzip.open(expr_gz, "rt", encoding="utf-8", errors="replace") as f, \
     open(out_path, "w", encoding="utf-8", newline="") as out:
    for i, line in enumerate(f):
        if i == 0:
            out.write(line)
            continue
        gid = line.split("\t", 1)[0].split(".")[0]
        if gid in wanted:
            out.write(line)
            kept += 1
            log(f"  kept {ens_to_symbol.get(gid, gid)}")

log(f"done: {kept} rows -> {out_path}")
