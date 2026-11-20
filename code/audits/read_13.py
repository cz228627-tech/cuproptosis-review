# -*- coding: utf-8 -*-
"""Read the full texts and build a per-paper dossier for manual judgement."""

import re
import urllib.request
import xml.etree.ElementTree as ET

PAPERS = [
    ("42375344", "PMC13310888"), ("42662336", "PMC13520559"), ("31344923", "PMC6724019"),
    ("20535236", "PMC2882109"), ("32251998", "PMC7132150"), ("39290994", "PMC11405343"),
    ("39915841", "PMC11800420"), ("41261257", "PMC12630286"), ("42939442", "PMC13701374"),
    ("42149287", "PMC13183766"), ("39913607", "PMC11801720"), ("37702109", "PMC10591933"),
    ("41510087", "PMC12776229"),
]
EF = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NORMAL = r"(normal|non-?malignant|non-?tumorigenic|hepatocyte|mrc-?5|wi-?38|mcf-?10a|hmec|pbmc|huvec|hk-?2|thle|astrocyte|neuron|fibroblast)"
QUANT = r"(IC50|IC 50|EC50|EC 50|GI50|CC50|selectivity index)"

for pmid, pmc in PAPERS:
    num = pmc.replace("PMC", "")
    try:
        root = ET.fromstring(urllib.request.urlopen(f"{EF}?db=pmc&rettype=xml&id={num}", timeout=90).read())
    except Exception as e:
        print(f"\n##### {pmid}: fetch failed {type(e).__name__}")
        continue

    title = "".join(root.find(".//article-title").itertext()) if root.find(".//article-title") is not None else ""
    abst = " ".join("".join(p.itertext()) for p in root.iter("abstract"))
    body = " ".join("".join(x.itertext()) for x in root.iter("body"))
    caps = " ".join("".join(x.itertext()) for x in root.iter("caption"))
    clean = lambda s: re.sub(r"\s+", " ", s).strip()

    print("\n" + "=" * 108)
    print(f"### {pmid} | {pmc} | {clean(title)[:100]}")

    # quantitative sentences that also name a normal-cell type
    qs = []
    for m in re.finditer(r"[^.]{0,260}" + QUANT + r"[^.]{0,260}", body, re.I):
        s = clean(m.group(0))
        if re.search(NORMAL, s, re.I) and re.search(r"\d", s):
            qs.append(s)
    print(f"[quant+normal sentences: {len(qs)}]")
    for s in qs[:3]:
        print("   >", s[:300])

    # figure captions naming a normal cell type
    cq = [clean(c) for c in re.split(r"(?<=[.!?])\s+", caps) if re.search(NORMAL, c, re.I)]
    print(f"[figure captions naming a normal cell: {len(cq)}]")
    for c in cq[:2]:
        print("   #", c[:300])
