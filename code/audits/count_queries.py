# -*- coding: utf-8 -*-
import json
import urllib.parse
import urllib.request

B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=1&term="

QS = {
    "elesclomol[tiab]": 'elesclomol[tiab]',
    "elesclomol|disulfiram + selectivity index": '("elesclomol"[tiab] OR "disulfiram"[tiab]) AND ("selectivity index"[tiab] OR "therapeutic index"[tiab])',
    "copper complex + selectivity index": '("copper complex"[tiab] OR "copper(II) complex"[tiab] OR "Cu(II) complex"[tiab]) AND "selectivity index"[tiab]',
    "cuproptosis + normal cell": 'cuproptosis[tiab] AND ("normal cell"[tiab] OR "normal cells"[tiab] OR "non-tumorigenic"[tiab] OR "non-malignant"[tiab])',
    "disulfiram + normal cell/PBMC/hepatocyte": '("disulfiram"[tiab] AND ("normal cell"[tiab] OR "normal cells"[tiab] OR "PBMC"[tiab] OR "hepatocyte"[tiab]))',
    "elesclomol + hepatocyte/neuron": '("elesclomol"[tiab] OR "copper ionophore"[tiab]) AND ("hepatocyte"[tiab] OR "hepatocytes"[tiab] OR "neuron"[tiab] OR "neurons"[tiab])',
}

for k, t in QS.items():
    url = B + urllib.parse.quote(t)
    d = json.loads(urllib.request.urlopen(url, timeout=30).read())
    print(f'{int(d["esearchresult"]["count"]):>6}  {k}')
