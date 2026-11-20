# -*- coding: utf-8 -*-
import re
import urllib.request
import xml.etree.ElementTree as ET

IDS = ["40002329", "41344596", "43002217", "42748964", "42665028", "37741885", "40163909"]
u = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(IDS)}"
root = ET.fromstring(urllib.request.urlopen(u, timeout=90).read())

for art in root.iter("PubmedArticle"):
    pmid = art.findtext(".//PMID")
    title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
    jr = art.findtext(".//Journal/ISOAbbreviation") or ""
    yr = art.findtext(".//PubDate/Year") or ""
    abst = re.sub(r"\s+", " ", " ".join("".join(p.itertext()) for p in art.iter("AbstractText")))
    print("=" * 100)
    print(f"{pmid} | {yr} | {jr}")
    print(title)
    print("-" * 100)
    for s in re.split(r"(?<=[.!?])\s+", abst):
        if re.search(r"copper|cu\b|glutathione|metallothionein|MTF1", s, re.I):
            print("  •", s[:330])
    print()
