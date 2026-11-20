# -*- coding: utf-8 -*-
"""GBM-subset audit: among glioma cuproptosis studies, how many test neuronal/astrocyte toxicity?"""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
Q = ('(cuproptosis[tiab] OR "copper ionophore"[tiab] OR elesclomol[tiab] OR "copper-induced cell death"[tiab]) '
     'AND (glioma*[tiab] OR glioblastoma*[tiab] OR GBM[tiab])')

ids = json.loads(urllib.request.urlopen(
    f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=800&term={urllib.parse.quote(Q)}",
    timeout=60).read())["esearchresult"]["idlist"]
print("records:", len(ids))

rows = []
for i in range(0, len(ids), 120):
    chunk = ids[i:i + 120]
    root = ET.fromstring(urllib.request.urlopen(
        f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}", timeout=150).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
        yr = art.findtext(".//PubDate/Year") or ""
        types = [t.text or "" for t in art.iter("PublicationType")]
        rows.append({
            "pmid": pmid, "year": yr,
            "title": re.sub(r"\s+", " ", title),
            "text": (title + " " + abst).lower(),
            "review": any("Review" in t for t in types),
            "abst": re.sub(r"\s+", " ", abst),
        })

NEURO = ["neuron", "neuronal", "astrocyte", "microglia", "neural stem", "brain slice",
         "organotypic", "neurotoxic"]
CYT = ["ic50", "ic 50", "ec50", "viability", "cytotox", "cell death", "apoptosis", "ldh release"]

primary = [r for r in rows if not r["review"]]
print(f"reviews: {sum(r['review'] for r in rows)}")
print(f"primary: {len(primary)}")

with_neuro = [r for r in primary if any(t in r["text"] for t in NEURO)]
print(f"\nprimary studies mentioning neurons/astrocytes/microglia: {len(with_neuro)} "
      f"({100*len(with_neuro)/max(len(primary),1):.1f}%)")

both = [r for r in with_neuro if any(t in r["text"] for t in CYT)]
print(f"...also mentioning a cytotoxicity readout: {len(both)}")

print("\n=== the ones mentioning neurons/astrocytes (primary studies) ===")
for r in sorted(with_neuro, key=lambda x: x["year"], reverse=True):
    terms = [t for t in NEURO if t in r["text"]]
    print(f"\n{r['pmid']} {r['year']} [{','.join(sorted(set(terms))[:3])}]")
    print("   ", r["title"][:120])
    for s in re.split(r"(?<=[.!?])\s+", r["abst"]):
        if any(t in s.lower() for t in NEURO):
            print("    >", s[:260])
            break
