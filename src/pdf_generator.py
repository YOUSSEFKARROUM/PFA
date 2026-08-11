"""
pdf_generator.py — Génération des rapports PDF d'audit (ReportLab).
"""
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

# ===== CMRPI branding =====
NAVY = colors.HexColor("#1B2A4A")
TEAL = colors.HexColor("#0E7C7B")
GOLD = colors.HexColor("#B08D57")
LIGHTGRAY = colors.HexColor("#F2F2F2")
WHITE = colors.white

DOMAIN_LABELS_FR = {
    "dom_gov": "Gouvernance",
    "dom_acc": "Accès & Identités",
    "dom_infra": "Infrastructure & Réseau",
    "dom_inc": "Incidents & Continuité",
    "dom_sens": "Sensibilisation & Formation",
}


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CMRPITitle", fontSize=19, textColor=NAVY, spaceBefore=8, spaceAfter=10,
        alignment=TA_CENTER, fontName="Helvetica-Bold", leading=23))
    styles.add(ParagraphStyle(
        name="CMRPISubtitle", fontSize=11, textColor=colors.HexColor("#595959"),
        alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Oblique"))
    styles.add(ParagraphStyle(
        name="CMRPIH2", fontSize=14, textColor=TEAL, spaceBefore=16,
        spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(
        name="CMRPIBody", fontSize=10, textColor=colors.HexColor("#1A1A1A"),
        spaceAfter=8, alignment=TA_LEFT, leading=14))
    styles.add(ParagraphStyle(name="CMRPISmall", fontSize=8, textColor=colors.HexColor("#595959")))
    return styles


def _score_color(score: float):
    if score < 25:
        return colors.HexColor("#C0392B")
    elif score < 50:
        return colors.HexColor("#D68910")
    elif score < 75:
        return colors.HexColor("#B7950B")
    return colors.HexColor("#1E8449")


def _domain_bar_chart(domain_scores: dict):
    drawing = Drawing(420, 200)
    chart = VerticalBarChart()
    chart.x = 40
    chart.y = 20
    chart.width = 350
    chart.height = 150
    labels = [DOMAIN_LABELS_FR.get(d, d) for d in domain_scores.keys()]
    values = list(domain_scores.values())
    chart.data = [values]
    chart.categoryAxis.categoryNames = [name.replace(" & ", " &\n") for name in labels]
    chart.categoryAxis.labels.fontSize = 6
    chart.categoryAxis.labels.dy = -6
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 25
    chart.bars[0].fillColor = TEAL
    drawing.add(chart)
    return drawing


def _gauge(score: float):
    """Jauge simple sous forme de barre horizontale colorée."""
    drawing = Drawing(400, 60)
    drawing.add(Rect(0, 20, 400, 20, fillColor=LIGHTGRAY, strokeColor=None))
    fill_width = 4 * score
    drawing.add(Rect(0, 20, fill_width, 20, fillColor=_score_color(score), strokeColor=None))
    drawing.add(String(
        200, 45, f"{score}%", textAnchor="middle", fontSize=16,
        fillColor=NAVY, fontName="Helvetica-Bold"))
    return drawing


def generate_audit_report(
    pme_name: str,
    sector: str,
    audit_date: str,
    domain_scores: dict,
    global_score: float,
    maturity_level: str,
    recommendations: dict,
    output_path: str = None,
) -> bytes:
    """
    Génère le rapport PDF d'audit complet.

    domain_scores: {domain_id: score}
    recommendations: {domain_id: [ {text_fr, severity, ...}, ... ]}
    returns: bytes du PDF (et l'écrit dans output_path si fourni)
    """
    styles = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        output_path if output_path else buffer,
        pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
    )
    story = []

    # ---- Header ----
    story.append(Paragraph("CMRPI — Espace Maroc Cyberconfiance", styles["CMRPISubtitle"]))
    story.append(Paragraph("Rapport d'Auto-Évaluation de la Maturité Cybersécurité", styles["CMRPITitle"]))
    story.append(Spacer(1, 10))

    info_table = Table(
        [
            ["Organisation", pme_name],
            ["Secteur", sector or "Non spécifié"],
            ["Date de l'audit", audit_date],
        ],
        colWidths=[4 * cm, 10 * cm],
    )
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHTGRAY),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # ---- Global Score ----
    story.append(Paragraph("Score Global de Maturité", styles["CMRPIH2"]))
    story.append(_gauge(global_score))
    story.append(Paragraph(f"Niveau de maturité : <b>{maturity_level}</b>", styles["CMRPIBody"]))
    story.append(Spacer(1, 10))

    # ---- Domain scores chart ----
    story.append(Paragraph("Scores par Domaine", styles["CMRPIH2"]))
    story.append(_domain_bar_chart(domain_scores))
    story.append(Spacer(1, 10))

    domain_table_data = [["Domaine", "Score", "Niveau"]]
    for domain_id, score in domain_scores.items():
        level = "Critique" if score < 25 else "Faible" if score < 50 else "Moyen" if score < 75 else "Avancé"
        domain_table_data.append([DOMAIN_LABELS_FR.get(domain_id, domain_id), f"{score}%", level])
    dt = Table(domain_table_data, colWidths=[8 * cm, 3 * cm, 3 * cm])
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHTGRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(dt)
    story.append(PageBreak())

    # ---- Recommendations ----
    story.append(Paragraph("Recommandations Prioritaires", styles["CMRPIH2"]))
    for domain_id, recs in recommendations.items():
        if not recs:
            continue
        story.append(Paragraph(f"<b>{DOMAIN_LABELS_FR.get(domain_id, domain_id)}</b>", styles["CMRPIBody"]))
        for rec in recs:
            severity = rec.get("severity", "")
            text = rec.get("text_fr", "")
            story.append(Paragraph(f"• [{severity}] {text}", styles["CMRPIBody"]))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"Document généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — "
        f"Plateforme CMRPI d'auto-évaluation cybersécurité. Confidentiel.",
        styles["CMRPISmall"],
    ))

    doc.build(story)

    if output_path:
        with open(output_path, "rb") as f:
            return f.read()
    return buffer.getvalue()
