# -*- coding: utf-8 -*-
"""Pilot literature search: copper ionophores with normal-cell comparisons."""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

QUERIES = {
    "Q1_elesclomol_normal": '("elesclomol"[tiab] OR "STA-4783"[tiab]) AND ("IC50"[tiab] OR "cytotoxicity"[tiab] OR "viability"[tiab]) AND ("normal"[tiab] OR "non-malignant"[tiab] OR "non-tumorigenic"[tiab] OR "hepatocytes"[tiab] OR "MCF-10A"[tiab] OR "MRC-5"[tiab] OR "WI-38"[tiab] OR "PBMC"[tiab])',
    "Q2_ionophore_SI": '("copper ionophore"[tiab] OR "Cu-elesclomol"[tiab] OR "disulfiram"[tiab] OR "NSC319726"[tiab] OR "cuproptosis"[tiab]) AND ("selectivity index"[tiab] OR "IC50"[tiab]) AND ("normal cells"[tiab] OR "non-tumorigenic"[tiab] OR "non-malignant"[tiab])',
    "Q3_organ_tox": '("elesclomol"[tiab] OR "copper ionophore"[tiab] OR "cuproptosis"[tiab]) AND ("primary hepatocytes"[tiab] OR "neurons"[tiab] OR "neurotoxicity"[tiab] OR "hepatotoxicity"[tiab]) AND ("IC50"[tiab] OR "EC50"[tiab] OR "concentration"[tiab])',
}

NORMAL_TERMS = ["hepatocyte", "mrc-5", "wi-38", "mcf-10a", "hmec", "pbmc", "huvuc",
                "huvec", "hk-2", "thle", "l-02", "astrocyte", "neuron", "fibroblast",
                "non-tumorigenic", "non-malignant", "normal cell", "normal human",
                "primary cell", "hek293", "cho", "cos-7"]


def esearch(term, retmax=60):
    u = f"{BASE}/esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}&term={urllib.parse.quote(term)}"
    return json.loads(urllib.request.urlopen(u, timeout=40).read())["esearchresult"]["idlist"]


ids = {}
for name, q in QUERIES.items():
    got = esearch(q)
    print(f"{name}: {len(got)} hits")
    for i in got:
        ids.setdefault(i, []).append(name)

all_ids = list(ids)
print(f"unique PMIDs: {len(all_ids)}")

if not all_ids:
    raise SystemExit

records = []
for chunk in [all_ids[i:i + 100] for i in range(0, len(all_ids), 100)]:
    u = f"{BASE}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}"
    root = ET.fromstring(urllib.request.urlopen(u, timeout=60).read())
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abst = " ".join("".join(p.itertext()) for p in art.iter("AbstractText"))
        year = art.findtext(".//PubDate/Year") or art.findtext(".//PubDate/MedlineDate") or ""
        journal = art.findtext(".//Journal/ISOAbbreviation") or ""
        low = (title + " " + abst).lower()
        hit_terms = [t for t in NORMAL_TERMS if t in low]
        has_ic50 = ("ic50" in low) or ("ic 50" in low) or ("ec50" in low)
        records.append({
            "pmid": pmid, "year": year, "journal": journal,
            "title": re.sub(r"\s+", " ", title)[:120],
            "normal_terms": ";".join(hit_terms[:4]),
            "has_ic50": has_ic50,
            "queries": ",".join(sorted(set(ids.get(pmid, [])))),
        })

records.sort(key=lambda r: (not (r["normal_terms"] and r["has_ic50"]), r["year"]), reverse=False)

print("\n=== candidates with a normal-cell term AND a quantitative endpoint ===")
n = 0
for r in records:
    if r["normal_terms"] and r["has_ic50"]:
        n += 1
        print(f"{r['pmid']}  {r['year']}  {r['journal'][:22]:22s}  [{r['normal_terms']}]")
        print(f"    {r['title']}")
print(f"\ncount: {n} / {len(records)}")

print("\n=== remaining (no normal-cell term in abstract) ===")
for r in records:
    if not (r["normal_terms"] and r["has_ic50"]):
        print(f"{r['pmid']}  {r['year']}  {r['title'][:100]}")
