# ============================================================
# NexRay AI - Report Generator
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from datetime import datetime
import os

REPORTS_FOLDER = "uploads/reports"
os.makedirs(REPORTS_FOLDER, exist_ok=True)

NAVY       = colors.HexColor("#1A3C5E")
BLUE       = colors.HexColor("#2E86AB")
LIGHT_BLUE = colors.HexColor("#EAF4FB")
MID_BLUE   = colors.HexColor("#D0E8F5")
RED        = colors.HexColor("#C0392B")
GREEN      = colors.HexColor("#1E8449")
ORANGE     = colors.HexColor("#D35400")
WHITE      = colors.white
DARK       = colors.HexColor("#1C1C1C")
GRAY       = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#F5F5F5")
BORDER     = colors.HexColor("#CCCCCC")
CONFIRMED  = colors.HexColor("#1E8449")
RULED_OUT  = colors.HexColor("#C0392B")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("rTitle",
            fontSize=26, textColor=NAVY, alignment=TA_CENTER,
            fontName="Helvetica-Bold", spaceAfter=2, leading=30),
        "subtitle": ParagraphStyle("rSub",
            fontSize=9, textColor=BLUE, alignment=TA_CENTER,
            fontName="Helvetica", spaceAfter=2, leading=12),
        "date": ParagraphStyle("rDate",
            fontSize=8, textColor=GRAY, alignment=TA_CENTER,
            fontName="Helvetica", spaceAfter=0, leading=11),
        "section": ParagraphStyle("rSection",
            fontSize=10, textColor=WHITE, fontName="Helvetica-Bold",
            spaceBefore=0, spaceAfter=0, leading=13),
        "body": ParagraphStyle("rBody",
            fontSize=9, textColor=DARK, fontName="Helvetica",
            spaceAfter=2, leading=13),
        "bold": ParagraphStyle("rBold",
            fontSize=9, textColor=DARK, fontName="Helvetica-Bold",
            spaceAfter=2, leading=13),
        "small": ParagraphStyle("rSmall",
            fontSize=8, textColor=GRAY, fontName="Helvetica",
            spaceAfter=2, leading=11),
        "confirmed": ParagraphStyle("rConfirmed",
            fontSize=9, textColor=CONFIRMED, fontName="Helvetica-Bold",
            spaceAfter=2, leading=13),
        "ruled_out": ParagraphStyle("rRuledOut",
            fontSize=9, textColor=RULED_OUT, fontName="Helvetica-Bold",
            spaceAfter=2, leading=13),
        "final_diagnosis": ParagraphStyle("rFinal",
            fontSize=10, textColor=NAVY, fontName="Helvetica-Bold",
            spaceAfter=3, leading=14),
        "disclaimer": ParagraphStyle("rDisclaimer",
            fontSize=7, textColor=RED, fontName="Helvetica-Oblique",
            alignment=TA_JUSTIFY, spaceAfter=0, leading=9),
        "urgency_emergency": ParagraphStyle("rUrgE",
            fontSize=9, textColor=RED, fontName="Helvetica-Bold", spaceAfter=2),
        "urgency_urgent": ParagraphStyle("rUrgU",
            fontSize=9, textColor=ORANGE, fontName="Helvetica-Bold", spaceAfter=2),
        "urgency_routine": ParagraphStyle("rUrgR",
            fontSize=9, textColor=GREEN, fontName="Helvetica-Bold", spaceAfter=2),
        "footer": ParagraphStyle("rFooter",
            fontSize=7, textColor=GRAY, alignment=TA_CENTER,
            fontName="Helvetica", spaceAfter=0),
    }


def _bullet(text, style):
    return Paragraph(f"&bull;&nbsp;&nbsp;{text}", style)


def _section_header(title, width, S, color=None):
    bg = color if color else NAVY
    t = Table([[Paragraph(title, S["section"])]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _findings_table(findings, W, S, BORDER, LIGHT_BLUE, WHITE, NAVY):
    tdata = [[
        Paragraph("<b>Possible Condition</b>", S["bold"]),
        Paragraph("<b>Confidence</b>", S["bold"])
    ]]
    for f in findings:
        confidence = f.get("confidence", "—")
        conf_str = f"{confidence}%" if isinstance(confidence, (int, float)) else str(confidence)
        tdata.append([
            Paragraph(f.get("condition", "—"), S["body"]),
            Paragraph(conf_str, S["body"])
        ])
    t = Table(tdata, colWidths=[W * 0.75, W * 0.25])
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1,  0), NAVY),
        ("TEXTCOLOR",      (0, 0), (-1,  0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BLUE, WHITE]),
        ("GRID",           (0, 0), (-1, -1), 0.4, BORDER),
        ("ALIGN",          (1, 0), ( 1, -1), "CENTER"),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
    ]))
    return t


def _get_modules_used(xray_findings, symptom_findings, refined_diagnosis=None):
    modules = []
    if xray_findings:
        modules.append("X-Ray Analysis")
    if symptom_findings:
        modules.append("Symptom Checker")
    if refined_diagnosis:
        modules.append("Refined Diagnosis")
    return "  •  ".join(modules) if modules else "None"


def generate_report(session_id: int, patient_name: str = None,
                    xray_findings: dict = None,
                    symptom_findings: dict = None,
                    refined_diagnosis: dict = None) -> str:

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"nexray_report_{session_id}_{timestamp}.pdf"
    filepath  = os.path.join(REPORTS_FOLDER, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=0.6*inch, leftMargin=0.6*inch,
        topMargin=0.35*inch,  bottomMargin=0.35*inch
    )

    S       = _styles()
    W       = doc.width
    content = []

    # ── HEADER ──
    date_str = datetime.now().strftime("%d %B %Y  |  %I:%M %p")
    content.append(Paragraph("NexRay AI", S["title"]))
    content.append(Paragraph("Medical Assistant Platform  •  Clinical Decision Support Report", S["subtitle"]))
    content.append(Paragraph(date_str, S["date"]))
    content.append(Spacer(1, 4))
    content.append(HRFlowable(width="100%", thickness=2, color=NAVY))
    content.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=4))

    # ── META BAR ──
    modules_used = _get_modules_used(xray_findings, symptom_findings, refined_diagnosis)
    meta_data = [[
        Paragraph(f"<b>Session ID:</b>  {session_id}", S["small"]),
        Paragraph(f"<b>Patient:</b>  {patient_name or 'Not specified'}", S["small"]),
        Paragraph(f"<b>Modules:</b>  {modules_used}", S["small"]),
    ]]
    meta_table = Table(meta_data, colWidths=[W/3, W/3, W/3])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GRAY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE",     (0, 0), (-1,  0), 0.5, BORDER),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.5, BORDER),
    ]))
    content.append(meta_table)
    content.append(Spacer(1, 6))

    # ── X-RAY SECTION ──
    if xray_findings:
        content.append(_section_header("X-Ray Analysis", W, S))
        content.append(Spacer(1, 4))

        region     = xray_findings.get("body_region", xray_findings.get("region", "Unknown")).title()
        # Support both findings and possible_conditions field names
        findings   = xray_findings.get("findings") or xray_findings.get("possible_conditions") or []
        summary    = xray_findings.get("overall_impression") or xray_findings.get("summary") or ""
        tests      = xray_findings.get("recommended_tests", [])
        treatments = xray_findings.get("suggested_treatment", [])
        next_steps = xray_findings.get("next_steps", [])
        urgency    = xray_findings.get("urgency", "")

        content.append(Paragraph(f"<b>Detected Region:</b>  {region}", S["body"]))
        content.append(Spacer(1, 3))

        if findings:
            content.append(_findings_table(findings, W, S, BORDER, LIGHT_BLUE, WHITE, NAVY))
        else:
            content.append(Paragraph("No significant findings detected.", S["body"]))

        if urgency:
            content.append(Spacer(1, 4))
            urgency_map = {
                "Emergency": S["urgency_emergency"],
                "Urgent":    S["urgency_urgent"],
                "Routine":   S["urgency_routine"],
            }
            urgency_label = {
                "Emergency": "🔴  Urgency Level: Emergency — Immediate action required",
                "Urgent":    "🟠  Urgency Level: Urgent — Same day attention required",
                "Routine":   "🟢  Urgency Level: Routine",
            }.get(urgency, f"Urgency Level: {urgency}")
            content.append(Paragraph(urgency_label, urgency_map.get(urgency, S["urgency_routine"])))
            content.append(Spacer(1, 4))

        if tests:
            content.append(Paragraph("Recommended Tests", S["bold"]))
            for test in tests:
                content.append(_bullet(test, S["body"]))
            content.append(Spacer(1, 3))

        if treatments:
            content.append(Paragraph("Suggested Treatment", S["bold"]))
            for treatment in treatments:
                content.append(_bullet(treatment, S["body"]))
            content.append(Spacer(1, 3))

        if next_steps:
            content.append(Paragraph("Next Steps", S["bold"]))
            for step in next_steps:
                content.append(_bullet(step, S["body"]))
            content.append(Spacer(1, 3))

        if summary:
            content.append(Paragraph(f"<i><b>Summary:</b> {summary}</i>", S["small"]))

        content.append(Spacer(1, 6))

    # ── SYMPTOM SECTION ──
    if symptom_findings:
        content.append(_section_header("Symptom Analysis", W, S))
        content.append(Spacer(1, 4))

        # Support both possible_conditions and findings field names
        possible_conditions = symptom_findings.get("possible_conditions") or symptom_findings.get("findings") or []
        tests               = symptom_findings.get("recommended_tests", [])
        treatments          = symptom_findings.get("suggested_treatment", [])
        next_steps          = symptom_findings.get("next_steps", [])
        urgency             = symptom_findings.get("urgency", "Routine")
        summary             = symptom_findings.get("summary", "")

        if possible_conditions:
            content.append(_findings_table(possible_conditions, W, S, BORDER, LIGHT_BLUE, WHITE, NAVY))
            content.append(Spacer(1, 4))

        urgency_map = {
            "Emergency": S["urgency_emergency"],
            "Urgent":    S["urgency_urgent"],
            "Routine":   S["urgency_routine"],
        }
        urgency_label = {
            "Emergency": "🔴  Urgency Level: Emergency — Immediate action required",
            "Urgent":    "🟠  Urgency Level: Urgent — Same day attention required",
            "Routine":   "🟢  Urgency Level: Routine",
        }.get(urgency, f"Urgency Level: {urgency}")
        content.append(Paragraph(urgency_label, urgency_map.get(urgency, S["urgency_routine"])))
        content.append(Spacer(1, 4))

        if tests:
            content.append(Paragraph("Recommended Tests", S["bold"]))
            for test in tests:
                content.append(_bullet(test, S["body"]))
            content.append(Spacer(1, 3))

        if treatments:
            content.append(Paragraph("Suggested Treatment", S["bold"]))
            for treatment in treatments:
                content.append(_bullet(treatment, S["body"]))
            content.append(Spacer(1, 3))

        if next_steps:
            content.append(Paragraph("Next Steps", S["bold"]))
            for step in next_steps:
                content.append(_bullet(step, S["body"]))
            content.append(Spacer(1, 3))

        if summary:
            content.append(Paragraph(f"<i><b>Summary:</b> {summary}</i>", S["small"]))

        content.append(Spacer(1, 6))

    # ── REFINED DIAGNOSIS SECTION ──
    if refined_diagnosis:
        content.append(_section_header("Refined Diagnosis — Based on Test Results", W, S,
                                       color=colors.HexColor("#1E5C2E")))
        content.append(Spacer(1, 4))

        confirmed    = refined_diagnosis.get("confirmed_conditions", [])
        ruled_out    = refined_diagnosis.get("ruled_out", [])
        final_dx     = refined_diagnosis.get("final_diagnosis", "")
        treatments   = refined_diagnosis.get("updated_treatment", [])
        next_steps   = refined_diagnosis.get("next_steps", [])
        urgency      = refined_diagnosis.get("urgency", "")
        summary      = refined_diagnosis.get("summary", "")

        if final_dx:
            final_box = Table(
                [[Paragraph(f"Final Diagnosis: {final_dx}", S["final_diagnosis"])]],
                colWidths=[W]
            )
            final_box.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#E8F5E9")),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEABOVE",     (0, 0), (-1,  0), 2, CONFIRMED),
            ]))
            content.append(final_box)
            content.append(Spacer(1, 4))

        if confirmed:
            content.append(Paragraph("✅  Confirmed Conditions", S["confirmed"]))
            for c in confirmed:
                status    = c.get("status", "Confirmed")
                condition = c.get("condition", "—")
                evidence  = c.get("evidence", "")
                content.append(_bullet(f"<b>{condition}</b> ({status}) — {evidence}", S["body"]))
            content.append(Spacer(1, 3))

        if ruled_out:
            content.append(Paragraph("❌  Ruled Out", S["ruled_out"]))
            for r in ruled_out:
                condition = r.get("condition", "—")
                reason    = r.get("reason", "")
                content.append(_bullet(f"<b>{condition}</b> — {reason}", S["body"]))
            content.append(Spacer(1, 3))

        if urgency:
            content.append(Spacer(1, 2))
            urgency_map = {
                "Emergency": S["urgency_emergency"],
                "Urgent":    S["urgency_urgent"],
                "Routine":   S["urgency_routine"],
            }
            urgency_label = {
                "Emergency": "🔴  Urgency Level: Emergency — Immediate action required",
                "Urgent":    "🟠  Urgency Level: Urgent — Same day attention required",
                "Routine":   "🟢  Urgency Level: Routine",
            }.get(urgency, f"Urgency Level: {urgency}")
            content.append(Paragraph(urgency_label, urgency_map.get(urgency, S["urgency_routine"])))
            content.append(Spacer(1, 4))

        if treatments:
            content.append(Paragraph("Updated Treatment", S["bold"]))
            for treatment in treatments:
                content.append(_bullet(treatment, S["body"]))
            content.append(Spacer(1, 3))

        if next_steps:
            content.append(Paragraph("Next Steps", S["bold"]))
            for step in next_steps:
                content.append(_bullet(step, S["body"]))
            content.append(Spacer(1, 3))

        if summary:
            content.append(Paragraph(f"<i><b>Summary:</b> {summary}</i>", S["small"]))

        content.append(Spacer(1, 6))

    # ── DISCLAIMER + FOOTER ──
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    content.append(Spacer(1, 4))

    disclaimer_box = Table(
        [[Paragraph(
            "<b>⚠ DISCLAIMER:</b>  This report is generated by NexRay AI and is intended solely as a "
            "clinical decision-support tool. All findings, conditions, treatments, and recommendations "
            "are AI-generated suggestions and do not constitute a formal medical diagnosis or prescription. "
            "The clinical judgment of the attending medical professional must be applied before any action is taken.",
            S["disclaimer"]
        )]],
        colWidths=[W]
    )
    disclaimer_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FDF2F2")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE",     (0, 0), (-1,  0), 1, RED),
    ]))
    content.append(disclaimer_box)
    content.append(Spacer(1, 4))
    content.append(HRFlowable(width="100%", thickness=2, color=NAVY))
    content.append(Spacer(1, 2))
    content.append(Paragraph("NexRay AI  —  Seeing Further, Diagnosing Smarter.", S["footer"]))

    doc.build(content)
    return filepath