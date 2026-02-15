"""
Fluir — Servico de Exportacao (Excel + PPT)
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt, Inches

from copsoq_data import DIMENSIONS


# ──────── Color helpers ────────
FILL_GREEN = PatternFill(start_color="D5F5E3", end_color="D5F5E3", fill_type="solid")
FILL_YELLOW = PatternFill(start_color="FEF9E7", end_color="FEF9E7", fill_type="solid")
FILL_RED = PatternFill(start_color="FADBD8", end_color="FADBD8", fill_type="solid")
FILL_HEADER = PatternFill(start_color="0F4C75", end_color="0F4C75", fill_type="solid")
FILL_SUBHEADER = PatternFill(start_color="3282B8", end_color="3282B8", fill_type="solid")
WHITE_FONT = Font(name="Inter", size=11, bold=True, color="FFFFFF")
NORMAL_FONT = Font(name="Inter", size=10, color="2C3E50")
BOLD_FONT = Font(name="Inter", size=10, bold=True, color="2C3E50")
THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)

STATUS_FILL = {"green": FILL_GREEN, "yellow": FILL_YELLOW, "red": FILL_RED}
STATUS_LABEL = {"green": "Favorável", "yellow": "Atenção", "red": "Crítico"}
PRIORITY_LABEL = {"imediata": "Ação Imediata", "curto": "Curto Prazo", "medio": "Médio Prazo"}

# Formato 16:9 (widescreen)
SLIDE_WIDTH_16_9 = Inches(13.333)
SLIDE_HEIGHT_16_9 = Inches(7.5)
LOGO_SIZE_INCHES = 1.0
IMG_DIR = Path(__file__).resolve().parent / "static" / "img"

# Limites de truncamento para export
MAX_DIM_DESC_LEN = 50
MAX_REC_DESC_LEN = 80
MAX_PROSE_LEN = 2000


# ══════════════════════════════════════════════
# EXCEL EXPORT
# ══════════════════════════════════════════════

def export_excel(
    survey: Dict[str, Any],
    respondents_data: List[Dict[str, Any]],
    dim_scores_agg: List[Dict[str, Any]],
    kpis: Dict[str, Any],
    summary: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
) -> io.BytesIO:
    """Gera Excel completo e retorna BytesIO."""
    wb = Workbook()
    CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
    LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # ─── Aba 1: Resumo Executivo ───
    ws = wb.active
    ws.title = "Resumo Executivo"
    ws.sheet_properties.tabColor = "0F4C75"
    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 40

    # Header
    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = f"Fluir — Relatório de Diagnóstico Psicossocial"
    c.font = Font(name="Inter", size=18, bold=True, color="FFFFFF")
    c.fill = FILL_HEADER
    c.alignment = CENTER
    ws.row_dimensions[1].height = 50

    ws.merge_cells("A2:F2")
    c = ws["A2"]
    c.value = f"{survey.get('company_name', '')} | {datetime.now().strftime('%d/%m/%Y')} | {summary.get('total', 0)} respondentes"
    c.font = Font(name="Inter", size=11, color="FFFFFF")
    c.fill = FILL_SUBHEADER
    c.alignment = CENTER
    ws.row_dimensions[2].height = 30

    # KPIs
    row = 4
    ws.merge_cells(f"A{row}:F{row}")
    ws[f"A{row}"].value = "INDICADORES-CHAVE (KPIs)"
    ws[f"A{row}"].font = Font(name="Inter", size=13, bold=True, color="FFFFFF")
    ws[f"A{row}"].fill = FILL_HEADER
    ws[f"A{row}"].alignment = CENTER

    row = 5
    for key, kpi in kpis.items():
        row += 1
        ws[f"B{row}"] = kpi["label"]
        ws[f"B{row}"].font = BOLD_FONT
        ws[f"C{row}"] = kpi["value"]
        ws[f"C{row}"].font = BOLD_FONT
        ws[f"C{row}"].alignment = CENTER
        ws[f"C{row}"].number_format = "0.00"
        ws[f"D{row}"] = kpi["status"]
        ws[f"D{row}"].alignment = CENTER
        ws[f"D{row}"].fill = STATUS_FILL.get(kpi["color"], FILL_YELLOW)
        for col in "BCDEF":
            ws[f"{col}{row}"].border = THIN_BORDER

    # Summary counts
    row += 2
    ws.merge_cells(f"A{row}:F{row}")
    ws[f"A{row}"].value = "RESUMO GERAL"
    ws[f"A{row}"].font = Font(name="Inter", size=13, bold=True, color="FFFFFF")
    ws[f"A{row}"].fill = FILL_HEADER
    ws[f"A{row}"].alignment = CENTER

    row += 1
    for label, count, color in [
        ("Dimensões Favoráveis", summary["green"], "27AE60"),
        ("Dimensões em Atenção", summary["yellow"], "F39C12"),
        ("Dimensões Críticas", summary["red"], "E74C3C"),
    ]:
        ws[f"B{row}"] = label
        ws[f"B{row}"].font = Font(name="Inter", size=11, bold=True, color=color)
        ws[f"C{row}"] = count
        ws[f"C{row}"].font = Font(name="Inter", size=14, bold=True, color=color)
        ws[f"C{row}"].alignment = CENTER
        row += 1

    # ─── Aba 2: Dimensões ───
    ws2 = wb.create_sheet("Dimensões")
    ws2.sheet_properties.tabColor = "3282B8"
    ws2.column_dimensions["A"].width = 5
    ws2.column_dimensions["B"].width = 35
    ws2.column_dimensions["C"].width = 12
    ws2.column_dimensions["D"].width = 14
    ws2.column_dimensions["E"].width = 12
    ws2.column_dimensions["F"].width = 28
    ws2.column_dimensions["G"].width = 35

    headers = ["#", "Dimensão", "Score", "Status", "Tipo", "Categoria", "Descrição"]
    for i, h in enumerate(headers, 1):
        c = ws2.cell(row=1, column=i, value=h)
        c.font = WHITE_FONT
        c.fill = FILL_HEADER
        c.alignment = CENTER

    for idx, d in enumerate(dim_scores_agg, 1):
        r = idx + 1
        ws2.cell(row=r, column=1, value=idx).alignment = CENTER
        ws2.cell(row=r, column=2, value=d["name"]).font = NORMAL_FONT
        ws2.cell(row=r, column=3, value=d["score"]).alignment = CENTER
        ws2.cell(row=r, column=3).number_format = "0.00"
        ws2.cell(row=r, column=4, value=STATUS_LABEL.get(d["status"], "")).alignment = CENTER
        ws2.cell(row=r, column=4).fill = STATUS_FILL.get(d["status"], FILL_YELLOW)
        ws2.cell(row=r, column=5, value="Risco" if d["type"] == "risk" else "Recurso").alignment = CENTER
        ws2.cell(row=r, column=6, value=d["category"])
        ws2.cell(row=r, column=7, value=d["description"])
        for col in range(1, 8):
            ws2.cell(row=r, column=col).border = THIN_BORDER

    # ─── Aba 3: Respostas Individuais ───
    ws3 = wb.create_sheet("Respostas Individuais")
    ws3.sheet_properties.tabColor = "27AE60"

    ws3.cell(row=1, column=1, value="ID").font = WHITE_FONT
    ws3.cell(row=1, column=1).fill = FILL_HEADER
    ws3.cell(row=1, column=1).alignment = CENTER
    ws3.column_dimensions["A"].width = 12

    dim_ids = list(DIMENSIONS.keys())
    for i, dim_id in enumerate(dim_ids, 2):
        c = ws3.cell(row=1, column=i, value=DIMENSIONS[dim_id]["name"])
        c.font = Font(name="Inter", size=9, bold=True, color="FFFFFF")
        c.fill = FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True, text_rotation=90)
        ws3.column_dimensions[get_column_letter(i)].width = 6

    for r_idx, resp in enumerate(respondents_data, 2):
        ws3.cell(row=r_idx, column=1, value=resp["display_id"]).alignment = CENTER
        for i, dim_id in enumerate(dim_ids, 2):
            score = resp.get("scores", {}).get(dim_id)
            if score is not None:
                cell = ws3.cell(row=r_idx, column=i, value=score)
                cell.alignment = CENTER
                cell.number_format = "0.00"
                status = resp.get("statuses", {}).get(dim_id, "yellow")
                cell.fill = STATUS_FILL.get(status, FILL_YELLOW)
                cell.border = THIN_BORDER

    # ─── Aba 4: Recomendações ───
    ws4 = wb.create_sheet("Recomendações")
    ws4.sheet_properties.tabColor = "7C83FD"
    ws4.column_dimensions["A"].width = 5
    ws4.column_dimensions["B"].width = 18
    ws4.column_dimensions["C"].width = 45
    ws4.column_dimensions["D"].width = 60

    for i, h in enumerate(["#", "Prioridade", "Título", "Descrição"], 1):
        c = ws4.cell(row=1, column=i, value=h)
        c.font = WHITE_FONT
        c.fill = FILL_HEADER
        c.alignment = CENTER

    for idx, rec in enumerate(recommendations, 1):
        r = idx + 1
        ws4.cell(row=r, column=1, value=idx).alignment = CENTER
        ws4.cell(row=r, column=2, value=PRIORITY_LABEL.get(rec.get("priority", ""), rec.get("priority", ""))).alignment = CENTER
        ws4.cell(row=r, column=3, value=rec.get("title", ""))
        ws4.cell(row=r, column=4, value=rec.get("description", ""))
        for col in range(1, 5):
            ws4.cell(row=r, column=col).border = THIN_BORDER
            ws4.cell(row=r, column=col).alignment = Alignment(vertical="center", wrap_text=True)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════
# PPT EXPORT
# ══════════════════════════════════════════════

def _add_title_slide(prs: Presentation, company: str, date: str, total_respondents: int = 0) -> None:
    """Adiciona slide de capa com wallpaper, logo e textos."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    w = prs.slide_width
    h = prs.slide_height
    wallpaper_path = IMG_DIR / "wallpaper_PPT.png"
    logo_path = IMG_DIR / "fluir_logo.png"
    if wallpaper_path.exists():
        slide.shapes.add_picture(str(wallpaper_path), 0, 0, w, h)
    if logo_path.exists():
        logo_size = Inches(LOGO_SIZE_INCHES)
        logo_left = Inches(13.333 - LOGO_SIZE_INCHES)
        slide.shapes.add_picture(str(logo_path), logo_left, Inches(0.2), logo_size, logo_size)
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1))
    t = title_box.text_frame.paragraphs[0]
    t.text = "Fluir"
    t.font.size = Pt(44)
    t.font.bold = True
    t.font.color.rgb = RGBColor(0x0F, 0x4C, 0x75)
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(2.7), Inches(9), Inches(1))
    p = tb.text_frame.paragraphs[0]
    p.text = "Relatorio de Diagnostico Psicossocial"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(0x32, 0x82, 0xB8)
    tb2 = slide.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(9), Inches(1))
    resp_text = f" | {total_respondents} respondentes" if total_respondents else ""
    tb2.text_frame.paragraphs[0].text = f"Organizacao: {company}  |  Data: {date}{resp_text}"
    tb2.text_frame.paragraphs[0].font.size = Pt(14)


def _add_table_slide(
    prs: Presentation, title_text: str, headers: List[str], rows: List[List[Any]]
) -> None:
    """Adiciona slide com tabela (formato 16:9)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    left = Inches(0.5)
    top = Inches(1)
    width = Inches(12)
    height = Inches(1)
    title_box = slide.shapes.add_textbox(left, Inches(0.3), width, Inches(0.6))
    title_box.text_frame.paragraphs[0].text = title_text
    title_box.text_frame.paragraphs[0].font.size = Pt(24)
    title_box.text_frame.paragraphs[0].font.bold = True
    n_cols = len(headers)
    n_rows = len(rows) + 1
    table_height = Inches(0.35 * min(n_rows, 12))
    table = slide.shapes.add_table(n_rows, n_cols, left, top, width, table_height).table
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = str(h)
        cell.text_frame.paragraphs[0].font.bold = True
    for r_idx, row in enumerate(rows, 1):
        for c_idx, val in enumerate(row):
            if c_idx < n_cols:
                table.cell(r_idx, c_idx).text = str(val)


def export_pptx(
    survey: Dict[str, Any],
    respondents_data: List[Dict[str, Any]],
    dim_scores_agg: List[Dict[str, Any]],
    kpis: Dict[str, Any],
    summary: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    recommendations_prose: Dict[str, str],
) -> io.BytesIO:
    """Gera apresentacao PowerPoint executiva e retorna BytesIO.

    Conteudo completo: capa, KPIs, resumo, dimensoes, respostas individuais,
    recomendacoes estruturadas, recomendacoes em prosa (IA), rodape.
    Formato 16:9. Capa com wallpaper e logo.
    """
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH_16_9
    prs.slide_height = SLIDE_HEIGHT_16_9

    company = survey.get("company_name", "Empresa")
    date_str = datetime.now().strftime("%d/%m/%Y")
    total_resp = summary.get("total", 0) or len(respondents_data)
    _add_title_slide(prs, company, date_str, total_resp)

    kpi_headers = ["Indicador", "Valor", "Status"]
    kpi_rows = [[kpi["label"], f"{kpi['value']:.2f}", kpi["status"]] for kpi in kpis.values()]
    _add_table_slide(prs, "Indicadores-Chave (KPIs)", kpi_headers, kpi_rows)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(0.5), Inches(1), Inches(12), Inches(1.5))
    p = box.text_frame.paragraphs[0]
    p.text = f"Resumo: {summary.get('green', 0)} favoraveis | {summary.get('yellow', 0)} atencao | {summary.get('red', 0)} criticas"
    p.font.size = Pt(18)

    dim_headers = ["#", "Dimensao", "Score", "Status", "Tipo", "Categoria", "Descricao"]
    dim_rows = [
        [idx, d["name"], f"{d['score']:.2f}", STATUS_LABEL.get(d["status"], ""),
         "Risco" if d["type"] == "risk" else "Recurso", d["category"], (d.get("description") or "")[:MAX_DIM_DESC_LEN]]
        for idx, d in enumerate(dim_scores_agg, 1)
    ]
    _add_table_slide(prs, "Analise por Dimensao", dim_headers, dim_rows)

    if respondents_data and DIMENSIONS:
        dim_ids = list(DIMENSIONS.keys())
        resp_headers = ["ID"] + [DIMENSIONS[d]["name"][:8] for d in dim_ids]
        resp_rows = []
        for r in respondents_data:
            row = [r.get("display_id", "")]
            for dim_id in dim_ids:
                s = r.get("scores", {}).get(dim_id)
                row.append(f"{s:.2f}" if s is not None else "-")
            resp_rows.append(row)
        if resp_rows:
            _add_table_slide(prs, "Respostas Individuais", resp_headers, resp_rows)

    if recommendations:
        rec_headers = ["#", "Prioridade", "Titulo", "Descricao"]
        rec_rows = [
            [idx, PRIORITY_LABEL.get(r.get("priority", ""), r.get("priority", "")), r.get("title", ""), (r.get("description") or "")[:MAX_REC_DESC_LEN]]
            for idx, r in enumerate(recommendations, 1)
        ]
        _add_table_slide(prs, "Recomendacoes Estruturadas", rec_headers, rec_rows)

    sections = [("Acoes imediatas", "imediata"), ("Curto prazo", "curto_prazo"), ("Medio prazo", "medio_prazo")]
    for title, key in sections:
        text = (recommendations_prose or {}).get(key) or ""
        if text.strip():
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            tit_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.7))
            tit_box.text_frame.paragraphs[0].text = title
            tit_box.text_frame.paragraphs[0].font.size = Pt(24)
            tit_box.text_frame.paragraphs[0].font.bold = True
            tx = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(12), Inches(5))
            tx.text_frame.word_wrap = True
            tx.text_frame.paragraphs[0].text = text.strip()[:MAX_PROSE_LEN]
            tx.text_frame.paragraphs[0].font.size = Pt(12)

    footer_slide = prs.slides.add_slide(prs.slide_layouts[6])
    fb = footer_slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(12), Inches(2))
    fb.text_frame.paragraphs[0].text = "Fluir — Bem-estar que move resultados. COPSOQ II. Documento confidencial."
    fb.text_frame.paragraphs[0].font.size = Pt(14)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf
