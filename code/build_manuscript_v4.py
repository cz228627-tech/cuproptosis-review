# -*- coding: utf-8 -*-
"""Manuscript v2 — adds the glioblastoma four-mismatch section and corrects the neurotoxicity claim."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"C:\work\manuscript_draft_v4.docx"
NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x50, 0x50, 0x50)


def font(run, size=10.5, bold=False, italic=False, color=None, ea="宋体", latin="Times New Roman"):
    run.font.name = latin
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.append(rf)
    rf.set(qn("w:eastAsia"), ea)
    rf.set(qn("w:ascii"), latin)
    rf.set(qn("w:hAnsi"), latin)


def P(doc, text, size=10.5, bold=False, italic=False, color=None, after=6, spacing=1.5, first=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = spacing
    if first:
        p.paragraph_format.first_line_indent = Cm(first)
    r = p.add_run(text)
    font(r, size=size, bold=bold, italic=italic, color=color)
    return p


def H(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 9)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    font(r, size=13 if level == 1 else 11, bold=True, color=NAVY, ea="微软雅黑", latin="Arial")


def shade(cell, hexcolor):
    tc = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), hexcolor)
    tc.append(s)


def table(doc, headers, rows, widths, fs=7.6):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        font(r, size=fs + 0.6, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), ea="微软雅黑", latin="Arial")
        shade(c, "1F3864")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(0)
            r = cells[i].paragraphs[0].add_run(v)
            font(r, size=fs)
    grid = t._tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w * 567)))
    for row in t.rows:
        for c, w in zip(row.cells, widths):
            c.width = Cm(w)


doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Cm(21.0), Cm(29.7)
s.left_margin = s.right_margin = Cm(2.2)
s.top_margin = s.bottom_margin = Cm(2.0)

P(doc, "Copper ionophores in cancer therapy: efficacy claims without a selectivity baseline",
  size=16, bold=True, color=NAVY, after=8, spacing=1.2)
P(doc, "[Author names] · [Affiliations] · Corresponding author: [ ]", size=9, color=GREY, after=3, spacing=1.0)
P(doc, "Draft v4 · 18 November 2026 · full-length draft for internal review",
  size=8.5, italic=True, color=GREY, after=14, spacing=1.0)

H(doc, "Abstract")
P(doc, "Cuproptosis, described in 2022 as a copper-dependent, mitochondria-centred mode of cell death, is routinely "
       "presented as a tumour-selective vulnerability. More than 380 publications on its prototypical inducer, "
       "elesclomol, have appeared in four years, and annual output is still rising. We asked what the record shows. "
       "In the only phase 3 trial of a copper ionophore the primary endpoint was not met and the trial stopped early "
       "for an overall-survival imbalance favouring control; in a randomised trial in recurrent glioblastoma, adding "
       "copper raised grade ≥3 toxicity from 11% to 34% without survival benefit. Across 240 tumour–adjacent-normal "
       "pairs from 16 cancer types, copper-homeostasis genes showed no threshold-level separation (0/240), whereas the "
       "ferroptosis gene SLC7A11 was 3.19-fold higher in tumours. In the GDSC2 screen elesclomol was tested over only "
       "0.0002–0.2 µM without copper supplementation, and 44% of fitted IC50 values lay beyond the highest dose. Of "
       "287 primary anticancer studies of elesclomol, 11 mentioned a non-malignant cell type, one used it as a "
       "cytotoxicity comparator, and none reported a paired normal-versus-tumour IC50. We then examine glioblastoma, "
       "the indication most often proposed for this approach, and find four independent reasons why it is among the "
       "least suitable: the tumour is hypoxic and glycolytic, its stem cells are reported to resist, the surrounding "
       "brain is both the target and the tissue at risk, and resistance is acquired at recurrence. Of 115 primary "
       "glioma studies, one tested the surrounding parenchyma and none reported a tumour-versus-parenchyma selectivity "
       "ratio. The field has not established a selectivity baseline for the drug class it treats as targeted therapy.",
  after=10)
P(doc, "Keywords: cuproptosis; elesclomol; disulfiram; glioblastoma; therapeutic window; evidence gap",
  size=9, italic=True, after=14)

# ---------------- 1
H(doc, "1. Introduction")
P(doc, "When a new form of cell death is described, the field acquires two things at once: a mechanism and a promise. "
       "The mechanism is usually reported carefully; the promise is usually not. For cuproptosis, the mechanism paper "
       "was explicit about its dependence on mitochondrial respiration and on a specific lipoylation machinery [1]. "
       "The promise — that this machinery constitutes a tumour-selective vulnerability — was supplied by the "
       "surrounding literature and has since been repeated in more than three hundred reviews; annual output rose from 23 papers in 2022 to 118 in 2026.")
P(doc, "The promise is not unreasonable. Ferroptosis, a neighbouring metal-dependent death programme, has a genuine "
       "dependency structure: some tumours depend on GPX4 in a way that normal tissue does not, and this asymmetry has "
       "been pursued clinically. It was natural to assume that cuproptosis would behave similarly. The difference is "
       "that, for ferroptosis, the asymmetry was measured before it was marketed.")
P(doc, "This review asks a narrow question: has anyone measured the equivalent asymmetry for copper ionophores? "
       "Asymmetry between tumour and host is what ‘therapeutic window’ denotes; without it, ‘vulnerability’ describes "
       "a mechanism rather than a treatment. We examine four levels of evidence — the human trial record, the "
       "transcriptomic comparison, the cell-line pharmacology, and the preclinical literature itself — and then apply "
       "the analysis to glioblastoma, the tumour type in which this approach is most often proposed. Where a level "
       "cannot answer the question, we say so rather than substituting a proxy.")
P(doc, "Two conventions apply throughout. First, we distinguish the mechanism from the molecule: a compound that "
       "delivers copper is not, by that fact, a cuproptosis inducer, and several drugs discussed below are not. "
       "Second, absence of evidence is reported as absence of evidence; a negative finding about a literature is a "
       "finding about the literature, not about biology.")


P(doc, "This review is therefore not a survey of cuproptosis biology; readers seeking one are well served "
       "elsewhere [14,15]. Nor is it a systematic review: no protocol was registered and no formal quality appraisal "
       "was performed. What it offers is an audit of one claim — that copper ionophores exploit a tumour-selective "
       "vulnerability — together with the reasoning that would be needed to make that claim testable. We are explicit "
       "about what we do not show: we do not show that cuproptosis cannot be induced in human tumours, because no "
       "study has attempted it in a form that would answer the question.")
P(doc, "Negative claims require a different kind of evidence from positive ones. A single experiment can establish "
       "that a mechanism operates; no single experiment can establish that a measurement has never been made. The only "
       "route is an explicit and reproducible accounting of the literature — which is why a substantial part of this "
       "review is a count, and why the search strings, dates and inclusion rules are given in full rather than "
       "summarised.")

# ---------------- 2
H(doc, "2. What cuproptosis requires, and why selectivity cannot be assumed")
P(doc, "Cuproptosis depends on three things: mitochondrial respiration, a functional FDX1–LIAS–lipoylation axis, and "
       "an increase in intracellular copper [1,2]. Cells shifted towards glycolysis are resistant; cells with high "
       "respiratory flux are sensitive. Death follows aggregation of lipoylated TCA-cycle proteins and loss of "
       "iron–sulfur cluster proteins, and is prevented by copper chelation.")
P(doc, "This definition has an uncomfortable implication. The requirement is not a property of malignant "
       "transformation; it is a property of oxidative metabolism. Two of the tissues that limit copper dosing in "
       "humans are themselves highly oxidative. The liver carries a large mitochondrial volume and depends on "
       "oxidative phosphorylation for gluconeogenesis and ureagenesis, although its metabolic zonation leaves "
       "substantial glycolytic capacity. The brain consumes roughly a fifth of resting oxygen, and neurons depend on "
       "oxidative phosphorylation for ion homeostasis, although astrocytes are predominantly glycolytic. The argument "
       "does not require that these be the most oxidative tissues in the body, only that they be oxidative enough to "
       "be susceptible — and human copper overload confirms that they are: Wilson disease damages the liver and the "
       "basal ganglia; Menkes disease damages the developing brain [13,12].")
P(doc, "Copper handling provides the second half of the argument. Cells defend against copper excess through "
       "metallothioneins, glutathione, and the ATP7A/ATP7B export pumps [3]. These systems are not tumour-specific and "
       "their capacity varies widely between tissues. A window can therefore arise in only two ways: the tumour must "
       "have higher respiratory dependence, or lower buffering capacity, than the dose-limiting normal tissue. Both "
       "are measurable; neither has been measured systematically for this drug class.")

P(doc, "The two routes deserve to be stated precisely, because both are narrow. The first — higher respiratory "
       "dependence in the tumour than in the dose-limiting tissue — is unlikely on first principles: glioblastoma is "
       "among the most glycolytic of tumours, and the tissues at risk are among the most oxidative. The second — lower "
       "buffer capacity in the tumour — is plausible but has never been measured in matched tissue. Neither route has "
       "been excluded; both have been assumed.")
P(doc, "The definition also sets a standard that most of the literature does not meet. To call a death cuproptotic "
       "requires, at minimum, dependence on FDX1 or on lipoylation and reversal by copper chelation; a rise in "
       "intracellular copper, or an effect of a copper chelator, is not sufficient. In the studies reviewed below, "
       "these criteria are rarely tested, and where they have been tested the answer has sometimes been negative "
       "(§4.4). The definitional question is therefore not pedantry: it determines which observations count as "
       "evidence that the mechanism works at all.")
P(doc, "One caution belongs here, because it bears on how toxicity should be interpreted. It is tempting to describe "
       "the hepatic and neurological toxicity of copper ionophores as ‘on-target’ death in the wrong tissue. For the "
       "liver the description is plausible, since hepatocytes undergo copper-induced death with the features of "
       "cuproptosis [19,20]. For the brain it is not: the only study to test the surrounding parenchyma found that "
       "copper–elesclomol killed astrocytes while sparing neurons, and that the astrocyte death was independent of "
       "FDX1 and reversible by antioxidants — that is, not cuproptosis [21]. The toxicity of this drug class is "
       "therefore not uniformly ‘the same mechanism in the wrong place’, and we return to this in §4. The distinction matters: on-target, off-tumour toxicity cannot be engineered away by improving the molecule, whereas off-target toxicity can.")

P(doc, "Box 1. How the numbers in this review were produced", size=9.5, bold=True, color=NAVY, after=3)
P(doc, "Expression comparison. TCGA/GTEx TOIL RSEM (log2[TPM+0.001]) was back-transformed to linear TPM. TCGA primary "
       "tumours were compared with TCGA adjacent normal within the same cancer type, retaining pairs with ≥20 tumours "
       "and ≥10 normals. Selectivity index S = P5(tumour)/P95(normal); S > 1 denotes threshold-level separation. "
       "Effect size is AUC, with one-sided Mann–Whitney tests and Benjamini–Hochberg correction. Adjacent normal is "
       "not normal tissue [16].", size=8.8, after=3)
P(doc, "Cell-line pharmacology. GDSC2 fitted dose–response (release 8.5). The screened concentration range for "
       "elesclomol was 0.0002–0.2 µM; no copper supplementation is specified. Values fitted above the highest dose "
       "are extrapolations.", size=8.8, after=3)
P(doc, "Literature audits. PubMed, 17 November 2026. Whole field: elesclomol, STA-4783 or elesclomol sodium in "
       "title/abstract (385 records); after excluding reviews, errata and non-cancer records, 287 primary anticancer "
       "studies. Glioma subset: cuproptosis or copper ionophore terms with glioma, glioblastoma or GBM (131 records; "
       "115 primary studies). Abstracts were screened for non-malignant cell types; every hit was read in full text "
       "where machine-readable and classified by the role that cell played. Values present only in figures or "
       "supplements were not assessed.", size=8.8, after=12)

# ---------------- 3
H(doc, "3. The human record")
P(doc, "SYMMETRY, a phase 3 trial of elesclomol plus paclitaxel in 651 patients with advanced melanoma, did not meet "
       "its primary progression-free-survival endpoint (HR 0.89, P = 0.23). It was stopped early because an interim "
       "overall-survival analysis showed an imbalance in deaths favouring the control arm, concentrated among patients "
       "with elevated baseline LDH; a prospectively defined subgroup with normal LDH showed a significant PFS "
       "improvement [4]. This interaction is often cited as evidence of metabolic stratification. It should be cited "
       "more cautiously: LDH is itself a prognostic factor in melanoma staging, and a subgroup benefit in a trial "
       "stopped for harm cannot distinguish a predictive interaction from prognostic imbalance.")
P(doc, "DIRECT, a randomised phase 2/3 trial in 88 patients with recurrent glioblastoma, added disulfiram and copper "
       "to alkylating chemotherapy. Six-month survival was 44% with copper and 62% without (P = 0.10); median overall "
       "survival 5.5 versus 8.2 months; grade ≥3 adverse events rose from 11% to 34% and serious adverse events from "
       "16% to 41%. The authors concluded the combination was without benefit [5]. The trial was open-label and "
       "modest, and no survival difference reached conventional significance. What it establishes is that adding "
       "copper to a tolerable regimen produces substantially more toxicity without producing efficacy.")

P(doc, "Making LDH informative would require either a trial in which treatment was assigned by LDH status, or at "
       "least a formal interaction test with a pre-specified threshold. Neither exists. The distinction matters: a "
       "prognostic marker can stratify prognosis without stratifying benefit, and treating the two as interchangeable "
       "would license a biomarker that has not been shown to work.")
P(doc, "Both trials share a design limitation that bears on interpretation. Neither measured tumour drug exposure; "
       "the only human exposure data come from three surgical patients in a phase 1/2 study [7]. A trial that fails "
       "without evidence of target engagement cannot distinguish an inactive drug from an undelivered one — which is "
       "why the exposure data matter more than their sample size suggests, and why the negative result does not by "
       "itself settle the pharmacological question.")
P(doc, "A single-arm phase 2 study of temozolomide plus disulfiram and copper in 23 patients with recurrent "
       "temozolomide-resistant glioblastoma reported an objective response rate of 0% [6]. A phase 1/2 study in 33 "
       "patients with newly diagnosed glioblastoma measured the presumed active metabolite in plasma and, in three "
       "patients resected after preoperative dosing, in tumour tissue: plasma concentrations were 4.59, 0.44 and "
       "0.11 ng/mL and no metabolite was detected in any of the three tumours [7]; the maximum tolerated dose was "
       "limited by transaminase elevation. In platinum-resistant ovarian cancer, elesclomol with weekly paclitaxel was "
       "tolerable and largely inactive [8].")
P(doc, "One human use of this molecule deserves separate mention, because it cuts both ways. Elesclomol–copper has been reported to improve neurodevelopment in two infants with Menkes disease [12]; the report has been contested on grounds of attribution and injection-site toxicity [31] and defended by its authors [32]. Whatever its merits, the case shows that a copper ionophore can deliver copper in humans without triggering cuproptosis — which is the relevant point here.")
P(doc, "A separate point concerns attribution. Disulfiram is widely described in the cuproptosis literature as a "
       "copper-dependent cuproptosis inducer. Its principal characterised anticancer target is NPL4, an adaptor of the "
       "p97 segregase, identified in the study that also established the ditiocarb–copper complex as the active "
       "metabolite [9]. Copper is part of the molecule, but the death that follows is not the lipoylation-dependent "
       "death defined in [1]. Trials of disulfiram plus copper therefore inform us about copper pharmacology in "
       "patients; they do not test cuproptosis.")

table(doc,
      ["Trial", "Design / n", "Primary result", "Attribution"],
      [["SYMMETRY [4]", "Phase 3, n = 651, melanoma",
        "PFS endpoint not met (HR 0.89, P = 0.23); stopped for OS imbalance favouring control, concentrated in high-LDH patients; normal-LDH subgroup improved",
        "Copper ionophore; designed before cuproptosis was described"],
       ["DIRECT [5]", "Randomised phase 2/3, n = 88, recurrent GBM",
        "6-month survival 44% vs 62%; grade ≥3 AE 34% vs 11%; no survival benefit", "Ditiocarb–copper; NPL4/p97, not lipoylation"],
       ["Huang 2019 [6]", "Phase 2, single arm, n = 23, recurrent GBM", "ORR 0%; median OS 7.1 months", "As above"],
       ["Huang 2024 [7]", "Phase 1/2, n = 33, newly diagnosed GBM",
        "No OS/PFS gain vs institutional controls; metabolite detectable in plasma, not in tumour (n = 3); DLT transaminase elevation",
        "As above; tumour exposure not demonstrated"],
       ["Monk 2018 [8]", "Phase 2, n = 58, platinum-resistant ovarian", "Tolerable; low response", "Copper ionophore"],
       ["Menkes cases [12]", "Case series, n = 2", "Neurodevelopmental improvement with elesclomol–copper", "Copper replacement, not cytotoxicity"]],
      widths=[2.9, 3.6, 6.6, 4.1])
P(doc, "Table 1. Human studies of copper ionophores. The attribution column separates the molecule from the mechanism.",
  size=8, italic=True, color=GREY, after=10)

# ---------------- 4 (NEW)
H(doc, "4. Glioblastoma: the indication most often proposed, and among the least suitable")
P(doc, "Glioblastoma is repeatedly nominated as the natural home for cuproptosis-based therapy: FDX1 is expressed, "
       "stem-like cells are held to depend on mitochondrial metabolism, and local delivery is at least conceivable. We "
       "reach the opposite conclusion. Four features of the disease each act against the mechanism, and they act "
       "independently.")

P(doc, "Two of the indications most often discussed for this approach — glioblastoma and hepatocellular carcinoma — share a feature that is unusual among solid tumours: the dose-limiting organ is the organ that contains the tumour. In glioblastoma the tissue at risk is the brain; in hepatocellular carcinoma it is the liver, where hepatocytes undergo copper-induced death with the features of cuproptosis [19,20]. We develop glioblastoma in detail because it is the indication most frequently proposed and because parenchymal data, however limited, exist for it. The argument applies with at least equal force to hepatocellular carcinoma, where the target cell and the cell at risk are the same cell type. The remaining mismatches — hypoxia-driven glycolysis, stem-cell resistance and acquired resistance at recurrence — are not specific to either tumour; they are properties of aggressive solid tumours in general.")
P(doc, "4.1 The tumour's defining physiology suppresses the mechanism", size=10.5, bold=True, color=NAVY, after=3)
P(doc, "Glioblastoma is among the most hypoxic of solid tumours; necrosis with pseudopalisading is a diagnostic "
       "feature. Hypoxia stabilises HIF, which drives PDK1 and inhibitory phosphorylation of the pyruvate dehydrogenase "
       "complex — the complex that contains DLAT — shifting metabolism towards glycolysis. Cuproptosis requires "
       "respiratory flux, and glycolysis-shifted cells are the resistant phenotype in the original description [1]. "
       "The mechanism's central requirement is therefore opposed by the tumour's defining condition. The point is "
       "about flux and dependence, not about the presence of the target: PDH phosphorylation does not remove "
       "lipoylation, and lipoylated protein may still be present in a glycolytic cell. It is the dependence on that "
       "protein that falls.")
P(doc, "This intersection appears to be almost unexamined. A PubMed search combining cuproptosis or elesclomol with "
       "hypoxia or HIF and with glioma returns a single record, a radiotracer study [22]. For a mechanism whose "
       "defining variable is oxygen-dependent metabolism, and for a tumour defined by hypoxia, one publication is a "
       "striking omission.")

P(doc, "4.2 Delivering copper does not guarantee its accumulation", size=10.5, bold=True, color=NAVY, after=3)
P(doc, "In principle the barrier to cuproptosis could be solved by delivering more copper. In glioblastoma it has not been, and the reason appears to be cellular rather than anatomical. In human tissue, copper is significantly higher in the peritumoral region than in the tumour core [29]: the tumour is not a copper-rich compartment. In GBM cells, exposure to 20 µM copper does not simply load the cell — it increases cytochrome c oxidase activity, shifts metabolism towards oxidative phosphorylation and substantially increases glutathione and its precursors [27], which is the opposite of the intended effect. Inducible buffering is superimposed on this: YY1 sustains metallothionein expression through MTF1 and ALDH1A3, and silencing YY1 is what makes disulfiram–copper effective [28], while LAMC1 overexpression reduces intracellular copper accumulation and confers resistance [33]. Two nanomedicine studies make the same point from the delivery side: they exist because copper influx is inefficient and efflux is active [30], and because the accumulation achieved by ionophore alone is insufficient [22]. A tumour that responds to copper by increasing its buffer has, in effect, moved the target.")
P(doc, "4.3 The cells that must be killed are the cells reported to resist", size=10.5, bold=True, color=NAVY, after=3)
P(doc, "Glioblastoma stem cells are the population that survives therapy, and the literature on their copper "
       "sensitivity is internally inconsistent. Elesclomol has been reported to impair stem-like cell survival through "
       "mitochondrial reactive oxygen species [23]. More recent work reports the opposite: stem cells resist "
       "cuproptosis, with copper levels varying under circadian control [24], and with DLD lactylation sustaining "
       "resistance [25]. These findings are not necessarily in conflict. Reactive-oxygen-mediated killing and "
       "FDX1-dependent death are different mechanisms, and only the second is what the field claims to exploit. What "
       "is missing is the comparison that would settle it: no study reports the sensitivity of stem-like cells "
       "alongside that of neural progenitors or astrocytes from the same preparation.")

P(doc, "4.4 The tissue that must be traversed is the tissue at risk", size=10.5, bold=True, color=NAVY, after=3)
P(doc, "For most solid tumours the dose-limiting organ is distant from the target. In glioblastoma the target organ "
       "and the tissue at risk are the same. The blood–brain barrier is therefore not only a delivery obstacle; it is "
       "the only structure separating the tumour from the parenchyma that shares its exposure. Strategies that improve "
       "barrier penetration raise delivery to both compartments and do not, by themselves, alter their ratio.")
P(doc, "The single study to examine the parenchyma directly is instructive [21]. In mixed cortical cultures, "
       "copper–elesclomol killed astrocytes at 2 µM copper with 100–300 nM elesclomol, while neurons were spared; "
       "neuronal injury, where present, was secondary to astrocyte failure and was blocked by an NMDA antagonist. The "
       "astrocyte death was not cuproptosis: it was unaffected by Complex III or IV inhibition, by >90% knockdown of "
       "FDX1, or by inhibitors of apoptosis, necroptosis or ferroptosis, and it was rescued by antioxidants. Neurons "
       "resisted because of high basal metallothionein expression, and pharmacological induction of MT1/MT2 protected "
       "astrocytes completely.")
P(doc, "Two consequences follow. First, copper toxicity in the brain is not cuproptosis, and describing it as such "
       "reproduces the attribution error discussed above. Second, the same antioxidant that rescued astrocytes also "
       "rescued C6 glioma cells: tumour and parenchyma died by the same non-cuproptotic mechanism. The absence of "
       "selectivity therefore does not depend on cuproptosis being the operative pathway; it survives the substitution "
       "of a different one.")

P(doc, "4.5 The window closes with recurrence", size=10.5, bold=True, color=NAVY, after=3)
P(doc, "Two 2026 reports describe acquired cuproptosis resistance in recurrent glioblastoma, one of them framing it as "
       "a universal mechanism of resistance in recurrent disease [26], the other implicating DLD lactylation in stem "
       "cells [25]. Glioblastoma is defined by recurrence: the tumour that is resectable is not the tumour that "
       "eventually requires systemic therapy. If resistance is acquired, the target is present at the point when local "
       "treatment is feasible and diminished at the point when a copper ionophore would actually be given.")

P(doc, "4.6 What the glioma literature has actually tested", size=10.5, bold=True, color=NAVY, after=3)
P(doc, "Of 115 primary glioma studies of cuproptosis or copper ionophores, four mention neurons, astrocytes or "
       "microglia at all — three as expression comparators, immune populations or single-cell clusters — and one "
       "tests parenchymal toxicity [21]. None reports a tumour-versus-parenchyma selectivity ratio. For a therapy "
       "whose dose-limiting organ is the organ it must treat, that is the measurement that matters most, and it has "
       "not been made.")

# ---------------- 5
H(doc, "5. Copper-handling genes in tumours: a descriptive comparison")
P(doc, "If copper ionophores were to have a window, the relevant machinery should be more abundant in tumours than in "
       "the corresponding normal tissue. We tested that expectation descriptively.")
P(doc, "Across 240 tumour–adjacent-normal pairs from 16 cancer types, no pair reached threshold-level separation "
       "(S > 1 in 0/240); the median selectivity index was 0.23. Nearly half of the pairs (109/240, 45%) had a higher "
       "median in tumour than in normal tissue, yet none separated. Statistical enrichment and practical separation "
       "are different things, and only the latter supports a window. A coordinated programme score across the same "
       "genes gave a median AUC of 0.33 and was lower in tumours in 12 of the 16 cancer types, with a single cancer "
       "(stomach adenocarcinoma) showing coordinated enrichment (AUC 0.73) whose best single gene still failed to "
       "separate (S = 0.53).")

P(doc, "The programme score averages z-scored expression across the twelve copper genes within each cancer type. It "
       "asks whether the genes move together, which individual-gene tests cannot answer, and it is the level at which "
       "pathway enrichment is usually claimed. Its median AUC of 0.33 means that in the median cancer type a randomly "
       "chosen tumour is less likely than a randomly chosen normal sample to carry the higher score — the opposite of "
       "the direction a targetable dependency requires. The single exception is instructive rather than reassuring: "
       "stomach adenocarcinoma showed coordinated enrichment (AUC 0.73), yet no individual gene separated, so a drug "
       "would still face overlapping distributions.")
P(doc, "The analysis is not insensitive. In the same samples the ferroptosis gene SLC7A11 was 3.19-fold higher in "
       "tumours (higher in 94% of cancer types) and GPX4 1.33-fold higher, while the immune checkpoint CD274 behaved "
       "as a near-null negative control. Against these anchors the copper genes behaved like the negative control: "
       "FDX1 had a median ratio of 0.79 and was higher in only 19% of cancer types.")
P(doc, "Three limitations bound this section. Adjacent normal tissue is not normal tissue; it carries field effects "
       "[16]. Bulk tissue dilutes malignant signal with stroma. And mRNA is neither protein nor lipoylation status, so "
       "neither individual genes nor a coordinated programme score measures pathway activity — a pathway can be "
       "engaged without a transcriptional shift. The section therefore supports one statement only: at the transcript "
       "level, the copper machinery is not enriched in tumours in the way a targetable dependency would require. It "
       "does not measure a therapeutic window, and we do not use the phrase for it.")

# ---------------- 6
H(doc, "6. The preclinical selectivity gap")
P(doc, "In GDSC2, elesclomol was profiled in 225 cancer cell lines. Median AUC was 0.848 and only 1.8% of lines fell "
       "below 0.5. But the screen tested elesclomol over 0.0002–0.2 µM only, and the protocol does not supplement "
       "copper; under those conditions 44% of fitted IC50 values lie beyond the highest dose tested, so the fitted "
       "value is an extrapolation. A copper ionophore assayed without added copper, over a range below that used in "
       "most mechanistic studies, cannot distinguish intrinsic resistance from insufficient substrate. We treat this "
       "dataset as context, not as evidence of resistance.")
P(doc, "The literature itself is unambiguous. Of 287 primary anticancer studies of elesclomol, 11 mentioned any "
       "non-malignant cell type in the abstract (3.8%), one used such a cell as a cytotoxicity comparator, and none "
       "reported a paired normal-versus-tumour IC50. The glioma subset behaves the same way (§4.5). Most of the 11 "
       "mentioned neurons, astrocytes, fibroblasts or tubular cells as disease models rather than comparators, which "
       "is why the number falls from 11 to 1 on reading. Fourteen of the 27 abstracts mentioning any non-malignant "
       "cell had no machine-readable full text, so data confined to figures or supplements would not have been "
       "captured; the finding is a statement about what is reported in accessible text.")

P(doc, "Three features of this audit bound its interpretation, and we state them in the order a reader is likely to "
       "raise them. First, screening was at the abstract level for the 385 records and at full text for the 13 "
       "machine-readable papers among the 27 that mentioned a non-malignant cell; a study that performed the "
       "comparison without saying so in the abstract would be missed. Second, values reported only in figures or "
       "supplementary files were not extracted, and dose–response curves are frequently presented in exactly that "
       "form. Third, PubMed indexes neither most preprints nor most conference abstracts, where preliminary or "
       "negative comparisons are disproportionately likely to appear. Each of these biases runs in the same "
       "direction — toward under-counting — and correcting any of them would strengthen rather than weaken the "
       "conclusion.")
P(doc, "It is worth stating what would overturn this section. A single study reporting paired IC50 values for a "
       "copper ionophore in a tumour line and a matched non-malignant cell, with copper supplementation and a "
       "selectivity index above ten, would establish that a window is achievable in vitro. That is a low bar, and none "
       "of the 287 studies we screened clears it. The claim this review makes is correspondingly specific: not that no "
       "window exists, but that no one has reported one.")
P(doc, "The cell-line data illustrate why the distinction between a negative result and an uninformative one matters. "
       "A screen conducted without added copper, over a concentration range that leaves 44% of fitted values beyond "
       "the highest dose, cannot license the sentence ‘elesclomol is inactive in most cancer cell lines’. It can "
       "license only the narrower sentence we use, and the difference between the two is the difference between a "
       "finding and an artefact.")
P(doc, "A drug class cannot be described as tumour-selective on the basis of a literature that has not measured the "
       "denominator of selectivity. The gap is not an absence of enthusiasm; it is an absence of the one experiment "
       "that would license the enthusiasm.")

# ---------------- 7
H(doc, "7. What would make cuproptosis a vulnerability")
P(doc, "The preceding sections are negative, and a review that stopped there would be a complaint. We therefore set "
       "out the conditions under which the negative could be reversed, in a form that can fail.")
P(doc, "Three steps follow from the mechanism. First, the tumour must be pushed towards oxidative metabolism before "
       "copper is delivered; otherwise the agent is given to cells that have already shifted away from the death "
       "pathway. Second, patients must be selected on a measurable metabolic or buffering variable rather than on a "
       "transcriptomic score of uncertain function. Third, the sequence must be explicit: priming, verification, then "
       "loading. Each step is testable in existing model systems and each has a readout that would falsify the "
       "framework rather than merely fail to support it.")
P(doc, "The glioblastoma analysis sharpens the first requirement. Because the target organ and the tissue at risk are "
       "the same, the framework cannot be tested by improving delivery; it can only be tested by showing that tumour "
       "cells are more sensitive than the parenchyma at the same exposure. The relevant readouts are therefore the "
       "OCR/ECAR ratio after priming, basal LDH, lipoylated DLAT abundance, and metallothionein or glutathione "
       "capacity. The single protective variable identified in the parenchyma study was metallothionein induction "
       "[21], which suggests a concrete stratification hypothesis: tumours with low metallothionein capacity should "
       "respond at exposures that spare astrocytes, and those with high capacity should not.")

P(doc, "Each step has its own falsifying observation. If priming fails to raise the OCR/ECAR ratio in patient-derived "
       "cells, the first step is wrong and the framework collapses before copper is added. If priming succeeds but "
       "tumours with low metallothionein capacity are no more sensitive than those with high capacity, the "
       "stratification step is wrong. If both hold in vitro yet the same exposure kills astrocytes or hepatocytes at "
       "similar concentrations, the framework fails at the level that matters clinically — the ratio — even though "
       "every component behaved as predicted.")
P(doc, "The design implied is a biomarker-stratified, exposure-verified study rather than another unselected phase 2. "
       "It would require a pharmacodynamic readout in tumour tissue — lipoylated DLAT, or copper content — before "
       "efficacy is interpreted, because otherwise a negative result is uninformative, as the existing trials "
       "demonstrate. It would also require a pre-specified selectivity index measured in matched normal cells, because "
       "that, and not tumour response alone, is the quantity in question. Neither requirement is technically "
       "demanding; both are absent from the record.")
P(doc, "We label this a proposed framework, not a finding. It is included because the alternative — continuing to "
       "describe cuproptosis as a vulnerability while never measuring the denominator — is what produced the current "
       "impasse.")

# ---------------- 8
H(doc, "8. Conclusion")
P(doc, "Four years and several hundred publications after cuproptosis was defined, the field has not established the "
       "measurement that would justify calling it a therapeutic strategy. The human trials show toxicity without "
       "efficacy and, in glioblastoma, failure to demonstrate tumour exposure. The transcriptomic comparison shows no "
       "threshold-level separation for copper-homeostasis genes, while the same data detect clear enrichment for a "
       "ferroptosis gene. The cell-line screen is too narrow and too copper-poor to adjudicate. In 287 anticancer "
       "studies the primary literature has produced one qualitative normal-cell comparison and no paired IC50; in 115 "
       "glioma studies it has produced one parenchymal toxicity study and no selectivity ratio.")
P(doc, "Glioblastoma, the indication most often proposed, is on this evidence among the least suitable: hypoxic and "
       "glycolytic where the mechanism requires respiration, with stem cells reported to resist, with a surrounding "
       "tissue that is damaged by the same exposure, and with resistance acquired by the time systemic therapy is "
       "needed. None of this shows that cuproptosis cannot be exploited. It shows that the claim has been made without "
       "the measurement that would support it, and that the measurement is neither difficult nor expensive. Until it "
       "is made, cuproptosis should be described as a mechanism of copper toxicity, with a plausible but untested "
       "route to selectivity — not as a vulnerability that clinical translation has so far failed to realise. Two observations would change this conclusion: a selectivity ratio above ten demonstrated in matched human cells, or a trial in which tumour exposure and pathway engagement were documented alongside benefit. Neither exists, and both are obtainable.")

# ---------------- legends
H(doc, "Figure legends")
P(doc, "Figure 1. Copper-homeostasis genes are not enriched in tumours at the transcript level. (a) Selectivity index S = P5(tumour)/P95(adjacent normal) for 15 genes across 16 cancer types (240 pairs; n_normal ≥ 10); no pair exceeds S = 1. (b) Statistical enrichment versus threshold separation: AUC versus S for the same pairs. (c) Coordinated programme score across the twelve copper genes, by cancer type; median AUC 0.33, lower in tumours in 12 of 16 types. (d) Median tumour-to-normal ratio by gene, showing that SLC7A11 (3.19) behaves as a positive control and CD274 (1.08) as a negative control, against which the copper genes are indistinguishable from the negative control. Descriptive only; see §5 for limitations.", size=9, after=5)
P(doc, "Figure 2. The preclinical selectivity gap. (a) Elesclomol in 225 cancer cell lines (GDSC2); shaded region marks "
       "IC50 values fitted beyond the highest dose tested (0.2 µM). (b) Literature audit: of 287 primary anticancer "
       "studies, 11 mention a non-malignant cell type, one uses it as a cytotoxicity comparator, none reports a paired "
       "IC50.", size=9, after=5)
P(doc, "Figure 3. Glioblastoma as the least suitable indication. Four independent mismatches between the requirements "
       "of cuproptosis and the biology of the disease: hypoxia-driven glycolysis, stem-cell resistance, a target organ "
       "that is also the tissue at risk, and resistance acquired at recurrence. Below: the audit of 115 glioma studies.", size=9, after=5)
P(doc, "Figure 4. From unstratified loading to a testable strategy. (a) The current paradigm and its failure modes. "
       "(b) A proposed framework — metabolic priming, stratification by buffer capacity, then copper loading — with "
       "explicit falsification criteria. Panel (b) is a hypothesis, not a result.", size=9, after=12)

# ---------------- refs
H(doc, "References (verified; to be completed during formatting)")
refs = [
    "Tsvetkov P, et al. Copper induces cell death by targeting lipoylated TCA cycle proteins. Science. 2022;375(6586):1254–1261. PMID 35298263.",
    "Cobine PA, Brady DC. Cuproptosis: cellular and molecular mechanisms underlying copper-induced cell death. Mol Cell. 2022;82(10):1786–1787. PMID 35594843.",
    "Ge EJ, et al. Connecting copper and cancer: from transition metal signalling to metalloplasia. Nat Rev Cancer. 2022;22(2):102–113. PMID 34764459.",
    "O'Day SJ, et al. Final results of phase III SYMMETRY study. J Clin Oncol. 2013;31(9):1211–1218. PMID 23401447.",
    "Werlenius K, et al. Disulfiram and copper plus chemotherapy vs chemotherapy alone in recurrent glioblastoma. JAMA Netw Open. 2023;6(3):e234149. PMID 37000452.",
    "Huang J, et al. Temozolomide plus disulfiram and copper for recurrent temozolomide-resistant glioblastoma. J Neurooncol. 2019;142(3):537–544. PMID 30771200.",
    "Huang J, et al. Disulfiram and copper with radiation therapy and temozolomide for newly diagnosed glioblastoma. Int J Radiat Oncol Biol Phys. 2024;120(3):738–749. PMID 38768767.",
    "Monk BJ, et al. Elesclomol sodium and weekly paclitaxel in platinum-resistant ovarian cancer. Gynecol Oncol. 2018;151(3):422–427. PMID 30309721.",
    "Skrott Z, et al. Alcohol-abuse drug disulfiram targets cancer via p97 segregase adaptor NPL4. Nature. 2017;552(7684):194–199. PMID 29211715.",
    "Zulkifli M, et al. FDX1-dependent and independent mechanisms of elesclomol-mediated intracellular copper delivery. PNAS. 2023;120(10):e2216722120. PMID 36848556.",
    "Zulkifli M, et al. Elesclomol rescues mitochondrial copper deficiency without triggering cuproptosis. J Pharmacol Exp Ther. 2025;392(2):100048. PMID 40023603.",
    "Godoy-Molina E, et al. Elesclomol-copper therapy improves neurodevelopment in two children with Menkes disease. J Clin Invest. 2025;135(19):e193107. PMID 40728898.",
    "Członkowska A, et al. Wilson disease. Nat Rev Dis Primers. 2018;4(1):21. PMID 30190489.",
    "Ragusa C, Oliveri V. Cuproptosis inducers in cancer therapy: state of the art and challenges. Chem Rec. 2026;26(7):e70179. PMID 42333434.",
    "Suwara J, Hartman ML. Balancing between cuproplasia and copper-dependent cell death: ATOX1 in cancer. J Exp Clin Cancer Res. 2025;44:222. PMID 40721800.",
    "Aran D, et al. Comprehensive analysis of normal adjacent to tumor transcriptomes. Nat Commun. 2017;8:1077. PMID 29057876.",
    "Safaei R, Howell SB. Copper transporters regulate the cellular pharmacology and sensitivity to Pt drugs. Crit Rev Oncol Hematol. 2005;53(1):13–23. PMID 15607932.",
    "Lun X, et al. Disulfiram with copper enhances temozolomide in glioblastoma. Clin Cancer Res. 2016;22(15):3860–3875. PMID 27006494.",
    "Cuproptosis in iron overload hepatocytes. Cell Death Dis. 2026. PMID 42763343.",
    "Copper overload drives hepatic stellate cell activation via cuproptosis to exacerbate acute liver injury. 2026. PMID 42260670.",
    "Copper induces neuron-sparing, ferredoxin 1-independent astrocyte toxicity mediated by oxidative stress. J Neurochem. 2023. PMID 37702109.",
    "Angiopep-2-functionalized Cu-Mn oxide nanoplatform for blood–brain barrier penetration and radiotherapy-enhanced cuproptosis in glioma. Biomed Mater. 2026. PMID 42748964.",
    "Elesclomol-induced increase of mitochondrial reactive oxygen species impairs glioblastoma stem-like cell survival. J Exp Clin Cancer Res. 2021. PMID 34253243.",
    "Glioblastoma stem cells resist cuproptosis with circadian variation of copper levels. J Clin Invest. 2026. PMID 41480765.",
    "AARS2-SIRT5-driven DLD K445 lactylation promotes cuproptosis resistance in glioblastoma stem cells. Adv Sci. 2026. PMID 42806865.",
    "Electric-field-driven ferredoxin 1-independent cuproptosis induction overcomes therapy-induced resistance in glioblastoma. ACS Nano. 2026. PMID 42411583.",
    "Copper-induced enhancement of glioblastoma tumorigenicity via cytochrome c oxidase. Antioxidants. 2025. PMID 40002329.",
    "YY1 prevents copper ionophore-induced cell death by interacting with Sp1 and MTF1 in glioblastoma. Acta Biochim Biophys Sin. 2026. PMID 43002217.",
    "Assessment of 13 essential and toxic trace elements in tumor and peritumoral brain tissues from human glioblastoma. J Biol Inorg Chem. 2023. PMID 37741885.",
    "Omeprazole-mediated nanodelivery of copper for synchronous remodeling of copper influx and efflux in cuproptotic glioblastoma therapy. Acta Biomater. 2026. PMID 41344596.",
    "LAMC1 modulates cuproptosis in glioma cells. Biochim Biophys Acta Mol Cell Res. 2026. PMID 42665028.",
    "Kaler S. Concerns regarding the safety and efficacy of ES-Cu-Captisol for Menkes disease. J Clin Invest. 2026;136(4):e201900. PMID 41697741.",
    "Gohil VM, Petris MJ, Palau F. Reply to Kaler. J Clin Invest. 2026;136(4):e202684. PMID 41697743.",
]
for i, r in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.75)
    run = p.add_run(f"{i}. {r}")
    font(run, size=8.5)

doc.save(OUT)
print("saved", OUT)
