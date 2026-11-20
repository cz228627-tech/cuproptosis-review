# -*- coding: utf-8 -*-
"""Find papers reporting intracellular copper in glioma/GBM cells after extracellular copper exposure."""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
QS = [
    'glioma[tiab] AND "intracellular copper"[tiab]',
    'glioblastoma[tiab] AND copper[tiab] AND ("ICP-MS"[tiab] OR "inductively coupled"[tiab] OR "copper content"[tiab] OR "labile copper"[tiab])',
    '(glioma[tiab] OR glioblastoma[tiab]) AND copper[tiab] AND (accumulation[tiab] OR uptake[tiab] OR influx[tiab])',
    '(glioma[tiab] OR glioblastoma[tiab]) AND (copper[tiab]) AND (homeostasis[tiab] OR buffering[tiab] OR metallothionein[tiab])',
]

seen = {}
for q in QS:
    u = f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=40&term={urllib.parse.quote(q)}"
    ids = json.loads(urllib.request.urlopen(u, timeout=40).read())["esearchresult"]["idlist"]
    print(f"{len(ids):>3}  {q[:90]}")
    for i in ids:
        seen.setdefault(i, []).append(q[:40])

ids = list(seen)
print("unique:", len(ids))

rows = []
for i in range(0, len(ids), 100):
    chunk = ids[i:i + 100]
    u = f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}"
    root = ET.fromstring(urllib.request.urlopen(u, timeout=120).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
        yr = art.findtext(".//PubDate/Year") or ""
        jr = art.findtext(".//Journal/ISOAbbreviation") or ""
        rows.append({"pmid": pmid, "year": yr, "jr": jr,
                     "title": re.sub(r"\s+", " ", title),
                     "abst": re.sub(r"\s+", " ", abst)})

KEY = r"(intracellular|uptake|accumulat|influx|labile|ICP-MS|content)"
for r in sorted(rows, key=lambda x: x["year"], reverse=True):
    t = (r["title"] + " " + r["abst"]).lower()
    if "copper" in t and re.search(KEY, t, re.I) and ("glioma" in t or "glioblastoma" in t):
        print(f"\n{r['pmid']} {r['year']} {r['jr'][:24]}")
        print("  ", r["title"][:140])
        # print the copper-relevant sentence
        for s in re.split(r"(?<=[.!?])\s+", r["abst"]):
            if "copper" in s.lower() and re.search(KEY, s, re.I):
                print("   >", s[:300])
                break
