import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, HRFlowable

_styles_cache = None

def _get_styles():
    """✅ Professional, perfectly aligned styles."""
    global _styles_cache
    if _styles_cache is not None:
        return _styles_cache
    
    styles = getSampleStyleSheet()
    
    # Title - Large, centered, bold
    styles.add(ParagraphStyle(
        name='PerfectTitle',
        fontSize=26,
        leading=30,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=TA_CENTER,
        spaceAfter=35,
        fontName="Helvetica-Bold"
    ))
    
    # Subtitle - Small, gray, centered
    styles.add(ParagraphStyle(
        name='PerfectSubtitle',
        fontSize=11,
        textColor=colors.HexColor("#6B7280"),
        alignment=TA_CENTER,
        spaceAfter=30
    ))
    
    # Section Headers - Bold, blue, left-aligned
    styles.add(ParagraphStyle(
        name='PerfectSection',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=30,
        spaceAfter=15,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT
    ))
    
    # Summary - Justified, indented, clean
    styles.add(ParagraphStyle(
        name='PerfectSummary',
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        leftIndent=15,
        rightIndent=15,
        spaceAfter=25,
        fontName="Helvetica"
    ))
    
    # Transcription - Readable paragraphs
    styles.add(ParagraphStyle(
        name='PerfectBody',
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leftIndent=10,
        rightIndent=10
    ))
    
    _styles_cache = styles
    return styles

def create_pdf(notes_data: dict, output_path: str):
    """✅ PERFECTLY ALIGNED PDF STRUCTURE."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.8*inch,
        leftMargin=0.8*inch,
        topMargin=1.2*inch,
        bottomMargin=1*inch
    )
    
    styles = _get_styles()
    story = []
    
    # ═══════════════════════════════════════════════════════════════
    # HEADER SECTION
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("📚 LECTURE NOTES", styles['PerfectTitle']))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y | %I:%M %p')}",
        styles['PerfectSubtitle']
    ))
    story.append(Spacer(1, 25))
    
    # ═══════════════════════════════════════════════════════════════
    # SUMMARY SECTION
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("📋 EXECUTIVE SUMMARY", styles['PerfectSection']))
    summary = notes_data.get('summary', 'Summary not available')
    story.append(Paragraph(summary, styles['PerfectSummary']))
    story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor("#E5E7EB"), spaceBefore=15, spaceAfter=20))
    
    # ═══════════════════════════════════════════════════════════════
    # FULL TRANSCRIPTION SECTION
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("🎙️ COMPLETE TRANSCRIPTION", styles['PerfectSection']))
    story.append(Spacer(1, 10))
    
    full_text = notes_data.get('full_transcription', '')
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', full_text) if s.strip()]
    
    # Perfect paragraph formation (70 words max per para)
    para_buffer = []
    for sentence in sentences:
        para_words = len(re.split(r'\s+', " ".join(para_buffer + [sentence])))
        if para_words > 70 and para_buffer:
            story.append(Paragraph(" ".join(para_buffer), styles['PerfectBody']))
            para_buffer = [sentence]
        else:
            para_buffer.append(sentence)
    
    if para_buffer:
        story.append(Paragraph(" ".join(para_buffer), styles['PerfectBody']))
    
    try:
        doc.build(story)
        print(f"✅ Perfectly structured PDF created: {output_path}")
    except Exception as e:
        print(f"❌ PDF Error: {e}")
        raise
