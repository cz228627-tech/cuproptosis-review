# -*- coding: utf-8 -*-
"""Second pass: include tables/floats and look for actual numeric IC50 values."""

import re
import urllib.request
import xml.etree.ElementTree as ET

PAPERS = {
    "42375344": "PMC13310888", "42662336": "PMC13520559", "31344923": "PMC6724019",
    "20535236": "PMC2882109", "32251998": "PMC7132150", "39290994": "PMC11405343",
    "39915841": "PMC11800420", "41261257": "PMC12630286", "42939442": "PMC13701374",
    "42149287": "PMC13183766", "39913607": "PMC11801720", "37702109": "PMC10591933",
    "41510087": "PMC12776229",
}
EF = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


for pmid, pmc in PAPERS.items():
    num = pmc.replace("PMC", "")
    try:
        raw = urllib.request.urlopen(f"{EF}?db=pmc&rettype=xml&id={num}", timeout=90).read()
        root = ET.fromstring(raw)
    except Exception as e:
        print(f"{pmid}: fetch failed {type(e).__name__}")
        continue

    tables = []
    for tw in root.iter("table-wrap"):
        txt = clean(" ".join("".join(x.itertext()) for x in tw.iter()))
        if re.search(r"(IC50|IC 50|EC50|IC₅₀)", txt, re.I):
            tables.append(txt[:500])

    body = clean(" ".join("".join(x.itertext()) for x in root.iter("body")))
    nums = []
    for m in re.finditer(r"[^.]{0,220}(IC50|IC 50|EC50|IC₅₀)[^.]{0,220}", body):
        s = m.group(0)
        if re.search(r"\d", s) and re.search(r"(normal|non-?malignant|HEK|fibroblast|hepatocyte|PBMC|MCF|HUVEC|HK-2|astrocyte|neuron)", s, re.I):
            nums.append(clean(s))

    if tables or nums:
        print(f"\n=== {pmid} ({pmc}) tables_with_IC50={len(tables)} sentences={len(nums)}")
        for t in tables[:2]:
            print("  [TABLE]", t[:420])
        for s in nums[:4]:
            print("  [TEXT ]", s[:420])
    else:
        print(f"{pmid}: no numeric IC50 near a normal-cell term")
