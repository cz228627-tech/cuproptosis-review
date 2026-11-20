# -*- coding: utf-8 -*-
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
QS = {
    "liver": '(cuproptosis[tiab] OR "copper-induced cell death"[tiab]) AND (hepatocyte*[tiab] OR "liver injury"[tiab] OR hepatotoxic*[tiab])',
    "neuron": '(cuproptosis[tiab] OR "copper-induced cell death"[tiab]) AND (neuron*[tiab] OR astrocyte*[tiab] OR neurotoxic*[tiab])',
}
for tag, q in QS.items():
    ids = json.loads(urllib.request.urlopen(
        f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=60&term={urllib.parse.quote(q)}",
        timeout=40).read())["esearchresult"]["idlist"]
    print(f"\n=== {tag}: {len(ids)} hits ===")
    root = ET.fromstring(urllib.request.urlopen(
        f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids)}", timeout=120).read())
    rows = []
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        yr = art.findtext(".//PubDate/Year") or ""
        jr = art.findtext(".//Journal/ISOAbbreviation") or ""
        abst = re.sub(r"\s+", " ", " ".join("".join(p.itertext()) for p in art.iter("AbstractText")))
        rows.append((yr, pmid, jr, re.sub(r"\s+", " ", title), abst))
    rows.sort(reverse=True)
    for yr, pmid, jr, title, abst in rows[:12]:
        print(f"  {pmid} {yr} {jr[:22]:22s} {title[:105]}")
