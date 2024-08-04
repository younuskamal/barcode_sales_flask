from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime

def generate_invoice_pdf(receipt_id, items, total_price, buyer_name, buyer_phone, seller_id):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    elements = []

    # Register Arabic font
    try:
        pdfmetrics.registerFont(TTFont('Scheherazade', r'C:\Users\YOUNUS KAMAL\Documents\GitHub\barcode_sales_flask\static\font\ScheherazadeNew-Bold.ttf'))
    except Exception as e:
        print(f"Error registering font: {e}")

    # Define styles
    styles = getSampleStyleSheet()
    
    # Title Style
    title_style = ParagraphStyle(
        name='Title',
        fontName='Scheherazade',
        fontSize=36,  # Increased font size
        alignment=1,  # Center align
        spaceAfter=24
    )

    # Header Style
    header_style = ParagraphStyle(
        name='Header',
        fontName='Scheherazade',
        fontSize=26,  # Increased font size
        alignment=1,  # Center align
        spaceAfter=12
    )

    # Normal Style
    normal_style = ParagraphStyle(
        name='Normal',
        fontName='Scheherazade',
        fontSize=18,  # Increased font size
        leading=24,
        spaceAfter=24
    )

    # Define styles for table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Scheherazade'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOX', (0, 0), (-1, 0), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ])

    # Company Info
    company_info = Paragraph(
        "Company Name: Electrical Engineering Co.<br/>"
        "Address: ZAKHO , IRAK <br/>"
        "Phone: 07504333582<br/>"
        "Email: ABDALKADIR@electricalengineering.com",
        normal_style
    )
    elements.append(company_info)
    elements.append(Spacer(1, 24))

    # Title
    title = Paragraph("Invoice", title_style)
    elements.append(title)
    elements.append(Spacer(1, 24))

    # Date and Time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_time_paragraph = Paragraph(f"Date and Time: {current_datetime}", normal_style)
    elements.append(date_time_paragraph)
    elements.append(Spacer(1, 24))

    # Buyer Information
    info_table_data = [
        ['Receipt ID:', receipt_id],
        ['Buyer Name:', buyer_name],
        ['Buyer Phone:', buyer_phone],
        ['Seller ID:', str(seller_id)]  # Add seller ID here
    ]
    
    info_table = Table(info_table_data, colWidths=[3*inch, 4*inch])
    info_table.setStyle(table_style)
    elements.append(info_table)
    elements.append(Spacer(1, 24))

    # Table Data
    data = [['Product', 'Quantity', 'Unit Price', 'Total Price']]
    for item in items:
        data.append([item['productName'], str(item['quantity']), f"${item['total'] / item['quantity']:.2f}", f"${item['total']:.2f}"])

    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Total Amount
    total_paragraph = Paragraph(f"<b>Total Amount:</b> ${total_price:.2f}", normal_style)
    elements.append(total_paragraph)

    doc.build(elements)
    pdf_buffer = buffer.getvalue()
    buffer.close()
    return pdf_buffer
