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
COMPANY_EMAIL = "support@ibhoom.com"
COMPANY_PHONE = "+91 XXX XXX XXXX"


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
    Generate a PDF invoice for a delivered order
    
    Args:
        order: Order model instance
        output_path: Optional path to save the invoice file
    
    Returns:
        BytesIO buffer containing the PDF invoice
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Company info style
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_LEFT
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
    
    # Header with company name (always show text to ensure full name displays)
    # Logo is optional, company name text is always displayed
    company_header = Paragraph(f"<b>{COMPANY_NAME}</b>", title_style)
    
    company_info = f"""
    <b>{COMPANY_NAME}</b><br/>
    {COMPANY_ADDRESS}<br/>
    Email: {COMPANY_EMAIL}<br/>
    Phone: {COMPANY_PHONE}
    """
    
    # Create header table with logo (if available) and company info
    header_data = []
    if logo_path and os.path.exists(logo_path):
        try:
            logo_img = Image(logo_path, width=2*inch, height=0.6*inch)
            # Show both logo and company name
            header_data.append([logo_img, company_header])
        except:
            header_data.append([company_header, ""])
    else:
        header_data.append([company_header, ""])
    
    # Company info table (separate from logo)
    company_info_table = Table([[Paragraph(company_info, company_style), ""]], colWidths=[4*inch, 2.5*inch])
    company_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    # Add header if logo exists, otherwise just company name
    if header_data:
        header_table = Table(header_data, colWidths=[3*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(header_table)
    
    # Add company info
    elements.append(company_info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Invoice title and number
    invoice_title = Paragraph(f"<b>INVOICE</b>", title_style)
    elements.append(invoice_title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice details table
    invoice_date = order.updated_at.strftime("%B %d, %Y") if order.updated_at else datetime.now().strftime("%B %d, %Y")
    order_date = order.created_at.strftime("%B %d, %Y")
    
    invoice_details_data = [
        ["Invoice Number:", order.order_number],
        ["Invoice Date:", invoice_date],
        ["Order Date:", order_date],
        ["Payment Status:", order.payment_status.value.replace("_", " ").title()],
    ]
    
    invoice_details_table = Table(invoice_details_data, colWidths=[2*inch, 4.5*inch])
    invoice_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(invoice_details_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer information
    customer_name = f"{order.customer.first_name} {order.customer.last_name}" if order.customer else "Customer"
    customer_email = order.customer.email if order.customer else ""
    
    customer_data = [
        ["<b>Bill To:</b>", ""],
        [customer_name, ""],
        [customer_email, ""],
        [f"{order.delivery_address}", ""],
        [f"{order.delivery_city}, {order.delivery_state} - {order.delivery_pincode}", ""],
        [f"Phone: {order.phone}", ""],
    ]
    
    customer_table = Table(customer_data, colWidths=[3.25*inch, 3.25*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Order items table
    # Use Unicode rupee symbol - ReportLab should handle it, but use "Rs." as fallback if needed
    # Try using rupee symbol, if it doesn't render, use "Rs."
    rupee_symbol = "₹"
    items_data = [["Item", "Quantity", "Unit Price", "Tax (Rate)", "Final Amount"]]
    
    for item in order.items:
        item_name = item.product_name
        quantity = item.quantity
        unit_price = float(item.customer_unit_price)
        tax_rate = float(item.tax_rate)
        tax_unit_amount = float(item.tax_unit_amount)
        final_total = float(item.total_final_amount)
        tax_text = Paragraph(
            f"{tax_rate:.2f}%<br/>{rupee_symbol}{tax_unit_amount:.2f}/unit",
            styles['Normal']
        )
        # Use Paragraph to ensure proper Unicode rendering
        items_data.append([
            item_name,
            str(quantity),
            Paragraph(f"{rupee_symbol}{unit_price:.2f}", styles['Normal']),
            tax_text,
            Paragraph(f"{rupee_symbol}{final_total:.2f}", styles['Normal'])
        ])
    
    items_table = Table(items_data, colWidths=[2.8*inch, 0.8*inch, 1.2*inch, 1.3*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totals
    subtotal = float(order.total_customer_amount)
    tax_total = float(order.total_tax_amount)
    grand_total = float(order.grand_total_amount)
    total_items = sum(item.quantity for item in order.items)
    rupee_symbol = "₹"
    
    totals_data = [
        ["Subtotal (before tax):", Paragraph(f"{rupee_symbol}{subtotal:.2f}", styles['Normal'])],
        ["Tax:", Paragraph(f"{rupee_symbol}{tax_total:.2f}", styles['Normal'])],
        ["Total Items:", str(total_items)],
        ["", ""],
        [Paragraph("<b>Grand Total:</b>", styles['Normal']), Paragraph(f"<b>{rupee_symbol}{grand_total:.2f}</b>", styles['Normal'])],
    ]
    
    totals_table = Table(totals_data, colWidths=[4.5*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 3), (1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 2), 10),
        ('FONTSIZE', (0, 3), (1, 3), 12),
        ('TEXTCOLOR', (0, 3), (1, 3), colors.HexColor('#2c3e50')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#34495e')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Footer
    footer_text = f"""
    <i>Thank you for your business!</i><br/>
    <i>This is a computer-generated invoice and does not require a signature.</i>
    """
    footer = Paragraph(footer_text, styles['Normal'])
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

