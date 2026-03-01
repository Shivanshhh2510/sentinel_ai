import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_pdf(report_data: dict):

    filename = f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(REPORT_DIR, filename)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "SentinelAI - Training Report")
    y -= 30

    c.setFont("Helvetica", 11)
    for k, v in report_data.items():
        c.drawString(40, y, f"{k}: {v}")
        y -= 20

        if y < 60:
            c.showPage()
            y = height - 40

    c.save()
    return path
