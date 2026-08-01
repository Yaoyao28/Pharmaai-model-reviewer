from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _escape_reportlab_text(
    value: object,
) -> str:
    """
    Escape characters that ReportLab Paragraph treats as markup.
    """

    text = str(value)

    return (
        text.replace(
            "&",
            "&amp;",
        )
        .replace(
            "<",
            "&lt;",
        )
        .replace(
            ">",
            "&gt;",
        )
    )


def _markdown_to_paragraphs(
    text: str,
    body_style: ParagraphStyle,
    heading_style: ParagraphStyle,
) -> list[Any]:
    """
    Convert simple Markdown-like LLM output into ReportLab elements.

    Supported:
        ## Heading
        ### Heading
        - bullet
        normal paragraph

    This is intentionally simple and stable.
    """

    elements: list[Any] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            elements.append(
                Spacer(
                    1,
                    0.08 * inch,
                )
            )
            continue

        if line.startswith("### "):
            heading = _escape_reportlab_text(
                line[4:]
            )

            elements.append(
                Paragraph(
                    heading,
                    heading_style,
                )
            )

            continue

        if line.startswith("## "):
            heading = _escape_reportlab_text(
                line[3:]
            )

            elements.append(
                Paragraph(
                    heading,
                    heading_style,
                )
            )

            continue

        if line.startswith("- "):
            bullet_text = _escape_reportlab_text(
                line[2:]
            )

            elements.append(
                Paragraph(
                    f"&#8226; {bullet_text}",
                    body_style,
                )
            )

            continue

        cleaned_line = _escape_reportlab_text(
            line
        )

        elements.append(
            Paragraph(
                cleaned_line,
                body_style,
            )
        )

    return elements


def _add_page_number(
    canvas: Any,
    document: Any,
) -> None:
    """
    Add page number and footer to every PDF page.
    """

    canvas.saveState()

    page_number = canvas.getPageNumber()

    footer_text = (
        "PharmaAI Model Reviewer - "
        f"Page {page_number}"
    )

    canvas.setFont(
        "Helvetica",
        8,
    )

    canvas.drawCentredString(
        letter[0] / 2,
        0.35 * inch,
        footer_text,
    )

    canvas.restoreState()


def generate_pdf_report(
    report_data: dict[str, Any],
) -> bytes:
    """
    Generate a PDF report and return it as bytes.

    These bytes can be supplied directly to:

        st.download_button(...)
    """

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=str(
            report_data.get(
                "report_title",
                "PharmaAI Model Review Report",
            )
        ),
        author="PharmaAI Model Reviewer",
    )

    style_sheet = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="ReportTitle",
        parent=style_sheet["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    subtitle_style = ParagraphStyle(
        name="ReportSubtitle",
        parent=style_sheet["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#555555"
        ),
        spaceAfter=14,
    )

    section_style = ParagraphStyle(
        name="SectionHeading",
        parent=style_sheet["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    subsection_style = ParagraphStyle(
        name="SubsectionHeading",
        parent=style_sheet["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        name="ReportBody",
        parent=style_sheet["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        name="SmallText",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#555555"
        ),
    )

    story: list[Any] = []

    report_title = _escape_reportlab_text(
        report_data.get(
            "report_title",
            "PharmaAI Model Review Report",
        )
    )

    story.append(
        Paragraph(
            report_title,
            title_style,
        )
    )

    subtitle_text = (
        f"Generated: "
        f"{_escape_reportlab_text(report_data.get('generated_at_display', 'Not available'))}"
        "<br/>"
        f"Status: "
        f"{_escape_reportlab_text(report_data.get('report_status', 'Not available'))}"
    )

    story.append(
        Paragraph(
            subtitle_text,
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Final Selected Base Model",
            section_style,
        )
    )

    selected_models = report_data.get(
        "selected_models",
        {},
    )

    selected_model_table = Table(
        [
            [
                "Component",
                "Selected model",
            ],
            [
                "Absorption",
                str(
                    selected_models.get(
                        "absorption_model",
                        "Not selected",
                    )
                ),
            ],
            [
                "Structural",
                str(
                    selected_models.get(
                        "structural_model",
                        "Not selected",
                    )
                ),
            ],
            [
                "Residual error",
                str(
                    selected_models.get(
                        "residual_error_model",
                        "Not selected",
                    )
                ),
            ],
        ],
        colWidths=[
            1.55 * inch,
            5.3 * inch,
        ],
        repeatRows=1,
    )

    selected_model_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#DCE6F1"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#1F2937"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "LEADING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#AAB2BD"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        selected_model_table
    )

    story.append(
        Spacer(
            1,
            0.15 * inch,
        )
    )

    final_model_text = _escape_reportlab_text(
        report_data.get(
            "final_model",
            "Not available",
        )
    )

    story.append(
        Paragraph(
            (
                "<b>Final model:</b> "
                f"{final_model_text}"
            ),
            body_style,
        )
    )

    story.append(
        Spacer(
            1,
            0.15 * inch,
        )
    )

    llm_information_table = Table(
        [
            [
                "LLM provider",
                str(
                    report_data.get(
                        "llm_provider",
                        "Not recorded",
                    )
                ),
            ],
            [
                "LLM model",
                str(
                    report_data.get(
                        "llm_model",
                        "Not recorded",
                    )
                ),
            ],
        ],
        colWidths=[
            1.55 * inch,
            5.3 * inch,
        ],
    )

    llm_information_table.setStyle(
        TableStyle(
            [
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor(
                        "#C8CDD3"
                    ),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F3F4F6"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(
        llm_information_table
    )

    sections = report_data.get(
        "sections",
        [],
    )

    for section_number, section in enumerate(
        sections,
        start=1,
    ):
        story.append(
            PageBreak()
        )

        stage_name = _escape_reportlab_text(
            section.get(
                "stage_name",
                f"Stage {section_number}",
            )
        )

        story.append(
            Paragraph(
                stage_name,
                section_style,
            )
        )

        summary_table = Table(
            [
                [
                    "Reviewer-selected model",
                    str(
                        section.get(
                            "selected_model",
                            "Not selected",
                        )
                    ),
                ],
                [
                    "Numerically favored model",
                    str(
                        section.get(
                            "numerically_favored_model",
                            "Not determined",
                        )
                    ),
                ],
                [
                    "Reviewer decision",
                    str(
                        section.get(
                            "reviewer_decision",
                            "Not recorded",
                        )
                    ),
                ],
            ],
            colWidths=[
                1.85 * inch,
                5.0 * inch,
            ],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor(
                            "#F3F4F6"
                        ),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#B8BEC5"
                        ),
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            summary_table
        )

        story.append(
            Paragraph(
                "Deterministic Numerical Conclusion",
                subsection_style,
            )
        )

        deterministic_conclusion = (
            _escape_reportlab_text(
                section.get(
                    "deterministic_conclusion",
                    "Not available",
                )
            )
        )

        story.append(
            Paragraph(
                deterministic_conclusion,
                body_style,
            )
        )

        story.append(
            Paragraph(
                "LLM-Assisted Review",
                subsection_style,
            )
        )

        llm_review = str(
            section.get(
                "llm_review",
                "No LLM review was generated.",
            )
        )

        story.extend(
            _markdown_to_paragraphs(
                text=llm_review,
                body_style=body_style,
                heading_style=subsection_style,
            )
        )

        story.append(
            Paragraph(
                "Reviewer Comments",
                subsection_style,
            )
        )

        reviewer_comments = (
            _escape_reportlab_text(
                section.get(
                    "reviewer_comments",
                    "No reviewer comments were recorded.",
                )
            )
        )

        story.append(
            Paragraph(
                reviewer_comments,
                body_style,
            )
        )

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Audit Information and Limitations",
            section_style,
        )
    )

    audit_statement = _escape_reportlab_text(
        report_data.get(
            "audit_statement",
            "Not available",
        )
    )

    story.append(
        Paragraph(
            audit_statement,
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Limitations",
            subsection_style,
        )
    )

    for limitation in report_data.get(
        "limitations",
        [],
    ):
        limitation_text = _escape_reportlab_text(
            limitation
        )

        story.append(
            Paragraph(
                f"&#8226; {limitation_text}",
                body_style,
            )
        )

    story.append(
        Spacer(
            1,
            0.15 * inch,
        )
    )

    story.append(
        Paragraph(
            (
                "This report is an AI-assisted draft. "
                "Final scientific responsibility remains "
                "with the qualified human reviewer."
            ),
            small_style,
        )
    )

    document.build(
        story,
        onFirstPage=_add_page_number,
        onLaterPages=_add_page_number,
    )

    pdf_bytes = pdf_buffer.getvalue()

    pdf_buffer.close()

    return pdf_bytes