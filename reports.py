from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from database import get_monthly_transactions, get_summary
from datetime import datetime, timedelta
import os

def generate_monthly_report(client_id, business_name, business_reg, owner_name, year, month):
    """Generate a professional PDF report for a specific month"""
    
    filename = f"report_{client_id}_{year}_{str(month).zfill(2)}.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a2e'),
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER,
        spaceAfter=3
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=15,
        spaceAfter=5
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
    )

    # Content
    content = []

    # Header
    content.append(Paragraph(business_name.upper(), title_style))
    content.append(Paragraph(f"Business Registration: {business_reg}", subtitle_style))
    content.append(Paragraph(f"Owner: {owner_name}", subtitle_style))
    content.append(Spacer(1, 20))

    # Report title
    month_name = datetime(year, month, 1).strftime("%B %Y")
    content.append(Paragraph(f"FINANCIAL REPORT — {month_name}", heading_style))
    content.append(Paragraph(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    content.append(Spacer(1, 15))

    # Get transactions
    transactions = get_monthly_transactions(client_id, year, month)
    
    total_income = 0
    total_expenses = 0
    income_rows = []
    expense_rows = []

    for t in transactions:
        type_, desc, amount, date, time = t
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        if type_ == "income":
            total_income += amount
            income_rows.append([formatted_date, desc.capitalize(), f"{amount:,.0f} TZS"])
        else:
            total_expenses += amount
            expense_rows.append([formatted_date, desc.capitalize(), f"{amount:,.0f} TZS"])

    profit = total_income - total_expenses

    # Income table
    content.append(Paragraph("INCOME (MAPATO)", heading_style))
    
    income_data = [["Date", "Description", "Amount"]] + income_rows
    if not income_rows:
        income_data = [["Date", "Description", "Amount"], ["—", "No income recorded", "0 TZS"]]
    income_data.append(["", "TOTAL INCOME", f"{total_income:,.0f} TZS"])

    income_table = Table(income_data, colWidths=[100, 280, 120])
    income_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2e7d32')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(income_table)
    content.append(Spacer(1, 15))

    # Expenses table
    content.append(Paragraph("EXPENSES (MATUMIZI)", heading_style))
    
    expense_data = [["Date", "Description", "Amount"]] + expense_rows
    if not expense_rows:
        expense_data = [["Date", "Description", "Amount"], ["—", "No expenses recorded", "0 TZS"]]
    expense_data.append(["", "TOTAL EXPENSES", f"{total_expenses:,.0f} TZS"])

    expense_table = Table(expense_data, colWidths=[100, 280, 120])
    expense_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fce4ec')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#c62828')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(expense_table)
    content.append(Spacer(1, 15))

    # Summary table
    content.append(Paragraph("SUMMARY (MUHTASARI)", heading_style))
    
    profit_color = colors.HexColor('#2e7d32') if profit >= 0 else colors.HexColor('#c62828')
    profit_label = "NET PROFIT" if profit >= 0 else "NET LOSS"

    summary_data = [
        ["Total Income", f"{total_income:,.0f} TZS"],
        ["Total Expenses", f"{total_expenses:,.0f} TZS"],
        [profit_label, f"{abs(profit):,.0f} TZS"],
    ]

    summary_table = Table(summary_data, colWidths=[380, 120])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, -1), (-1, -1), profit_color),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 30))

    # Signature
    content.append(Paragraph("─" * 60, normal_style))
    content.append(Paragraph(f"Prepared by: {owner_name}", normal_style))
    content.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", normal_style))
    content.append(Spacer(1, 5))
    content.append(Paragraph("This report was automatically generated by Mama Pima Business System.", subtitle_style))

    # Build PDF
    doc.build(content)
    print(f"✅ Report generated: {filename}")
    return filename