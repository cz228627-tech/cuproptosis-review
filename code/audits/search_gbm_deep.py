# -*- coding: utf-8 -*-
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
QS = {
    "hypoxia": '(cuproptosis[tiab] OR elesclomol[tiab]) AND (hypoxia[tiab] OR HIF[tiab]) AND (glioma*[tiab] OR glioblastoma*[tiab] OR GBM[tiab])',
    "GSC": '(cuproptosis[tiab] OR elesclomol[tiab]) AND ("glioma stem"[tiab] OR "stem-like"[tiab] OR GSC*[tiab])',
    "recurrence": '(cuproptosis[tiab] OR elesclomol[tiab]) AND (recurren*[tiab] OR "acquired resistance"[tiab]) AND (glioma*[tiab] OR glioblastoma*[tiab])',
}
for tag, q in QS.items():
    ids = json.loads(urllib.request.urlopen(
        f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=40&term={urllib.parse.quote(q)}",
        timeout=40).read())["esearchresult"]["idlist"]
    print(f"\n=== {tag}: {len(ids)} hits ===")
    if not ids:
        continue
    root = ET.fromstring(urllib.request.urlopen(
        f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids[:40])}", timeout=120).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        yr = art.findtext(".//PubDate/Year") or ""
        jr = art.findtext(".//Journal/ISOAbbreviation") or ""
        print(f"  {pmid} {yr} {jr[:20]:20s} {re.sub(r'[[:space:]]+',' ',title)[:105]}")
