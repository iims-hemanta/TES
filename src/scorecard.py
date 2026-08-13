"""ReportLab 1-page PDF scorecard engine for the TES 360° Evaluation System."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .config import (
    CLASSIFICATION_THRESHOLDS,
    COLOR_ACCENT_HL,
    COLOR_BG_HEADER,
    COLOR_BG_ROW_ALT,
    COLOR_BORDER,
    COLOR_MUTED_TEXT,
    COLOR_PRIMARY,
)


def _classify(final_score: float) -> Tuple[str, str]:
    """Return (result_text, description) based on the final classification score."""
    for threshold, result_text, description in CLASSIFICATION_THRESHOLDS:
        if final_score < threshold:
            return result_text, description
    # Should never reach here, but return the last (highest) tier
    return CLASSIFICATION_THRESHOLDS[-1][1], CLASSIFICATION_THRESHOLDS[-1][2]


def build_pdf_scorecard(
    pdf_path: str,
    faculty_name: str,
    staff_id: str,
    school_name: str,
    experience: str,
    qualification: str,
    period_code: str,
    d_scores: Dict[str, float],
    stakeholder_scores: Dict[str, float],
    radar_png: str,
) -> Tuple[str, float, float, str]:
    """
    Build a 1-page PDF scorecard for a single faculty member.

    Parameters
    ----------
    pdf_path : str
        Output path for the PDF file.
    faculty_name : str
        Faculty member's name.
    staff_id : str
        Staff identification number.
    school_name : str
        School or college name.
    experience : str
        Teaching experience (e.g. "5.5 years").
    qualification : str
        Highest academic qualification.
    period_code : str
        Appraisal period code (e.g. "AP2024/04").
    d_scores : dict
        Dimension scores (D1–D7), each out of 5.0.
    stakeholder_scores : dict
        Stakeholder scores (Self, Superior, Peers, Students), each out of 70.
    radar_png : str
        Path to the radar chart PNG.

    Returns
    -------
    tuple
        (pdf_path, weighted_avg, final_score, result_text)
    """
    # Set explicit document metadata to fix the browser tab title
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=f"{faculty_name.upper()} ({staff_id}) Scorecard",
        author=school_name,
        subject=f"{period_code} Scorecard Report",
    )
    styles = getSampleStyleSheet()

    # Palette definition
    PRIMARY = colors.HexColor(COLOR_PRIMARY)
    MUTED_TEXT = colors.HexColor(COLOR_MUTED_TEXT)
    BG_HEADER = colors.HexColor(COLOR_BG_HEADER)
    BG_ROW_ALT = colors.HexColor(COLOR_BG_ROW_ALT)
    BORDER_COLOR = colors.HexColor(COLOR_BORDER)
    ACCENT_HL = colors.HexColor(COLOR_ACCENT_HL)

    title_style = ParagraphStyle(
        "Title", parent=styles["Normal"], fontSize=15, fontName="Helvetica-Bold", textColor=PRIMARY
    )
    header_right = ParagraphStyle(
        "HeaderRight", parent=styles["Normal"], fontSize=13, fontName="Helvetica-Bold", alignment=2, textColor=PRIMARY
    )
    sec_banner = ParagraphStyle(
        "SecBanner", parent=styles["Normal"], fontSize=9.5, fontName="Helvetica-Bold", textColor=colors.white
    )
    text_style = ParagraphStyle(
        "Text", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=PRIMARY
    )
    bold_text = ParagraphStyle(
        "BoldText", parent=styles["Normal"], fontSize=8.5, leading=11, fontName="Helvetica-Bold", textColor=PRIMARY
    )

    elements = []

    # 1. Header Block
    header_data = [
        [
            Paragraph(
                f"<b>{faculty_name.upper()} ({staff_id})</b><br/>"
                f"<font size=8.5 color='#64748B'>{school_name}</font>",
                title_style,
            ),
            Paragraph(f"{period_code} SCORECARD", header_right),
        ]
    ]
    elements.append(Table(header_data, colWidths=[340, 200]))
    elements.append(
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=4, spaceAfter=8)
    )

    # 2. Profile & TES Framework Banners
    t1 = Table(
        [
            [
                Paragraph("PROFILE", sec_banner),
                Paragraph("TEACHING EXCELLENCE FRAMEWORK (360° EVALUATION)", sec_banner),
            ]
        ],
        colWidths=[260, 280],
    )
    t1.setStyle(
        TableStyle([("BACKGROUND", (0, 0), (-1, -1), BG_HEADER), ("PADDING", (0, 0), (-1, -1), 4)])
    )
    elements.append(t1)

    prof_text = (
        f"Teaching Experience: <b>{experience}</b><br/>"
        f"Highest Academic Qualification: <b>{qualification}</b>"
    )
    tes_desc = (
        "TES utilizes a multi-source 360° feedback system across D1-D7 capability dimensions: "
        "Contextualization, Supportive Environment, Impact, Feedback, Technology, "
        "Affective Attributes, Research."
    )

    t2 = Table([[Paragraph(prof_text, text_style), Paragraph(tes_desc, text_style)]], colWidths=[260, 280])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG_ROW_ALT),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ]
        )
    )
    elements.append(t2)
    elements.append(Spacer(1, 6))

    # 3. Left Column Layout
    left_flowables = []
    tea_b = Table([[Paragraph("TEACHING ENGAGEMENT ASSESSMENT SCALE", sec_banner)]], colWidths=[260])
    tea_b.setStyle(
        TableStyle([("BACKGROUND", (0, 0), (-1, -1), BG_HEADER), ("PADDING", (0, 0), (-1, -1), 4)])
    )
    left_flowables.append(tea_b)

    cell_hdr = ParagraphStyle(
        "CHdr", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=colors.white
    )
    d_rows = [
        [Paragraph("Dimension (Calculated from Student Data)", cell_hdr), Paragraph("Score", cell_hdr)]
    ]
    for k, v in d_scores.items():
        d_rows.append([Paragraph(k, text_style), Paragraph(f"{v:.1f} / 5.0", text_style)])

    t_d = Table(d_rows, colWidths=[200, 60])
    t_d.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("PADDING", (0, 0), (-1, -1), 2.5),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_ROW_ALT]),
            ]
        )
    )
    left_flowables.append(t_d)
    left_flowables.append(Spacer(1, 6))

    stk_rows = [
        [Paragraph("360° Teaching Engagement Assessment", cell_hdr), Paragraph("Score", cell_hdr)]
    ]
    stk_rows.append(
        [Paragraph("Self", text_style), Paragraph(f"{stakeholder_scores['Self']:.1f} / 70.0", text_style)]
    )
    stk_rows.append(
        [Paragraph("Peers", text_style), Paragraph(f"{stakeholder_scores['Peers']:.1f} / 70.0", text_style)]
    )
    stk_rows.append(
        [Paragraph("Superior", text_style), Paragraph(f"{stakeholder_scores['Superior']:.1f} / 70.0", text_style)]
    )
    stk_rows.append(
        [
            Paragraph("<b>Students (Actual Data)</b>", bold_text),
            Paragraph(f"<b>{stakeholder_scores['Students']:.1f} / 70.0</b>", bold_text),
        ]
    )

    weighted_avg = float(np.mean(list(stakeholder_scores.values())))
    stk_rows.append(
        [
            Paragraph("<b>360° Weighted Average</b>", bold_text),
            Paragraph(f"<b>{weighted_avg:.1f} / 70.0</b>", bold_text),
        ]
    )

    t_stk = Table(stk_rows, colWidths=[200, 60])
    t_stk.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("PADDING", (0, 0), (-1, -1), 2.5),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("BACKGROUND", (0, -1), (-1, -1), ACCENT_HL),
            ]
        )
    )
    left_flowables.append(t_stk)

    # 4. Right Column Layout
    right_flowables = [
        Paragraph(
            "<b>Dimensions 360° TES Assessment</b>",
            ParagraphStyle("Ctr", parent=bold_text, alignment=1),
        ),
        Image(radar_png, width=165, height=165),
        Spacer(1, 2),
    ]

    class_b = Table([[Paragraph("CLASSIFICATION LEVEL (CL)", sec_banner)]], colWidths=[260])
    class_b.setStyle(
        TableStyle([("BACKGROUND", (0, 0), (-1, -1), BG_HEADER), ("PADDING", (0, 0), (-1, -1), 4)])
    )
    right_flowables.append(class_b)

    cl_data = [
        [Paragraph("CL < 56.0", text_style), Paragraph("Poor Teaching Engagement", text_style)],
        [Paragraph("56.0 ≤ CL < 65.0", text_style), Paragraph("Fair Teaching Engagement", text_style)],
        [Paragraph("65.0 ≤ CL < 75.0", text_style), Paragraph("Average Teaching Engagement", text_style)],
        [Paragraph("75.0 ≤ CL < 85.0", text_style), Paragraph("Above Average Teaching Engagement", text_style)],
        [Paragraph("CL ≥ 85.0", bold_text), Paragraph("<b>Excellent Teaching Engagement</b>", bold_text)],
    ]
    t_cl = Table(cl_data, colWidths=[110, 150])
    t_cl.setStyle(
        TableStyle(
            [
                ("PADDING", (0, 0), (-1, -1), 2),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG_ROW_ALT]),
            ]
        )
    )

    final_score = (weighted_avg / 70.0) * 100.0
    result_text, _ = _classify(final_score)

    # Highlight the active classification row
    row_index = 0
    for i, (threshold, _, _) in enumerate(CLASSIFICATION_THRESHOLDS):
        if final_score < threshold:
            row_index = i
            break
    t_cl.setStyle(TableStyle([("BACKGROUND", (0, row_index), (-1, row_index), ACCENT_HL)]))

    right_flowables.append(t_cl)

    main_grid = Table([[left_flowables, right_flowables]], colWidths=[270, 270])
    main_grid.setStyle(
        TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 0)])
    )
    elements.append(main_grid)
    elements.append(Spacer(1, 8))

    # 5. Calculation Summary Block
    calc_b = Table([[Paragraph("CLASSIFICATION CALCULATION (%)", sec_banner)]], colWidths=[540])
    calc_b.setStyle(
        TableStyle([("BACKGROUND", (0, 0), (-1, -1), BG_HEADER), ("PADDING", (0, 0), (-1, -1), 4)])
    )
    elements.append(calc_b)

    calc_data = [
        [Paragraph("Teaching Experience (Weight: 0.0%)", text_style), Paragraph("0.0 / 0.0", text_style)],
        [
            Paragraph("Highest Academic Qualification (Weight: 0.0%)", text_style),
            Paragraph("0.0 / 0.0", text_style),
        ],
        [
            Paragraph("Teaching Engagement Assessment Scale (Weight: 100.0%)", text_style),
            Paragraph(f"{final_score:.1f} / 100.0", text_style),
        ],
        [
            Paragraph("<b>Classification Score</b>", bold_text),
            Paragraph(f"<b>{final_score:.1f} / 100.0</b>", bold_text),
        ],
    ]
    t_calc = Table(calc_data, colWidths=[400, 140])
    t_calc.setStyle(
        TableStyle(
            [
                ("PADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("ROWBACKGROUNDS", (0, 0), (-1, -2), [colors.white, BG_ROW_ALT]),
                ("BACKGROUND", (0, -1), (-1, -1), ACCENT_HL),
            ]
        )
    )
    elements.append(t_calc)
    elements.append(Spacer(1, 10))

    # 6. Status Footer Banner
    res_b = Table([[Paragraph(f"<b>{result_text}</b>", sec_banner)]], colWidths=[540])
    res_b.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    elements.append(res_b)

    doc.build(elements)

    # Clean up the radar PNG
    if os.path.exists(radar_png):
        os.remove(radar_png)

    return pdf_path, weighted_avg, final_score, result_text
