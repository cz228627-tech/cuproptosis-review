# -*- coding: utf-8 -*-
"""Read 37702109 (J Neurochem 2023) in detail: CuES effects on neurons vs astrocytes."""

import re
import urllib.request
import xml.etree.ElementTree as ET

u = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&rettype=xml&id=10591933"
root = ET.fromstring(urllib.request.urlopen(u, timeout=120).read())

title = "".join(root.find(".//article-title").itertext())
abst = re.sub(r"\s+", " ", " ".join("".join(p.itertext()) for p in root.iter("abstract")))
print("TITLE:", re.sub(r"\s+", " ", title))
print("\nABSTRACT:\n", abst, "\n")

body = " ".join("".join(x.itertext()) for x in root.iter("body"))
body = re.sub(r"\s+", " ", body)

# key result sentences
pats = [
    r"[^.]{0,300}(FDX1|ferredoxin)[^.]{0,300}\.",
    r"[^.]{0,250}(neuron)[^.]{0,250}(spar|resist|surviv|unaffected|healthy)[^.]{0,200}\.",
    r"[^.]{0,250}(astrocyte)[^.]{0,250}(toxic|death|swell|LDH)[^.]{0,200}\.",
    r"[^.]{0,200}(1 ?µM|1 ?uM|CuES)[^.]{0,250}\.",
]
seen = set()
for p in pats:
    for m in re.finditer(p, body, re.I):
        s = m.group(0).strip()
        if len(s) < 40 or s[:80] in seen:
            continue
        seen.add(s[:80])
        print(" •", s[:400], "\n")
