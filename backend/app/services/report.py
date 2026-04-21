from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from pathlib import Path
from .storage import resolve_report_path


def generate_result_report(student_name: str, subject_name: str, evaluation: dict, report_filename: str) -> str:
    report_path = resolve_report_path(report_filename)
    doc = SimpleDocTemplate(str(report_path), pagesize=letter,
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='ReportTitle',
        parent=styles['Title'],
        alignment=1,
        spaceAfter=14,
    )
    normal_style = ParagraphStyle(
        name='NormalBody',
        parent=styles['BodyText'],
        leading=14,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        name='TableCell',
        parent=styles['BodyText'],
        leading=12,
        fontSize=9,
    )

    elements = []
    elements.append(Paragraph('Smart Exam Copy Evaluation Report', title_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'<b>Student:</b> {student_name}', normal_style))
    elements.append(Paragraph(f'<b>Subject:</b> {subject_name}', normal_style))
    elements.append(Paragraph(f'<b>Score:</b> {evaluation.get("score", 0)} / {evaluation.get("max_score", 0)}', normal_style))
    
    # Feedback handle karna (agar bohot bada ho toh)
    feedback_text = str(evaluation.get("feedback", "No overall feedback provided."))
    feedback_text = feedback_text.replace('\n', '<br />')
    elements.append(Paragraph(f'<b>Overall Feedback:</b> {feedback_text}', normal_style))
    elements.append(Spacer(1, 12))

    summary = (
        'This report summarizes the graded student responses against the uploaded answer key. ' 
        'Scores reflect semantic relevance, keyword coverage, and answer accuracy for each response.'
    )
    elements.append(Paragraph(summary, cell_style))
    elements.append(Spacer(1, 12))

    # TABLE HEADERS UPDATE
    table_data = [['Q.No', 'Score', 'Student Response', 'Professor Comment']]
    
    for item in evaluation.get('details', []):
        q_num = str(item.get('question_number', item.get('question', 'N/A')))
        score = str(item.get('score', item.get('marks', '0')))
        response = str(item.get('student_response', item.get('response', 'Not transcribed')))
        comment = str(item.get('professor_comment', item.get('comment', item.get('feedback', ''))))
        
        table_data.append([
            Paragraph(q_num, cell_style),
            Paragraph(score, cell_style),
            Paragraph(response, cell_style),
            Paragraph(comment, cell_style),
        ])

    # COLUMNS WIDHTS ARE ADJUSTED ACCORDING TO 4 COLUMNS 
    table = Table(table_data, colWidths=[40, 40, 250, 200], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph('<b>Professor notes:</b>', normal_style))
    notes = 'Review the comments for each question carefully. This detailed feedback reflects how a professor would mark the copy.'
    elements.append(Paragraph(notes, cell_style))

    doc.build(elements)
    
    # FastAPI ko result update karne ke liye sirf filename return karo
    return report_filename