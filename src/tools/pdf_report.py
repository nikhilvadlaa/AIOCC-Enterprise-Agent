from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

class PDFReportGenerator:
    def __init__(self, output_path="report.pdf"):
        self.output_path = output_path
        self.logger = None

    def attach_logger(self, logger):
        self.logger = logger

    def generate_report(self, insights, reasons, plan, result, trace_id=None):
        c = canvas.Canvas(self.output_path, pagesize=letter)
        width, height = letter

        y = height - 40

        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, y, "AIOCC Insights Report")
        y -= 40

        c.setFont("Helvetica", 12)
        c.drawString(30, y, f"Generated at: {datetime.utcnow().isoformat()}")
        y -= 40

        # Insights
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Insights")
        y -= 20
        c.setFont("Helvetica", 12)
        for k, v in insights.items():
            c.drawString(40, y, f"- {k}: {v}")
            y -= 20

        # Reasons
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Possible Reasons")
        y -= 20
        c.setFont("Helvetica", 12)
        for r in reasons:
            c.drawString(40, y, f"- {r}")
            y -= 20

        # Plan
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Action Plan")
        y -= 20
        c.setFont("Helvetica", 12)
        for p in plan:
            c.drawString(40, y, f"- {p['action']} (confidence: {p['confidence']})")
            y -= 20

        # Results
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Execution Results")
        y -= 20
        c.setFont("Helvetica", 12)
        for r in result:
            c.drawString(40, y, f"- {r}")
            y -= 20

        c.save()

        print(f"[PDF] Report saved to {self.output_path}")

        if self.logger:
            self.logger.log(
                message=f"PDF report written to {self.output_path}",
                agent="PDFReportGenerator",
                trace_id=trace_id
            )
