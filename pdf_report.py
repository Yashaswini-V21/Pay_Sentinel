from datetime import datetime
import os

from fpdf import FPDF


def _try_setup_unicode_font(pdf):
    candidates = [
        "fonts/NotoSansKannada-Regular.ttf",
        "C:/Windows/Fonts/Nirmala.ttf",
        "C:/Windows/Fonts/NirmalaB.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            pdf.add_font("KAN", "", path)
            return True
    return False


def make_pdf(merchant, results, fp):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    has_unicode_font = _try_setup_unicode_font(pdf)

    # Header
    pdf.set_fill_color(15, 15, 30)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_y(7)
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(226, 75, 74)
    pdf.cell(0, 10, "PaySentinel - Merchant Fraud Report", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(180, 180, 200)
    pdf.cell(0, 7, "AI-Powered UPI Anomaly Detection | English + Kannada", ln=True, align="C")

    # Kannada title line
    pdf.set_y(38)
    if has_unicode_font:
        pdf.set_font("KAN", "", 10)
        title_text = "ವ್ಯಾಪಾರಿ ತಪಾಸಣೆ ವರದಿ | Merchant Audit Report"
    else:
        pdf.set_font("Arial", "I", 10)
        title_text = "Kannada font unavailable | Merchant Audit Report"
    pdf.set_text_color(100, 80, 0)
    pdf.set_fill_color(255, 248, 220)
    pdf.cell(0, 8, title_text, ln=True, align="C", fill=True)

    # Stats
    pdf.set_y(52)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 30, 50)
    pdf.cell(0, 8, f"Merchant: {merchant}  |  Date: {datetime.now().strftime('%d %b %Y')}", ln=True)
    total = len(results)
    fraud = results[results["is_anomaly"] == 1]
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(60, 60, 80)
    pdf.cell(0, 7, f"Total: {total}  |  Suspicious: {len(fraud)}  |  At-risk: Rs.{fraud['amount'].sum():,.0f}", ln=True)
    pdf.ln(4)

    # Flagged table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Flagged Transactions", ln=True)
    pdf.set_fill_color(40, 40, 70)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    for h, w in zip(["Date", "Hour", "Amount", "Score", "Risk"], [35, 18, 35, 28, 28]):
        pdf.cell(w, 8, h, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_text_color(30, 30, 50)
    pdf.set_font("Arial", "", 9)

    for _, row in fraud.sort_values("anomaly_score", ascending=False).head(20).iterrows():
        risk = str(row.get("risk_level", "HIGH"))
        bg = {"CRITICAL": (255, 220, 220), "HIGH": (255, 240, 220)}.get(risk, (255, 255, 230))
        pdf.set_fill_color(*bg)
        for v, w in zip(
            [
                str(row.get("date", ""))[:10],
                f"{int(row.get('hour', 0))}:00",
                f"Rs.{row.get('amount', 0):,.0f}",
                f"{row.get('anomaly_score', 0):.1f}",
                risk,
            ],
            [35, 18, 35, 28, 28],
        ):
            pdf.cell(w, 7, v, border=1, align="C", fill=True)
        pdf.ln()

    # Kannada advisory
    pdf.ln(5)
    pdf.set_fill_color(255, 248, 220)
    pdf.set_text_color(100, 70, 0)
    if has_unicode_font:
        pdf.set_font("KAN", "", 10)
        title = "ಕನ್ನಡ ಸಲಹೆ (Kannada Advisory):"
        lines = [
            "ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರಗಳನ್ನು ತಕ್ಷಣ ನಿಮ್ಮ ಬ್ಯಾಂಕ್‌ಗೆ ತಿಳಿಸಿ.",
            "(Report suspicious transactions to your bank immediately.)",
            "ಸೈಬರ್ ಕ್ರೈಮ್ ಸಹಾಯವಾಣಿ: 1930 | cybercrime.gov.in",
            "Roadmap: Tamil, Telugu, Malayalam, Hindi, Marathi - 800M Indians",
        ]
    else:
        pdf.set_font("Arial", "B", 10)
        title = "Kannada Advisory (font fallback):"
        lines = [
            "Report suspicious transactions to your bank immediately.",
            "Cyber Crime Helpline: 1930 | cybercrime.gov.in",
            "Roadmap: Tamil, Telugu, Malayalam, Hindi, Marathi - 800M Indians",
        ]

    pdf.cell(0, 7, title, ln=True, fill=True)
    if has_unicode_font:
        pdf.set_font("KAN", "", 9)
    else:
        pdf.set_font("Arial", "", 9)
    for line in lines:
        pdf.cell(0, 5, line, ln=True, fill=True)

    out = pdf.output(dest="S")
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return out.encode("latin-1")
