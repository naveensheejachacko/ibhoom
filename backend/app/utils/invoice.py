"""
Invoice generation utility for ibhoom marketplace
Generates PDF invoices when orders are delivered
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from pathlib import Path
from typing import Optional
from PIL import Image as PILImage
import os


# Company details
COMPANY_NAME = "ibhoom"
COMPANY_ADDRESS = "Kerala, India"
COMPANY_EMAIL = "ibhoomstore@gmail.com"
COMPANY_PHONE = "+91 99475 53510"


def get_payment_status_label(payment_status: str) -> str:
    """Convert payment status to user-friendly label"""
    status_map = {
        'cod_pending': 'Cash on Delivery',
        'cod_collected': 'Payment Collected',
        'paid': 'Paid Online',
        'refunded': 'Refunded'
    }
    return status_map.get(payment_status, payment_status.replace('_', ' ').title())


def create_logo_placeholder(output_path: Path) -> str:
    """
    Create a simple text-based logo placeholder if logo doesn't exist
    Returns the path to the logo file
    """
    logo_path = output_path / "logo.png"
    
    if not logo_path.exists():
        # Create a simple logo image using PIL
        img = PILImage.new('RGB', (200, 60), color='#2c3e50')
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(img)
        # Try to use default font, fallback to basic font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            except:
                font = ImageFont.load_default()
        
        # Draw company name - ensure full name fits
        # Use a smaller font or adjust position to ensure "ibhoom" is fully visible
        text_bbox = draw.textbbox((0, 0), COMPANY_NAME, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        # Center the text if needed, or start from left with padding
        x_pos = max(10, (200 - text_width) // 2) if text_width < 180 else 10
        draw.text((x_pos, 15), COMPANY_NAME, fill='white', font=font)
        img.save(logo_path)
    
    return str(logo_path)


def generate_invoice_pdf(order, output_path: Optional[Path] = None) -> BytesIO:
    """
    Generate a modern PDF invoice for a delivered order
    
    Args:
        order: Order model instance
        output_path: Optional path to save the invoice file
    
    Returns:
        BytesIO buffer containing the PDF invoice
    """
    buffer = BytesIO()
    
    # Create PDF document with modern margins
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch, 
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Modern color scheme
    primary_color = colors.HexColor('#1e40af')  # Modern blue
    accent_color = colors.HexColor('#3b82f6')   # Light blue
    dark_text = colors.HexColor('#1f2937')      # Dark gray
    light_text = colors.HexColor('#6b7280')     # Medium gray
    
    # Modern title style
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceAfter=6,
        spaceBefore=0,
        alignment=TA_RIGHT,
        leading=22
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'ModernHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=16,
        alignment=TA_LEFT
    )
    
    # Company info style
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=light_text,
        alignment=TA_LEFT,
        leading=14
    )
    
    # Info text style
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=dark_text,
        alignment=TA_LEFT,
        leading=14
    )
    
    # Invoice header with logo and company info
    # Get the backend directory (parent of app)
    backend_dir = Path(__file__).parent.parent.parent
    # Get the project root directory (parent of backend)
    project_root = backend_dir.parent
    invoice_dir = backend_dir / "static" / "invoices"
    
    # Create invoice directory if it doesn't exist
    invoice_dir.mkdir(parents=True, exist_ok=True)
    
    # Get logo from static files directory in project root
    logo_path = None
    static_files_dir = project_root / "static files"
    
    # Try to find the logo in static files directory
    if (static_files_dir / "ibhoom logo.png").exists():
        logo_path = str(static_files_dir / "ibhoom logo.png")
    elif (static_files_dir / "ibhoom-logo.png").exists():
        logo_path = str(static_files_dir / "ibhoom-logo.png")
    elif (static_files_dir / "logo.png").exists():
        logo_path = str(static_files_dir / "logo.png")
    # Fallback to backend static/logos directory
    else:
        logo_dir = backend_dir / "static" / "logos"
        logo_dir.mkdir(parents=True, exist_ok=True)
        if (logo_dir / "logo.png").exists():
            logo_path = str(logo_dir / "logo.png")
        elif (logo_dir / "ibhoom.png").exists():
            logo_path = str(logo_dir / "ibhoom.png")
        else:
            # Create placeholder logo as last resort
            logo_path = create_logo_placeholder(logo_dir)
    
    # Modern two-column header layout
    # Left column: Logo and company info | Right column: Invoice details
    
    # Prepare logo
    logo_element = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo_element = Image(logo_path, width=1.8*inch, height=0.55*inch)
        except Exception:
            pass
    
    # Company contact info
    company_contact = f"""
    {COMPANY_ADDRESS}<br/>
    {COMPANY_EMAIL}<br/>
    {COMPANY_PHONE}
    """
    
    # Invoice details
    invoice_date = order.updated_at.strftime("%d %b, %Y") if order.updated_at else datetime.now().strftime("%d %b, %Y")
    order_date = order.created_at.strftime("%d %b, %Y")
    
    # Right-aligned style for invoice details
    right_info_style = ParagraphStyle(
        'RightInfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=dark_text,
        alignment=TA_RIGHT,
        leading=14
    )
    
    # Create invoice section with title and details together (right aligned)
    invoice_section = f"""
    <font size="20" color="#1e40af"><b>INVOICE</b></font><br/>
    <b>Invoice #:</b> {order.order_number}<br/>
    <b>Invoice Date:</b> {invoice_date}<br/>
    <b>Order Date:</b> {order_date}<br/>
    <b>Payment:</b> {get_payment_status_label(order.payment_status.value)}
    """
    
    # Build header table
    if logo_element:
        left_content = [[logo_element], [Paragraph(company_contact, company_style)]]
        left_table = Table(left_content, colWidths=[2.5*inch])
        left_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8),
        ]))
    else:
        left_table = Paragraph(company_contact, company_style)
    
    # Main header table with proper alignment
    header_table = Table([[left_table, Paragraph(invoice_section, right_info_style)]], colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 20),
    ]))
    elements.append(header_table)
    
    # Divider line
    line_table = Table([[""]], colWidths=[7*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, accent_color),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    elements.append(line_table)
    
    # Modern Bill To section
    elements.append(Paragraph("BILL TO", heading_style))
    
    customer_name = f"{order.customer.first_name} {order.customer.last_name}" if order.customer else "Customer"
    customer_email = order.customer.email if order.customer else ""
    
    customer_info = f"""
    <b>{customer_name}</b><br/>
    {customer_email}<br/>
    {order.delivery_address}<br/>
    {order.delivery_city}, {order.delivery_state} - {order.delivery_pincode}<br/>
    Phone: {order.phone}
    """
    
    customer_box = Table([[Paragraph(customer_info, info_style)]], colWidths=[7*inch])
    customer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(customer_box)
    elements.append(Spacer(1, 0.25*inch))
    
    # Modern items section
    elements.append(Paragraph("ITEMS", heading_style))
    
    # Use Rs. instead of rupee symbol to avoid rendering issues
    rupee_symbol = "Rs."
    
    # Modern item table with clean design
    items_data = [["ITEM", "QTY", "PRICE", "TAX", "AMOUNT"]]
    
    # Small font style for table content
    small_style = ParagraphStyle('SmallStyle', parent=styles['Normal'], fontSize=9, leading=11)
    
    for item in order.items:
        item_name = item.product_name
        quantity = item.quantity
        unit_price = float(item.customer_unit_price)
        tax_rate = float(item.tax_rate)
        tax_unit_amount = float(item.tax_unit_amount)
        final_total = float(item.total_final_amount)
        
        items_data.append([
            Paragraph(item_name, small_style),
            str(quantity),
            f"{rupee_symbol} {unit_price:.2f}",
            f"{tax_rate:.1f}%",
            f"{rupee_symbol} {final_total:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3.2*inch, 0.6*inch, 1.1*inch, 0.9*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Content rows
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 10),
        
        # Borders
        ('LINEBELOW', (0, 0), (-1, 0), 2, primary_color),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Modern totals section - right aligned
    subtotal = float(order.total_customer_amount)
    tax_total = float(order.total_tax_amount)
    grand_total = float(order.grand_total_amount)
    total_items = sum(item.quantity for item in order.items)
    
    # Summary style
    summary_style = ParagraphStyle('SummaryStyle', parent=styles['Normal'], 
                                   fontSize=10, textColor=dark_text, alignment=TA_RIGHT)
    summary_bold_style = ParagraphStyle('SummaryBoldStyle', parent=styles['Normal'], 
                                        fontSize=10, textColor=dark_text, 
                                        fontName='Helvetica-Bold', alignment=TA_RIGHT)
    total_style = ParagraphStyle('TotalStyle', parent=styles['Normal'], 
                                 fontSize=13, textColor=primary_color, 
                                 fontName='Helvetica-Bold', alignment=TA_RIGHT)
    
    totals_data = [
        [Paragraph("Subtotal:", summary_style), Paragraph(f"{rupee_symbol} {subtotal:.2f}", summary_style)],
        [Paragraph("Tax:", summary_style), Paragraph(f"{rupee_symbol} {tax_total:.2f}", summary_style)],
        [Paragraph("Total Items:", summary_style), Paragraph(str(total_items), summary_style)],
        ["", ""],
        [Paragraph("TOTAL", total_style), Paragraph(f"{rupee_symbol} {grand_total:.2f}", total_style)],
    ]
    
    totals_table = Table(totals_data, colWidths=[5.2*inch, 1.8*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, 2), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 2), 6),
        ('TOPPADDING', (0, 4), (-1, 4), 10),
        ('BOTTOMPADDING', (0, 4), (-1, 4), 10),
        ('LINEABOVE', (0, 4), (-1, 4), 2, primary_color),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#eff6ff')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Modern footer
    footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], 
                                  fontSize=9, textColor=light_text, 
                                  alignment=TA_CENTER, leading=12)
    
    # Divider line before footer
    footer_line = Table([[""]], colWidths=[7*inch])
    footer_line.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
    ]))
    elements.append(footer_line)
    
    footer_text = """
    <b>Thank you for your business!</b><br/>
    This is a computer-generated invoice and does not require a signature.<br/>
    For any queries, please contact us at {email} or call {phone}
    """.format(email=COMPANY_EMAIL, phone=COMPANY_PHONE)
    
    footer = Paragraph(footer_text, footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Save to file if path provided
    if output_path:
        invoice_dir.mkdir(parents=True, exist_ok=True)
        file_path = invoice_dir / f"invoice_{order.order_number}.pdf"
        with open(file_path, 'wb') as f:
            f.write(buffer.getvalue())
        buffer.seek(0)  # Reset buffer position
    
    buffer.seek(0)  # Reset buffer position for reading
    return buffer

