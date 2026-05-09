import base64
import hashlib
import os
import sys
import tempfile
from datetime import datetime
from io import BytesIO

import pandas as pd
import qrcode
from fpdf import FPDF


def _find_font(filename: str) -> str | None:
    """Find a font file cross-platform."""
    candidates = []
    if sys.platform == "win32":
        win_dir = os.environ.get("WINDIR", "C:\\Windows")
        candidates = [
            os.path.join(win_dir, "Fonts", filename),
            os.path.expanduser(f"~/AppData/Local/Microsoft/Windows/Fonts/{filename}"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            f"/Library/Fonts/{filename}",
            f"/System/Library/Fonts/{filename}",
            os.path.expanduser(f"~/Library/Fonts/{filename}"),
        ]
    else:  # Linux
        candidates = [
            f"/usr/share/fonts/truetype/dejavu/{filename}",
            f"/usr/share/fonts/truetype/noto/{filename}",
            f"/usr/local/share/fonts/{filename}",
            os.path.expanduser(f"~/.fonts/{filename}"),
        ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def generate_proof(merchant, txn_row):
    """Generate a cryptographic proof for a fraud detection."""
    ts = datetime.utcnow().isoformat()
    txn_id = str(txn_row.get('transaction_id', 'TXN-UNKNOWN'))
    amt = float(txn_row.get('amount', 0))
    score = float(txn_row.get('anomaly_score', 0))
    raw = f"{merchant}|{txn_id}|{amt:.2f}|{score:.1f}|{ts}"
    proof_hash = hashlib.sha256(raw.encode()).hexdigest()
    return {
        'proof_id': f"PS-{proof_hash[:8].upper()}",
        'hash': proof_hash,
        'timestamp': ts
    }


def make_qr_png(data_str) -> bytes:
    """Generate a QR code PNG as bytes."""
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def make_pdf(merchant: str, results: pd.DataFrame, fp: dict) -> bytes:
    """
    Generate a comprehensive bilingual PDF fraud report.
    
    Parameters:
    -----------
    merchant : str
        Name of the merchant
    results : pd.DataFrame
        Transaction results from detector.predict()
        Must have columns: date, hour, amount, anomaly_score, risk_level, is_anomaly
    fp : dict
        Merchant fingerprint from build_fingerprint()
        Must have keys: hour_min, hour_max, peak_hour, amt_p99
    
    Returns:
    --------
    bytes
        PDF file content as bytes (ready for st.download_button)
    """
    
    # Initialize PDF with DejaVu font for Unicode support
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Try to add DejaVu font (supports Unicode/Kannada), fallback to Helvetica
    font_path = _find_font("DejaVuSans.ttf")
    if font_path:
        try:
            pdf.add_font("DejaVu", "", font_path)
            bold_path = _find_font("DejaVuSans-Bold.ttf")
            if bold_path:
                pdf.add_font("DejaVu", "B", bold_path)
            default_font = "DejaVu"
        except Exception:
            default_font = "Helvetica"
    else:
        default_font = "Helvetica"
    
    pdf.set_font(default_font, "", 11)
    
    # ========================================================================
    # 1. PREMIUM HEADER
    # ========================================================================
    
    # Full-width dark bar
    pdf.set_fill_color(12, 12, 28)
    pdf.rect(0, 0, 210, 40, 'F')
    
    # Title "PAYSENTINEL"
    pdf.set_xy(0, 8)
    pdf.set_font(default_font, "B", 24)
    pdf.set_text_color(226, 75, 74)  # Saffron-Red
    pdf.cell(210, 12, "PAYSENTINEL", ln=True, align="C")
    
    # Subtitle
    pdf.set_xy(0, 20)
    pdf.set_font(default_font, "", 10)
    pdf.set_text_color(180, 180, 200)
    pdf.cell(210, 10, "AI-Powered UPI Fraud Detection Certificate", ln=True, align="C")
    
    # Thin colored line below header (Gradient simulation)
    pdf.set_fill_color(0, 245, 212) # Teal
    pdf.rect(0, 40, 105, 2, 'F')
    pdf.set_fill_color(255, 112, 67) # Saffron
    pdf.rect(105, 40, 105, 2, 'F')
    
    pdf.ln(12)
    
    # ========================================================================
    # 2. MERCHANT SUMMARY BOX
    # ========================================================================
    
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    fraud_mask = results["is_anomaly"] == 1
    fraud_count = int(fraud_mask.sum())
    fraud_amount = float(results[fraud_mask]["amount"].sum()) if fraud_count > 0 else 0.0
    
    # Background Box
    pdf.set_fill_color(20, 20, 40)
    pdf.rect(10, 48, 190, 32, 'F')
    
    pdf.set_xy(15, 52)
    pdf.set_text_color(220, 231, 247)
    pdf.set_font(default_font, "B", 11)
    pdf.cell(100, 6, f"MERCHANT: {merchant.upper()}")
    pdf.set_font(default_font, "", 9)
    pdf.set_text_color(150, 150, 170)
    pdf.cell(80, 6, f"REPORT DATE: {today}", align="R", ln=True)
    
    pdf.set_x(15)
    pdf.set_text_color(220, 231, 247)
    pdf.cell(180, 6, f"TOTAL TXNS: {len(results)}   |   FLAGGED: {fraud_count}   |   AT-RISK: Rs.{fraud_amount:,.0f}", ln=True)
    
    pdf.set_x(15)
    pdf.set_text_color(0, 245, 212)
    pdf.cell(180, 6, f"BASELINE HOURS: {int(fp['hour_min'])}:00-{int(fp['hour_max'])}:00   |   PEAK: {int(fp['peak_hour'])}:00", ln=True)
    
    pdf.ln(12)
    
    # ========================================================================
    # 3. RISK SUMMARY ROW
    # ========================================================================
    
    critical_c = int((results["risk_level"] == "CRITICAL").sum())
    high_c = int((results["risk_level"] == "HIGH").sum())
    medium_c = int((results["risk_level"] == "MEDIUM").sum())
    
    pdf.set_font(default_font, "B", 9)
    box_w = 60
    
    # Critical Box
    pdf.set_fill_color(255, 23, 68)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(box_w, 10, f" CRITICAL: {critical_c}", border=0, fill=True)
    pdf.cell(5, 10, "") # spacer
    
    # High Box
    pdf.set_fill_color(255, 112, 67)
    pdf.cell(box_w, 10, f" HIGH: {high_c}", border=0, fill=True)
    pdf.cell(5, 10, "") # spacer
    
    # Medium Box
    pdf.set_fill_color(255, 193, 7)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(box_w, 10, f" MEDIUM: {medium_c}", border=0, fill=True)
    
    pdf.ln(15)
    
    # ========================================================================
    # 4. FLAGGED TRANSACTIONS TABLE
    # ========================================================================
    
    # Filter and sort flagged transactions
    flagged = results[results["is_anomaly"] == 1].copy()
    flagged = flagged.sort_values("anomaly_score", ascending=False).head(20)
    
    if len(flagged) > 0:
        pdf.set_font(default_font, "B", 9)
        
        # Table header
        pdf.set_fill_color(40, 40, 70)
        pdf.set_text_color(255, 255, 255)
        
        col_widths = [32, 15, 35, 25, 27]
        headers = ["Date", "Hour", "Amount", "Score", "Risk"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align="C", fill=True)
        
        pdf.ln()
        
        # Table rows
        pdf.set_font(default_font, "", 8)
        
        for idx, row in flagged.iterrows():
            risk_level = row["risk_level"]
            
            # Set row background color based on risk level
            if risk_level == "CRITICAL":
                pdf.set_fill_color(255, 215, 215)  # Light red
            elif risk_level == "HIGH":
                pdf.set_fill_color(255, 240, 215)  # Light orange
            else:  # MEDIUM
                pdf.set_fill_color(255, 255, 225)  # Light yellow
            
            pdf.set_text_color(0, 0, 0)
            
            # Date
            pdf.cell(col_widths[0], 7, str(row["date"])[:10], border=1, fill=True)
            
            # Hour
            pdf.cell(col_widths[1], 7, str(int(row["hour"])), border=1, align="C", fill=True)
            
            # Amount
            pdf.cell(col_widths[2], 7, f"Rs.{row['amount']:,.0f}", border=1, align="R", fill=True)
            
            # Score
            pdf.cell(col_widths[3], 7, f"{row['anomaly_score']:.1f}%", border=1, align="C", fill=True)
            
            # Risk Level
            pdf.cell(col_widths[4], 7, str(risk_level), border=1, align="C", fill=True)
            
            pdf.ln()
        
        pdf.ln(8)
        
        # ========================================================================
        # 5. FRAUD CERTIFICATES (QR CODES)
        # ========================================================================
        
        pdf.set_font(default_font, "B", 11)
        pdf.set_text_color(12, 12, 28)
        pdf.cell(190, 8, "FORENSIC FRAUD CERTIFICATES (TOP 3)", ln=True)
        pdf.ln(2)
        
        # Top 3 Critical/High
        top_forensics = flagged.head(3)
        
        for idx, row in top_forensics.iterrows():
            proof = generate_proof(merchant, row)
            qr_bytes = make_qr_png(proof['hash'])
            
            # Draw cert box
            pdf.set_fill_color(248, 249, 250)
            pdf.rect(10, pdf.get_y(), 190, 30, 'F')
            
            # QR
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(qr_bytes)
                tmp_path = tmp.name
            
            curr_y = pdf.get_y()
            try:
                pdf.image(tmp_path, x=12, y=curr_y+2.5, w=25, h=25)
            except Exception as e:
                import logging
                logging.getLogger("paysentinel.pdf").warning(f"[PDF] QR image embed failed: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            # Details
            pdf.set_xy(40, curr_y+4)
            pdf.set_font(default_font, "B", 10)
            pdf.set_text_color(226, 75, 74)
            pdf.cell(100, 5, f"CERTIFICATE: {proof['proof_id']}", ln=True)
            
            pdf.set_x(40)
            pdf.set_font(default_font, "", 8)
            pdf.set_text_color(80, 80, 100)
            pdf.cell(150, 4, f"TXN Amount: Rs.{row['amount']:,.2f} | Risk: {row['risk_level']} ({row['anomaly_score']:.1f}%)", ln=True)
            
            pdf.set_x(40)
            pdf.cell(150, 4, f"Hash: {proof['hash'][:48]}...", ln=True)
            
            pdf.set_x(40)
            pdf.cell(150, 4, f"Issued At: {proof['timestamp'][:19]} UTC", ln=True)
            
            pdf.set_y(curr_y + 32)
            
        pdf.ln(5)
    
    # ========================================================================
    # 5. RECOMMENDATIONS
    # ========================================================================
    
    pdf.set_font(default_font, "B", 10)
    pdf.set_text_color(226, 75, 74)
    pdf.cell(190, 7, "Recommendations", ln=True)
    
    pdf.set_font(default_font, "", 9)
    pdf.set_text_color(0, 0, 0)
    
    recommendations = [
        "1. Contact your bank immediately for CRITICAL transactions",
        "2. Verify flagged transactions directly with the sender",
        "3. File complaint at cybercrime.gov.in for confirmed fraud",
        "4. Block unknown senders making late-night large transfers",
    ]
    
    for rec in recommendations:
        pdf.multi_cell(190, 5, f"   {rec}")
    
    pdf.ln(2)
    
    # ========================================================================
    # 7. KANNADA ADVISORY SECTION
    # ========================================================================
    
    if fraud_count == 0:
        kannada_msg = "ನಿಮ್ಮ ಅಂಗಡಿ ಸುರಕ್ಷಿತವಾಗಿದೆ. ಯಾವುದೇ ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ ಪತ್ತೆಯಾಗಿಲ್ಲ."
    elif fraud_count <= 2:
        kannada_msg = "ಕೆಲವು ಸಂಶயಾಸ್ಪದ ವ್ಯವಹಾರಗಳು ಪತ್ತೆಯಾಗಿವೆ. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ."
    else:
        kannada_msg = "ಎಚ್ಚರಿಕೆ! ಅನೇಕ ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರಗಳು. ತಕ್ಷಣ ಬ್ಯಾಂಕ್ಗೆ ಸಂಪರ್ಕಿಸಿ."

    pdf.set_fill_color(255, 248, 220)
    pdf.set_xy(10, pdf.get_y())
    pdf.set_font(default_font, "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 8, "ಕನ್ನಡ ಸಲಹೆ (KANNADA ADVISORY)", ln=True, align="L", fill=True)
    
    pdf.set_font(default_font, "", 9)
    pdf.multi_cell(190, 6, kannada_msg)
    pdf.ln(2)
    
    pdf.set_font(default_font, "B", 9)
    pdf.cell(190, 6, "IMPORTANT ADVISORY (Safety Tips)", ln=True)
    pdf.set_font(default_font, "", 8)
    
    advisory = [
        "- Report suspicious transactions to your bank immediately (Helpline: 1930)",
        "- Do NOT share OTP or payment passwords with anyone",
        "- Verify sender identity before confirming large transfers",
        "- File complaints at cybercrime.gov.in for confirmed fraud",
    ]
    
    for line in advisory:
        pdf.multi_cell(190, 4, line)
    
    pdf.ln(5)
    
    # ========================================================================
    # 7. FOOTER
    # ========================================================================
    
    pdf.set_font(default_font, "", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(190, 4, 
                   "PaySentinel | BluePrint 2026 | Not a substitute for legal advice",
                   align="C")
    
    # ========================================================================
    # RETURN PDF AS BYTES
    # ========================================================================
    
    output = pdf.output(dest="S")
    if isinstance(output, bytes):
        return output
    elif isinstance(output, bytearray):
        return bytes(output)
    else:
        return output.encode("latin-1")


def save_pdf(merchant: str, results: pd.DataFrame, fp: dict, output_path: str = None) -> str:
    """
    Generate PDF and save to disk.
    
    Parameters:
    -----------
    merchant : str
        Merchant name
    results : pd.DataFrame
        Transaction results
    fp : dict
        Merchant fingerprint
    output_path : str
        Directory to save PDF (default: root/data/reports)
    
    Returns:
    --------
    str
        Path to saved PDF file
    """
    import os
    
    if output_path is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(root, "data", "reports")
    
    os.makedirs(output_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paysentinel_report_{timestamp}.pdf"
    filepath = os.path.join(output_path, filename)
    
    pdf_bytes = make_pdf(merchant, results, fp)
    
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
    
    return filepath


# ============================================================================
# TEST BLOCK
# ============================================================================

if __name__ == "__main__":
    from generate_data import generate_merchant_transactions
    from model import PaySentinelDetector, engineer, build_fingerprint
    
    print("=" * 70)
    print("📄 PaySentinel PDF Report Generator Test")
    print("=" * 70)
    
    # Generate test data
    print("\n[TEST 1] Generating sample data...")
    try:
        df = generate_merchant_transactions(days=60, seed=42)
        df_eng = engineer(df)
        fp = build_fingerprint(df_eng)
        print("  ✅ Sample data generated")
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        exit(1)
    
    # Train detector
    print("\n[TEST 2] Training detector...")
    try:
        detector = PaySentinelDetector()
        detector.fit(df)
        print("  ✅ Detector trained")
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        exit(1)
    
    # Generate predictions
    print("\n[TEST 3] Making predictions...")
    try:
        results = detector.predict(df)
        print(f"  ✅ Predictions made ({(results['is_anomaly'] == 1).sum()} anomalies)")
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        exit(1)
    
    # Generate PDF
    print("\n[TEST 4] Generating PDF report...")
    try:
        pdf_bytes = make_pdf("Test Kirana Store", results, fp)
        print(f"  ✅ PDF generated ({len(pdf_bytes)} bytes)")
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        exit(1)
    
    # Save PDF
    print("\n[TEST 5] Saving PDF to disk...")
    try:
        filepath = save_pdf("Test Kirana Store", results, fp)
        print(f"  ✅ PDF saved: {filepath}")
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        exit(1)
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\n🎉 PDF report generation is ready for the HTML dashboard!\n")


