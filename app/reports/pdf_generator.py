from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf(report_data, output_path):

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 40

    def write_line(text):
        nonlocal y
        c.drawString(40, y, text)
        y -= 18
        if y < 40:
            c.showPage()
            y = height - 40

    write_line("SentinelAI - Automated Business Intelligence Report")
    write_line(f"Generated: {datetime.now()}")
    write_line("-" * 80)

    summary = report_data["summary"]
    automl = report_data["automl"]

    write_line("DATASET SUMMARY")
    write_line(f"Rows: {summary['rows']}")
    write_line(f"Columns: {summary['columns']}")
    write_line("")

    write_line("MODEL LEADERBOARD")
    for model, score in automl["leaderboard"].items():
        write_line(f"{model}: {score}")

    write_line("")
    write_line(f"Best Model: {automl['best_model']}")
    write_line(f"Reliability Score: {automl['model_reliability_score']}")

    write_line("")
    write_line("DATASET WARNINGS")
    for w in automl["dataset_insights"]["warnings"]:
        write_line(f"- {w}")

    write_line("")
    write_line("TOP INFLUENTIAL FEATURES")
    for f in automl["explainability"]["top_features"]:
        write_line(f"{f['feature']} : {f['impact']}")

    write_line("")
    write_line("END OF REPORT")

    c.save()
