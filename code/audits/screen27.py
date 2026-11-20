# -*- coding: utf-8 -*-
"""Screen the 27 comparator-mentioning papers: PMC availability + extractable normal-cell IC50 text."""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

PMIDS = ["42939442", "42863734", "42812787", "42662336", "42617725", "42375344",
         "42214610", "42149287", "41457948", "41261257", "40998065", "40917066",
         "39924054", "39915841", "39913607", "39423623", "39394530", "39290994",
         "39288174", "37702109", "35167033", "32251998", "31344923", "27510477",
         "25078786", "20535236", "41510087"]

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

NORMAL = r"(normal|non-?malignant|non-?tumorigenic|hepatocyte|mrc-?5|wi-?38|mcf-?10a|hmec|pbmc|huvec|hk-?2|thle|astrocyte|neuron|fibroblast|nephrotox|hepatotox)"
QUANT = r"(IC50|IC 50|EC50|EC 50|GI50|selectivity index|SI\b)"


def get_meta(pmid):
    u = f"{EPMC}?query=EXT_ID:{pmid}&format=json&resultType=core&pageSize=1"
    try:
        r = json.loads(urllib.request.urlopen(u, timeout=30).read())
        rec = r["resultList"]["result"][0]
        return {
            "pmid": pmid,
            "title": rec.get("title", "")[:95],
            "pmcid": rec.get("pmcid", ""),
            "oa": rec.get("isOpenAccess", "N") == "Y",
        }
    except Exception as e:
        return {"pmid": pmid, "title": f"[meta failed: {e}]", "pmcid": "", "oa": False}


def sentences(text):
    t = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", t)
    out = []
    for s in parts:
        if re.search(QUANT, s, re.I) and re.search(NORMAL, s, re.I) and len(s) < 900:
            out.append(s.strip())
    return out


results = []
for p in PMIDS:
    m = get_meta(p)
    m["sentences"] = []
    if m["pmcid"]:
        num = m["pmcid"].replace("PMC", "")
        try:
            u = f"{EFETCH}?db=pmc&rettype=xml&id={num}"
            raw = urllib.request.urlopen(u, timeout=90).read()
            root = ET.fromstring(raw)
            body = " ".join("".join(x.itertext()) for x in root.iter("body"))
            m["sentences"] = sentences(body)[:6]
        except Exception as e:
            m["sentences"] = [f"[fulltext failed: {type(e).__name__}]"]
    results.append(m)

print(f"{'PMID':10s} {'PMC':12s} {'OA':3s} title")
for r in results:
    print(f"{r['pmid']:10s} {r['pmcid'] or '-':12s} {'Y' if r['oa'] else 'N':3s} {r['title']}")

print("\n\n=== extractable sentences (normal-cell + quantitative) ===")
for r in results:
    if r["sentences"] and not str(r["sentences"][0]).startswith("["):
        print(f"\n--- {r['pmid']} | {r['pmcid']} | {r['title']}")
        for s in r["sentences"]:
            print("   *", s[:420])
