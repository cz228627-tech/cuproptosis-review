# -*- coding: utf-8 -*-
"""v2 extraction workbook for the normal-vs-tumour IC50 selectivity table."""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule

OUT = r"C:\work\cuproptosis_IC50_template_v2.xlsx"
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF", size=9.5)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ------------------------------------------------ 说明
ws = wb.active
ws.title = "说明"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 4
ws.column_dimensions["B"].width = 112

text = [
    ("T", "正常细胞 vs 肿瘤细胞 IC50 选择性比（SI）提取表  v2.0"),
    ("N", "产出：SI = IC50(正常) / IC50(肿瘤)。SI < 3 视为无治疗窗；SI > 10 视为存在窗口。"),
    ("B", ""),
    ("H", "三条硬标准（缺一不可）"),
    ("N", "① 只收外源补铜条件下的数据。无铜对照的结果反映的是脱靶效应，不是铜载体杀伤。"),
    ("N", "    接受形式：培养基加 CuCl2（记录浓度）、或预络合态（Elesclomol-Cu / DSF-Cu / Cu(DTC)2）。"),
    ("N", "② 优先同篇文献、同批次的成对数据。跨文献硬凑的正常/肿瘤 IC50 只能标 TierC，不进主分析。"),
    ("N", "③ 正常细胞必须分级：T1 = 肝/神经/内皮（临床剂量限制器官）；T2 = 成纤维/正常上皮；T3 = PBMC。"),
    ("B", ""),
    ("H", "两条补充（容易踩坑，但审稿人一定看）"),
    ("N", "④ 排除“伪正常”：HEK293、CHO、COS-7、以及任何另一株肿瘤细胞系，都不能算正常对照。"),
    ("N", "⑤ 记录孵育时间。24 h 与 72 h 的 IC50 不可直接比较；同一行内的正常/肿瘤必须同时间。"),
    ("B", ""),
    ("H", "字段与判读"),
    ("N", "SI_Ratio 列已设为公式（正常 IC50 ÷ 肿瘤 IC50），填完自动计算。"),
    ("N", "条件格式：SI < 3 标红（无窗），3–10 标黄（窄），> 10 标绿（有窗）。"),
    ("N", "汇总页按药物自动统计：配对数、SI 中位数、SI<3 的比例。"),
    ("B", ""),
    ("H", "填表顺序"),
    ("N", "先读 10 篇试水 → 看能凑出几个合格配对 → 再决定是否扩到 30–40 篇。"),
    ("N", "若 10 篇里合格配对 < 5，说明文献里几乎没人做过正常细胞对照，这本身就是结论。"),
]

r = 1
for kind, s in text:
    c = ws.cell(row=r, column=2, value=s)
    if kind == "T":
        c.font = Font(bold=True, size=15, color="1F3864")
    elif kind == "H":
        c.font = Font(bold=True, size=11, color="1F3864")
    else:
        c.font = Font(size=9.5, color="404040")
    c.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1

# ------------------------------------------------ 提取表
ws2 = wb.create_sheet("提取表")
ws2.sheet_view.showGridLines = False

cols = [
    ("Study_ID", 13), ("Agent", 17), ("Cu_Condition", 20), ("Assay_Time_h", 10),
    ("Assay", 12), ("Normal_Cell", 15), ("Normal_Tier", 16), ("Normal_Primary", 11),
    ("Normal_IC50_uM", 12), ("Tumor_Cell", 14), ("Tumor_IC50_uM", 12),
    ("SI_Ratio", 10), ("Comparability", 11), ("Notes", 34),
]
for i, (h, w) in enumerate(cols, 1):
    c = ws2.cell(row=1, column=i, value=h)
    c.font = HDR_FONT
    c.fill = HDR_FILL
    c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
    c.border = BORDER
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.row_dimensions[1].height = 34
ws2.freeze_panes = "A2"
ws2.auto_filter.ref = f"A1:{get_column_letter(len(cols))}1"

for row in range(2, 402):
    ws2.cell(row=row, column=12).value = (
        f'=IF(AND(ISNUMBER(I{row}),ISNUMBER(K{row}),K{row}>0),ROUND(I{row}/K{row},2),"")'
    )

dvs = [
    ("B", '"Elesclomol,Elesclomol-Cu,DSF-Cu,NSC319726,铜配合物,纳米铜,其他"'),
    ("E", '"MTT,CCK-8,SRB,CellTiter-Glo,流式凋亡,克隆形成,其他"'),
    ("G", '"T1 肝/神经/内皮,T2 成纤维/上皮,T3 PBMC"'),
    ("H", '"是,否,未说明"'),
    ("M", '"A 同文献同批次,B 同文献不同批次,C 跨文献"'),
]
for col, formula in dvs:
    dv = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
    ws2.add_data_validation(dv)
    dv.add(f"{col}2:{col}401")

ws2.conditional_formatting.add("L2:L401", CellIsRule(operator="lessThan", formula=["3"],
                                                     fill=PatternFill("solid", fgColor="F8CBAD")))
ws2.conditional_formatting.add("L2:L401", CellIsRule(operator="between", formula=["3", "10"],
                                                     fill=PatternFill("solid", fgColor="FFE699")))
ws2.conditional_formatting.add("L2:L401", CellIsRule(operator="greaterThan", formula=["10"],
                                                     fill=PatternFill("solid", fgColor="C6E0B4")))

# ------------------------------------------------ 纳入排除
ws3 = wb.create_sheet("纳入排除")
ws3.sheet_view.showGridLines = False
h3 = [("Study_ID", 13), ("第一作者", 14), ("年份", 7), ("PMID/DOI", 18),
      ("有正常细胞对照", 12), ("有补铜条件", 11), ("有定量终点", 11), ("判定", 9), ("排除理由", 44)]
for i, (h, w) in enumerate(h3, 1):
    c = ws3.cell(row=1, column=i, value=h)
    c.font = HDR_FONT
    c.fill = HDR_FILL
    c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
    c.border = BORDER
    ws3.column_dimensions[get_column_letter(i)].width = w
ws3.freeze_panes = "A2"
for col, f in [("E", '"是,否"'), ("F", '"是,否,未说明"'), ("G", '"是,否"'), ("H", '"纳入,排除,待定"')]:
    dv = DataValidation(type="list", formula1=f, allow_blank=True)
    ws3.add_data_validation(dv)
    dv.add(f"{col}2:{col}401")

# ------------------------------------------------ 汇总
ws4 = wb.create_sheet("汇总")
ws4.sheet_view.showGridLines = False
ws4["A1"] = "按药物汇总（公式随提取表更新；中位数请在 R/pandas 中计算）"
ws4["A1"].font = Font(bold=True, size=12, color="1F3864")
for i, h in enumerate(["Agent", "合格配对数", "SI 中位数*", "SI < 3 比例*", "SI > 10 计数"], 1):
    c = ws4.cell(row=3, column=i, value=h)
    c.font = HDR_FONT
    c.fill = HDR_FILL
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = BORDER
    ws4.column_dimensions[get_column_letter(i)].width = 22 if i == 1 else 16

agents = ["Elesclomol", "Elesclomol-Cu", "DSF-Cu", "NSC319726", "铜配合物", "纳米铜", "其他"]
for i, a in enumerate(agents, 4):
    ws4.cell(row=i, column=1, value=a).font = Font(size=9.5)
    ws4.cell(row=i, column=2).value = (
        f'=COUNTIFS(提取表!$B$2:$B$401,$A{i},提取表!$L$2:$L$401,">0")'
    )
    ws4.cell(row=i, column=5).value = (
        f'=COUNTIFS(提取表!$B$2:$B$401,$A{i},提取表!$L$2:$L$401,">10")'
    )
    for col in range(1, 6):
        ws4.cell(row=i, column=col).border = BORDER

ws4.cell(row=len(agents) + 5, column=1,
         value="* 中位数与比例需在主分析时用 R/pandas 计算，避免 Excel 数组公式").font = Font(size=8.5, color="808080")

wb.save(OUT)
print("saved", OUT)
