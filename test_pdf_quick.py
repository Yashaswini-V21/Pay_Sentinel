"""
Quick PDF Generation Test
Run this to verify pdf_report.py is ready for production
"""

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector, engineer, build_fingerprint
from pdf_report import make_pdf

print("=" * 70)
print("🧪 Quick PDF Report Test")
print("=" * 70)

# 1. Generate sample data
print("\n[1] Generating sample data...")
df = generate_merchant_transactions(days=60, seed=42)
df_eng = engineer(df)
fp = build_fingerprint(df_eng)

# 2. Fit detector
print("[2] Fitting detector...")
detector = PaySentinelDetector()
detector.fit(df)

# 3. Run predictions
print("[3] Running predictions...")
results = detector.predict(df)

# 4. Generate PDF
print("[4] Generating PDF...")
pdf_bytes = make_pdf("Raju Kirana Store", results, fp)

# 5. Save to disk
print("[5] Saving to test_output.pdf...")
with open("test_output.pdf", "wb") as f:
    f.write(pdf_bytes)

# Verify and report
file_size = len(pdf_bytes)
print("\n" + "=" * 70)
if file_size > 2000:  # Single-page PDF with table is typically 3-5 KB
    print(f"✅ PDF generated successfully")
    print(f"   File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"   Location: test_output.pdf")
else:
    print(f"❌ PDF seems too small: {file_size} bytes")

print("=" * 70)
print("\n💡 UNICODE FIX:\n")
print("If you get a UnicodeEncodeError with Kannada text in PDFs:")
print("  • Root cause: fpdf2 uses Helvetica font by default (no Unicode)")
print("  • Solution: Use DejaVu fonts via pdf.add_font('DejaVu', '', path)")
print("  • Note: Kannada works in voice_alerts.py (gTTS) - check voice_alerts.py!")
print("  • For PDFs: English text works with stock fonts\n")
