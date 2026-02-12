"""
Fluir — Serviço de Exportação (PDF + Excel)
"""

import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

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


# ══════════════════════════════════════════════
# EXCEL EXPORT
# ══════════════════════════════════════════════

def export_excel(survey, respondents_data, dim_scores_agg, kpis, summary, recommendations) -> io.BytesIO:
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
# PDF EXPORT
# ══════════════════════════════════════════════

def export_pdf(survey, dim_scores_agg, kpis, summary, recommendations_prose) -> io.BytesIO:
    """Gera PDF executivo e retorna BytesIO.

    A secao de recomendacoes utiliza texto corrido consultivo, organizado por prazo:
    - imediata
    - curto_prazo
    - medio_prazo
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("FluirTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, textColor=colors.HexColor("#0F4C75"), spaceAfter=6))
    styles.add(ParagraphStyle("FluirSubtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=12, textColor=colors.HexColor("#3282B8"), spaceAfter=12))
    styles.add(ParagraphStyle("FluirSection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, textColor=colors.HexColor("#0F4C75"), spaceBefore=16, spaceAfter=8))
    styles.add(ParagraphStyle("FluirBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#2C3E50"), spaceAfter=4, leading=14))
    styles.add(ParagraphStyle("FluirSmall", parent=styles["Normal"], fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#7F8C8D")))

    story = []

    # Title
    story.append(Paragraph("Fluir", styles["FluirTitle"]))
    story.append(Paragraph("Relatório de Diagnóstico Psicossocial", styles["FluirSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0F4C75"), spaceAfter=12))

    company = survey.get("company_name", "Empresa")
    date = datetime.now().strftime("%d/%m/%Y")
    story.append(Paragraph(f"<b>Organização:</b> {company} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Data:</b> {date}", styles["FluirBody"]))
    story.append(Spacer(1, 12))

    # KPIs
    story.append(Paragraph("Indicadores-Chave de Desempenho (KPIs)", styles["FluirSection"]))

    kpi_data = [["Indicador", "Valor", "Status"]]
    kpi_colors_map = {"green": colors.HexColor("#27AE60"), "yellow": colors.HexColor("#F39C12"), "red": colors.HexColor("#E74C3C")}
    kpi_row_colors = []
    for key, kpi in kpis.items():
        kpi_data.append([kpi["label"], f"{kpi['value']:.2f}", kpi["status"]])
        kpi_row_colors.append(kpi.get("color", "yellow"))

    kpi_table = Table(kpi_data, colWidths=[200, 80, 100])
    kpi_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C75")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWHEIGHTS", (0, 0), (-1, -1), 28),
    ]
    for i, c in enumerate(kpi_row_colors):
        kpi_style.append(("BACKGROUND", (2, i + 1), (2, i + 1), kpi_colors_map.get(c, colors.white)))
        kpi_style.append(("TEXTCOLOR", (2, i + 1), (2, i + 1), colors.white))
    kpi_table.setStyle(TableStyle(kpi_style))
    story.append(kpi_table)
    story.append(Spacer(1, 16))

    # Summary
    story.append(Paragraph("Resumo Geral", styles["FluirSection"]))
    story.append(Paragraph(f"• <font color='#27AE60'><b>{summary['green']}</b></font> dimensões favoráveis &nbsp;&nbsp; • <font color='#F39C12'><b>{summary['yellow']}</b></font> em atenção &nbsp;&nbsp; • <font color='#E74C3C'><b>{summary['red']}</b></font> críticas", styles["FluirBody"]))
    story.append(Spacer(1, 8))

    # Dimensions table
    story.append(Paragraph("Análise por Dimensão", styles["FluirSection"]))

    dim_data = [["Dimensão", "Score", "Status", "Tipo", "Categoria"]]
    dim_row_colors = []
    for d in dim_scores_agg:
        dim_data.append([d["name"], f"{d['score']:.2f}", STATUS_LABEL.get(d["status"], ""), "Risco" if d["type"] == "risk" else "Recurso", d["category"]])
        dim_row_colors.append(d["status"])

    dim_table = Table(dim_data, colWidths=[140, 50, 70, 55, 140])
    dim_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C75")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (3, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWHEIGHTS", (0, 0), (-1, -1), 20),
    ]
    for i, c in enumerate(dim_row_colors):
        dim_style.append(("BACKGROUND", (2, i + 1), (2, i + 1), kpi_colors_map.get(c, colors.white)))
        if c in ("green", "red"):
            dim_style.append(("TEXTCOLOR", (2, i + 1), (2, i + 1), colors.white))
    dim_table.setStyle(TableStyle(dim_style))
    story.append(dim_table)

    # Recommendations em texto corrido (IA)
    if recommendations_prose:
        has_any_text = any(
            bool((recommendations_prose.get(key) or "").strip())
            for key in ("imediata", "curto_prazo", "medio_prazo")
        )
        if has_any_text:
            story.append(PageBreak())
            story.append(Paragraph("Análise e Recomendações (IA)", styles["FluirSection"]))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3282B8"), spaceAfter=8))

            sections = [
                ("Ações de aplicação imediata", "imediata"),
                ("Ações de curto prazo", "curto_prazo"),
                ("Ações de médio prazo", "medio_prazo"),
            ]
            for title, key in sections:
                text = (recommendations_prose.get(key) or "").strip()
                if not text:
                    continue
                story.append(Paragraph(f"<b>{title}</b>", styles["FluirBody"]))
                story.append(Paragraph(text, styles["FluirBody"]))
                story.append(Spacer(1, 8))

    # Footer
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=6))
    story.append(Paragraph("Relatório gerado pela plataforma <b>Fluir</b> — Bem-estar que move resultados", styles["FluirSmall"]))
    story.append(Paragraph("Metodologia: COPSOQ II (Copenhagen Psychosocial Questionnaire) — Versão Curta Portuguesa", styles["FluirSmall"]))
    story.append(Paragraph("Documento confidencial — Uso exclusivo para fins de consultoria organizacional", styles["FluirSmall"]))

    doc.build(story)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════
# DOCX EXPORT
# ══════════════════════════════════════════════

def export_docx(survey, dim_scores_agg, kpis, summary, recommendations_prose) -> io.BytesIO:
    """Gera relatorio em Word (.docx) com texto corrido de IA.

    O foco e fornecer um documento editavel, em formato de apresentacao profissional,
    com os principais blocos:
    - capa com empresa e data
    - resumo de KPIs
    - tabela de dimensoes
    - analise e recomendacoes (IA) por prazo
    """
    try:
        from docx import Document  # type: ignore
        from docx.shared import Pt
    except ImportError:
        # Deixamos o erro claro para quem estiver rodando o backend.
        raise RuntimeError("Dependencia 'python-docx' nao encontrada. Instale com: pip install python-docx")

    doc = Document()

    company = survey.get("company_name", "Empresa")
    date = datetime.now().strftime("%d/%m/%Y")

    # Estilos basicos
    style_title = doc.styles["Title"]
    style_title.font.name = "Calibri"
    style_title.font.size = Pt(24)
    style_title.font.bold = True

    # Capa
    doc.add_heading("Fluir — Relatório de Diagnóstico Psicossocial", level=0)
    p = doc.add_paragraph()
    run = p.add_run(f"Organização: {company}\nData: {date}")
    run.font.size = Pt(12)
    doc.add_paragraph()

    # KPIs
    doc.add_heading("Indicadores-Chave (KPIs)", level=1)
    if kpis:
        table = doc.add_table(rows=1, cols=3)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Indicador"
        hdr_cells[1].text = "Valor"
        hdr_cells[2].text = "Status"
        for kpi in kpis.values():
            row_cells = table.add_row().cells
            row_cells[0].text = str(kpi.get("label", ""))
            row_cells[1].text = f"{kpi.get('value', 0):.2f}"
            row_cells[2].text = str(kpi.get("status", ""))
    else:
        doc.add_paragraph("Nenhum indicador calculado até o momento.")

    doc.add_paragraph()

    # Resumo simples
    doc.add_heading("Resumo Geral", level=1)
    doc.add_paragraph(
        f"Dimensões favoráveis: {summary.get('green', 0)} | "
        f"em atenção: {summary.get('yellow', 0)} | "
        f"críticas: {summary.get('red', 0)}"
    )

    doc.add_paragraph()

    # Tabela de dimensoes
    doc.add_heading("Análise por Dimensão", level=1)
    if dim_scores_agg:
        table = doc.add_table(rows=1, cols=5)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Dimensão"
        hdr_cells[1].text = "Score"
        hdr_cells[2].text = "Status"
        hdr_cells[3].text = "Tipo"
        hdr_cells[4].text = "Categoria"
        for d in dim_scores_agg:
            row = table.add_row().cells
            row[0].text = str(d.get("name", ""))
            row[1].text = f"{d.get('score', 0):.2f}"
            row[2].text = STATUS_LABEL.get(d.get("status", ""), "")
            row[3].text = "Risco" if d.get("type") == "risk" else "Recurso"
            row[4].text = str(d.get("category", ""))
    else:
        doc.add_paragraph("Ainda não há dados suficientes para análise das dimensões.")

    doc.add_page_break()

    # Analise e recomendacoes em texto corrido (IA)
    doc.add_heading("Análise e Recomendações (IA)", level=1)
    if recommendations_prose:
        sections = [
            ("Ações de aplicação imediata", "imediata"),
            ("Ações de curto prazo", "curto_prazo"),
            ("Ações de médio prazo", "medio_prazo"),
        ]
        any_text = False
        for title, key in sections:
            text = (recommendations_prose.get(key) or "").strip()
            if not text:
                continue
            any_text = True
            doc.add_heading(title, level=2)
            doc.add_paragraph(text)

        if not any_text:
            doc.add_paragraph("Nenhuma recomendação de IA disponível no momento.")
    else:
        doc.add_paragraph("Nenhuma recomendação de IA disponível no momento.")

    # Rodape simples
    doc.add_paragraph()
    doc.add_paragraph(
        "Relatório gerado pela plataforma Fluir — Bem-estar que move resultados. "
        "Documento confidencial, de uso exclusivo para fins de consultoria organizacional."
    )

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
