# -*- coding: utf-8 -*-
import urllib.request
import xml.etree.ElementTree as ET

ids = ["42662336", "20535236", "27510477", "41510087"]
u = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids)}"
root = ET.fromstring(urllib.request.urlopen(u, timeout=60).read())

for art in root.iter("PubmedArticle"):
    pmid = art.findtext(".//PMID")
    title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
    jr = art.findtext(".//Journal/ISOAbbreviation") or ""
    abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
    print("=" * 100)
    print(f"{pmid} | {jr}")
    print(title)
    print("-" * 100)
    print(abst[:1600])
    print()
