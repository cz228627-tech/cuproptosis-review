# -*- coding: utf-8 -*-
"""Abstract-level gap analysis: how many elesclomol papers report a non-malignant comparator?"""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
Q = 'elesclomol[tiab]'

u = f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=500&term={urllib.parse.quote(Q)}"
ids = json.loads(urllib.request.urlopen(u, timeout=40).read())["esearchresult"]["idlist"]
print("elesclomol[tiab] records:", len(ids))

NORMAL = ["normal cell", "normal cells", "non-malignant", "nonmalignant", "non-tumorigenic",
          "nontumorigenic", "normal human", "normal hepatocyte", "primary hepatocyte",
          "mrc-5", "wi-38", "mcf-10a", "hmec", "pbmc", "huvec", "huvuc", "hk-2",
          "thle", "l-02", "astrocyte", "neuron", "fibroblast", "hek293", "hek-293"]
QUANT = ["ic50", "ic 50", "ec50", "gi50", "selectivity index", "therapeutic index"]

rows = []
for i in range(0, len(ids), 100):
    chunk = ids[i:i + 100]
    u = f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}"
    root = ET.fromstring(urllib.request.urlopen(u, timeout=90).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
        low = (title + " " + abst).lower()
        rows.append({
            "pmid": pmid, "title": re.sub(r"\s+", " ", title),
            "normal": [t for t in NORMAL if t in low],
            "quant": [t for t in QUANT if t in low],
        })

n = len(rows)
with_normal = [r for r in rows if r["normal"]]
with_both = [r for r in rows if r["normal"] and r["quant"]]

print(f"abstracts retrieved: {n}")
print(f"mention any non-malignant comparator: {len(with_normal)} ({100*len(with_normal)/n:.1f}%)")
print(f"mention both a comparator and a quantitative endpoint: {len(with_both)} ({100*len(with_both)/n:.1f}%)")

print("\n=== those mentioning a comparator AND a quantitative endpoint ===")
for r in with_both:
    print(f"{r['pmid']}  [{','.join(r['normal'][:3])}]")
    print(f"    {r['title'][:120]}")

print("\n=== comparator mentioned, no quantitative term in abstract ===")
for r in with_normal:
    if r not in with_both:
        print(f"{r['pmid']}  [{','.join(r['normal'][:3])}]  {r['title'][:90]}")
