from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from backend.models.schemas import Report
from backend.utils.config import settings


def export_report_pdf(report: Report) -> str:
    Path(settings.reports_dir).mkdir(parents=True, exist_ok=True)
    path = Path(settings.reports_dir) / f"{report.id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="RMTitle", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#111827")))
    styles.add(ParagraphStyle(name="RMHeading", parent=styles["Heading2"], fontSize=15, textColor=colors.HexColor("#2563eb")))
    story = [Paragraph(escape(report.title), styles["RMTitle"]), Spacer(1, 0.25 * inch)]
    story.append(Paragraph("Table of Contents", styles["RMHeading"]))
    for item in report.table_of_contents:
        story.append(Paragraph(escape(item), styles["BodyText"]))
    story.append(PageBreak())
    for title, body in report.sections.items():
        story.append(Paragraph(escape(title), styles["RMHeading"]))
        for paragraph in body.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(escape(paragraph.strip()), styles["BodyText"]))
                story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Conclusion", styles["RMHeading"]))
    story.append(Paragraph(escape(report.conclusion), styles["BodyText"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("References", styles["RMHeading"]))
    for citation in report.references:
        story.append(Paragraph(escape(citation.text), styles["BodyText"]))
    doc.build(story)
    return str(path)
