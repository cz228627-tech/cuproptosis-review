# -*- coding: utf-8 -*-
"""Audit the denominator: what are the 385 records actually made of?"""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
Q = '(elesclomol[tiab] OR "STA-4783"[tiab] OR "elesclomol sodium"[tiab])'
ids = json.loads(urllib.request.urlopen(
    f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=500&term={urllib.parse.quote(Q)}",
    timeout=40).read())["esearchresult"]["idlist"]

rows = []
for i in range(0, len(ids), 120):
    chunk = ids[i:i + 120]
    root = ET.fromstring(urllib.request.urlopen(
        f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}", timeout=120).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
        yr = art.findtext(".//PubDate/Year") or ""
        types = [t.text or "" for t in art.iter("PublicationType")]
        rows.append({"pmid": pmid, "year": yr,
                     "title": re.sub(r"\s+", " ", title),
                     "text": (title + " " + abst).lower(),
                     "types": types})

print(f"records: {len(rows)}")

CANCER = ["cancer", "tumour", "tumor", "carcinoma", "glioma", "glioblastoma", "leukemia",
          "leukaemia", "melanoma", "sarcoma", "neoplasm", "malignan", "oncolog", "myeloma",
          "lymphoma", "adenocarcinoma"]
NONCANCER_ONLY = ["menkes", "wilson", "alzheimer", "parkinson", "stroke", "ischemi",
                  "cardiac", "kidney injury", "wound", "scar", "infection", "antimicrob",
                  "antiviral", "leishman", "trypanosoma", "staphylococcus", "mycobacter"]

is_review = [any("Review" in t for t in r["types"]) for r in rows]
is_cancer = [any(k in r["text"] for k in CANCER) for r in rows]
is_errata = [any(("Erratum" in t or "Comment" in t or "Editorial" in t or "Retraction" in t)
                 for t in r["types"]) for r in rows]

n = len(rows)
print(f"  reviews                 : {sum(is_review)}")
print(f"  errata/comment/editorial: {sum(is_errata)}")
print(f"  mention cancer terms    : {sum(is_cancer)}")
print(f"  non-review + cancer     : {sum(1 for i in range(n) if is_cancer[i] and not is_review[i] and not is_errata[i])}")
print(f"  non-review + NO cancer  : {sum(1 for i in range(n) if not is_cancer[i] and not is_review[i] and not is_errata[i])}")

from collections import Counter
yrs = Counter(r["year"] for r in rows)
print("\nyear distribution (top 12):", sorted(yrs.items())[-12:])

# how many primary cancer papers mention a non-malignant cell?
NORMAL = ["normal cell", "normal cells", "non-malignant", "nonmalignant", "non-tumorigenic",
          "nontumorigenic", "normal human", "normal hepatocyte", "primary hepatocyte",
          "mrc-5", "wi-38", "mcf-10a", "hmec", "pbmc", "huvec", "huvuc", "hk-2",
          "thle", "l-02", "astrocyte", "neuron", "fibroblast", "hek293", "hek-293"]
sub = [r for i, r in enumerate(rows) if is_cancer[i] and not is_review[i] and not is_errata[i]]
hit = [r for r in sub if any(t in r["text"] for t in NORMAL)]
print(f"\nprimary cancer papers: {len(sub)}")
print(f"  of which mention a non-malignant cell: {len(hit)} ({100*len(hit)/max(len(sub),1):.1f}%)")
