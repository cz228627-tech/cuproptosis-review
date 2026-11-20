# -*- coding: utf-8 -*-
"""Verify the 381 -> 27 -> 3 -> 0 chain: recount, then screen all 27 abstracts properly."""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# ---------- 1. recount with the drug's former name included
Q = '(elesclomol[tiab] OR "STA-4783"[tiab] OR "elesclomol sodium"[tiab])'
u = f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=500&term={urllib.parse.quote(Q)}"
ids = json.loads(urllib.request.urlopen(u, timeout=40).read())["esearchresult"]["idlist"]
print(f"query: elesclomol OR STA-4783 OR elesclomol sodium -> {len(ids)} records")

# ---------- 2. fetch all abstracts
recs = []
for i in range(0, len(ids), 120):
    chunk = ids[i:i + 120]
    uu = f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}"
    root = ET.fromstring(urllib.request.urlopen(uu, timeout=120).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
        yr = art.findtext(".//PubDate/Year") or ""
        recs.append({"pmid": pmid, "year": yr,
                     "title": re.sub(r"\s+", " ", title),
                     "abstract": re.sub(r"\s+", " ", abst)})

NORMAL = ["normal cell", "normal cells", "non-malignant", "nonmalignant", "non-tumorigenic",
          "nontumorigenic", "normal human", "normal hepatocyte", "primary hepatocyte",
          "mrc-5", "wi-38", "mcf-10a", "hmec", "pbmc", "huvec", "huvuc", "hk-2",
          "thle", "l-02", "astrocyte", "neuron", "fibroblast", "hek293", "hek-293"]
hit = [r for r in recs if any(t in (r["title"] + " " + r["abstract"]).lower() for t in NORMAL)]
print(f"mention any non-malignant cell term: {len(hit)} ({100*len(hit)/len(recs):.1f}%)")

print("\n" + "=" * 110)
for r in hit:
    txt = (r["title"] + " " + r["abstract"]).lower()
    terms = [t for t in NORMAL if t in txt]
    # sentences that contain a normal-cell term AND a cytotoxicity word
    sents = [s for s in re.split(r"(?<=[.!?])\s+", r["abstract"])
             if any(t in s.lower() for t in NORMAL) and re.search(r"(viabilit|cytotox|ic50|kill|survival|apoptos)", s, re.I)]
    print(f"\n### {r['pmid']} ({r['year']}) terms={terms[:3]}")
    print("TITLE:", r["title"][:130])
    if sents:
        print("  >>", sents[0][:330])
    else:
        print("  (no sentence links a non-malignant cell to a cytotoxicity readout)")
