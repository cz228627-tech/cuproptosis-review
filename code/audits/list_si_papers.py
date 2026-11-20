# -*- coding: utf-8 -*-
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
QS = [
    '("elesclomol"[tiab] OR "disulfiram"[tiab]) AND ("selectivity index"[tiab] OR "therapeutic index"[tiab])',
    '("copper complex"[tiab] OR "copper(II) complex"[tiab] OR "Cu(II) complex"[tiab]) AND "selectivity index"[tiab]',
]

ids = []
for q in QS:
    u = f"{B}/esearch.fcgi?db=pubmed&retmode=json&retmax=40&term={urllib.parse.quote(q)}"
    ids += json.loads(urllib.request.urlopen(u, timeout=30).read())["esearchresult"]["idlist"]
ids = list(dict.fromkeys(ids))

u = f"{B}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids)}"
root = ET.fromstring(urllib.request.urlopen(u, timeout=60).read())

for art in root.iter("PubmedArticle"):
    pmid = art.findtext(".//PMID")
    title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
    year = art.findtext(".//PubDate/Year") or ""
    jr = art.findtext(".//Journal/ISOAbbreviation") or ""
    print(f"{pmid}\t{year}\t{jr[:24]:24s}\t{re.sub(chr(10),' ',title)[:110]}")
