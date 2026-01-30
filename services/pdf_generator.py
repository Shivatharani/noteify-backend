from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime

# ─────────────────────────────────────────────
# Professional Page Design with Canvas
# ─────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._pages)
        for page_num, page in enumerate(self._pages, 1):
            self.__dict__.update(page)
            self.draw_page_decorations(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_num, total_pages):
        width, height = A4
        
        # Professional header background
        self.setFillColor(HexColor("#0F172A"))
        self.rect(0, height - 70, width, 70, fill=True, stroke=False)
        
        # Header text
        self.setFont("Helvetica-Bold", 18)
        self.setFillColor(HexColor("#FFFFFF"))
        self.drawString(50, height - 40, "NOTEIFY AI")
        
        self.setFont("Helvetica", 11)
        self.setFillColor(HexColor("#CBD5E1"))
        self.drawString(50, height - 55, "Professional Lecture Notes Generator")
        
        # Decorative line
        self.setStrokeColor(HexColor("#3B82F6"))
        self.setLineWidth(2)
        self.line(50, height - 65, width - 50, height - 65)
        
        # Footer
        self.setFont("Helvetica", 9)
        self.setFillColor(HexColor("#64748B"))
        self.drawString(50, 30, f"Generated on {datetime.now().strftime('%d %B %Y')}")
        self.drawRightString(width - 50, 30, f"Page {page_num} of {total_pages}")
        
        # Footer line
        self.setStrokeColor(HexColor("#E2E8F0"))
        self.setLineWidth(1)
        self.line(50, 45, width - 50, 45)

# ─────────────────────────────────────────────
# Professional PDF Generator
# ─────────────────────────────────────────────
def create_pdf(notes_data: dict, output_path: str, original_filename: str):
    """Create a professional, beautifully aligned PDF with unique style names"""
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=100,
        bottomMargin=60
    )

    # Get default styles
    styles = getSampleStyleSheet()

    # ═══════════════════════════════════════════
    # CUSTOM PROFESSIONAL STYLES - UNIQUE NAMES
    # ═══════════════════════════════════════════
    
    styles.add(ParagraphStyle(
        name="NoteifyTitle",
        fontName="Helvetica-Bold",
        fontSize=32,
        alignment=TA_CENTER,
        textColor=HexColor("#0F172A"),
        spaceAfter=10,
        leading=38,
        leftIndent=0,
        rightIndent=0
    ))

    styles.add(ParagraphStyle(
        name="NoteifySubtitle",
        fontName="Helvetica",
        fontSize=13,
        alignment=TA_CENTER,
        textColor=HexColor("#64748B"),
        spaceAfter=35,
        leading=16
    ))

    styles.add(ParagraphStyle(
        name="NoteifyMeta",
        fontName="Helvetica",
        fontSize=10,
        alignment=TA_CENTER,
        textColor=HexColor("#475569"),
        spaceAfter=40,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name="NoteifySectionTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=HexColor("#1E40AF"),
        spaceBefore=25,
        spaceAfter=12,
        leftIndent=0,
        rightIndent=0
    ))

    styles.add(ParagraphStyle(
        name="NoteifySummary",
        fontName="Helvetica",
        fontSize=12,
        alignment=TA_JUSTIFY,
        leading=18,
        textColor=HexColor("#1F2937"),
        spaceAfter=30,
        leftIndent=12,
        rightIndent=0,
        borderLeft=3,
        borderLeftColor=HexColor("#3B82F6"),
        borderLeftWidth=3,
        borderPadding=12
    ))

    styles.add(ParagraphStyle(
        name="NoteifyContent",
        fontName="Helvetica",
        fontSize=11,
        alignment=TA_JUSTIFY,
        leading=17,
        textColor=HexColor("#334155"),
        spaceAfter=14,
        leftIndent=0,
        rightIndent=0
    ))

    # ═══════════════════════════════════════════
    # BUILD DOCUMENT STORY
    # ═══════════════════════════════════════════
    story = []

    # TITLE
    story.append(Paragraph("LECTURE NOTES", styles["NoteifyTitle"]))
    story.append(Spacer(1, 12))

    # SUBTITLE
    story.append(Paragraph("Professional AI-Generated Summary & Transcription", styles["NoteifySubtitle"]))
    
    # META INFO TABLE (Clean, professional look)
    meta_data = [
        [
            Paragraph(f"<b>Source File:</b><br/>{original_filename}", styles["NoteifyMeta"]),
            Paragraph(f"<b>Generated:</b><br/>{datetime.now().strftime('%d %B %Y')}", styles["NoteifyMeta"]),
            Paragraph(f"<b>Time:</b><br/>{datetime.now().strftime('%I:%M %p')}", styles["NoteifyMeta"])
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 30))

    # ─────────────────────────────────────────
    # EXECUTIVE SUMMARY (2-3 LINES - CLEAN)
    # ─────────────────────────────────────────
    summary_text = notes_data["summary"]["paragraph"].strip()
    
    # Remove trailing dots or ellipsis
    summary_text = summary_text.rstrip('.')
    summary_text = summary_text.rstrip('…')
    summary_text = summary_text.rstrip('...')
    summary_text = summary_text.strip()
    
    # Ensure proper ending punctuation
    if not summary_text.endswith(('.', '!', '?')):
        summary_text += '.'
    
    story.append(Paragraph("EXECUTIVE SUMMARY", styles["NoteifySectionTitle"]))
    story.append(Paragraph(summary_text, styles["NoteifySummary"]))
    story.append(Spacer(1, 15))

    # ─────────────────────────────────────────
    # COMPLETE TRANSCRIPTION
    # ─────────────────────────────────────────
    story.append(Paragraph("COMPLETE TRANSCRIPTION", styles["NoteifySectionTitle"]))
    story.append(Spacer(1, 10))

    for i, paragraph in enumerate(notes_data["full_transcription"], 1):
        # Clean paragraph text
        para_text = paragraph.strip()
        if not para_text.endswith(('.', '!', '?')):
            para_text += '.'
        
        # Format with number
        numbered_para = f"<b>{i}.</b>&nbsp;&nbsp;&nbsp;&nbsp;{para_text}"
        story.append(Paragraph(numbered_para, styles["NoteifyContent"]))
        
        # Smart page break every 12 paragraphs
        if i % 12 == 0 and i < len(notes_data["full_transcription"]):
            story.append(PageBreak())

    # ─────────────────────────────────────────
    # BUILD PDF WITH CUSTOM CANVAS
    # ─────────────────────────────────────────
    doc.build(story, canvasmaker=NumberedCanvas)
