"""
PaySentinel: Kannada + English Voice Alerts using gTTS
World's first fraud detection tool to speak Kannada!
"""

import base64
import os
import tempfile
from gtts import gTTS


# ============================================================================
# KANNADA ALERT TEMPLATES
# ============================================================================

KN = {
    "critical": "ಎಚ್ಚರಿಕೆ! ತುರ್ತು ಅಪಾಯ. {amt} ರೂಪಾಯಿ ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ {hour} ಗಂಟೆಗೆ ಪತ್ತೆ.",
    "high": "ಎಚ್ಚರಿಕೆ! {amt} ರೂಪಾಯಿ ಅಸಾಮಾನ್ಯ ವ್ಯವಹಾರ. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ.",
    "medium": "ಗಮನ ಕೊಡಿ. {amt} ರೂಪಾಯಿ ವ್ಯವಹಾರ ಸ್ವಲ್ಪ ಅಸಾಮಾನ್ಯ.",
    "summary": "{count} ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ ಪತ್ತೆ. ವರದಿ ಪರಿಶೀಲಿಸಿ.",
}

# ============================================================================
# ENGLISH ALERT TEMPLATES
# ============================================================================

EN = {
    "critical": "Critical alert. Suspicious transaction of rupees {amt} at {hour} hours.",
    "high": "Warning. Transaction of rupees {amt} at {hour} hours is suspicious.",
    "medium": "Notice. Transaction of rupees {amt} is slightly unusual.",
    "summary": "{count} suspicious transactions detected. Please review.",
}


# ============================================================================
# PRIVATE FUNCTION: Generate Base64 Audio HTML
# ============================================================================

def _html(text, lang, autoplay=True):
    """
    Generate HTML audio player with base64-encoded gTTS audio.
    
    Parameters:
    -----------
    text : str
        Text to convert to speech (Kannada or English)
    lang : str
        Language code: 'kn' for Kannada, 'en' for English
    autoplay : bool
        Whether to autoplay the audio (default: True)
    
    Returns:
    --------
    str
        HTML audio element with embedded base64 audio data
    """
    try:
        # Create temporary file for MP3
        tmp_path = tempfile.mktemp(suffix=".mp3")
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(tmp_path)
        
        # Read MP3 file and base64 encode
        with open(tmp_path, "rb") as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        # Delete temporary file
        os.unlink(tmp_path)
        
        # Generate HTML audio element
        autoplay_attr = "autoplay" if autoplay else ""
        html = f"""<audio {autoplay_attr} controls style="width: 100%; max-width: 400px;">
            <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>"""
        
        return html.strip()
    
    except Exception as e:
        return f"<p style='color: red;'>Audio unavailable: {str(e)}</p>"


# ============================================================================
# PUBLIC FUNCTION: Generate Alert HTML for Individual Transaction
# ============================================================================

def alert_html(amount, hour, risk="HIGH", language="English", autoplay=True):
    """
    Generate voice alert HTML for a suspicious transaction.
    
    Parameters:
    -----------
    amount : float
        Transaction amount in rupees
    hour : int
        Hour of transaction (0-23)
    risk : str
        Risk level: "CRITICAL", "HIGH", "MEDIUM" (default: "HIGH")
    language : str
        Language: "English" or "Kannada" (default: "English")
    autoplay : bool
        Whether to autoplay audio (default: True)
    
    Returns:
    --------
    str
        HTML audio element with embedded speech
    """
    
    # Normalize inputs
    risk = risk.lower()
    amount_str = f"{float(amount):,.0f}"
    hour_int = int(hour)
    
    # Validate and default risk level
    if risk not in ["critical", "high", "medium"]:
        risk = "high"
    
    # Select template and language
    if language.lower() in ["kannada", "ಕನ್ನಡ", "kn"]:
        template = KN[risk]
        lang_code = "kn"
    else:
        template = EN[risk]
        lang_code = "en"
    
    # Format template with transaction details
    text = template.format(amt=amount_str, hour=hour_int)
    
    # Generate and return HTML audio
    return _html(text, lang_code, autoplay=autoplay)


# ============================================================================
# PUBLIC FUNCTION: Generate Summary Alert HTML
# ============================================================================

def summary_html(count, language="English", autoplay=False):
    """
    Generate voice alert HTML for summary of detected frauds.
    
    Parameters:
    -----------
    count : int
        Number of suspicious transactions detected
    language : str
        Language: "English" or "Kannada" (default: "English")
    autoplay : bool
        Whether to autoplay audio (default: False)
    
    Returns:
    --------
    str
        HTML audio element with embedded speech
    """
    
    # Select template and language
    if language.lower() in ["kannada", "ಕನ್ನಡ", "kn"]:
        template = KN["summary"]
        lang_code = "kn"
    else:
        template = EN["summary"]
        lang_code = "en"
    
    # Format template with count
    text = template.format(count=count)
    
    # Generate and return HTML audio
    return _html(text, lang_code, autoplay=autoplay)


# ============================================================================
# PUBLIC FUNCTION: Generate and Save MP3 Alert File
# ============================================================================

def save_alert_mp3(amount, hour, risk="HIGH", language="English", output_path="data/alerts"):
    """
    Generate a voice alert and save as MP3 file.
    
    Parameters:
    -----------
    amount : float
        Transaction amount in rupees
    hour : int
        Hour of transaction (0-23)
    risk : str
        Risk level: "CRITICAL", "HIGH", "MEDIUM"
    language : str
        Language: "English" or "Kannada"
    output_path : str
        Directory to save MP3 file (default: "data/alerts")
    
    Returns:
    --------
    str
        Path to saved MP3 file, or error message if failed
    """
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Normalize inputs
        risk = risk.lower()
        amount_str = f"{float(amount):,.0f}"
        hour_int = int(hour)
        
        # Select template and language
        if language.lower() in ["kannada", "ಕನ್ನಡ", "kn"]:
            template = KN.get(risk, KN["high"])
            lang_code = "kn"
            lang_name = "kannada"
        else:
            template = EN.get(risk, EN["high"])
            lang_code = "en"
            lang_name = "english"
        
        # Format template
        text = template.format(amt=amount_str, hour=hour_int)
        
        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Create filename
        filename = f"{lang_name}_{risk}_{int(amount)}_{hour_int:02d}.mp3"
        filepath = os.path.join(output_path, filename)
        
        # Save to file
        tts.save(filepath)
        
        return filepath
    
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# TEST BLOCK
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔊 PaySentinel Voice Alerts Test")
    print("=" * 70)
    
    # Test English Critical Alert
    print("\n[TEST 1] English Critical Alert...")
    try:
        html_en = alert_html(8200, 2, risk="CRITICAL", language="English", autoplay=False)
        if "audio" in html_en.lower() and "data:audio" in html_en:
            print("  ✅ English: OK")
        else:
            print("  ❌ English: FAIL (invalid HTML)")
    except Exception as e:
        print(f"  ❌ English: FAIL ({e})")
    
    # Test Kannada Critical Alert
    print("\n[TEST 2] Kannada Critical Alert...")
    try:
        html_kn = alert_html(8200, 2, risk="CRITICAL", language="Kannada", autoplay=False)
        if "audio" in html_kn.lower() and "data:audio" in html_kn:
            print("  ✅ Kannada: OK")
        else:
            print("  ❌ Kannada: FAIL (invalid HTML)")
    except Exception as e:
        print(f"  ❌ Kannada: FAIL ({e})")
    
    # Test English Summary
    print("\n[TEST 3] English Summary Alert...")
    try:
        html_sum_en = summary_html(5, language="English", autoplay=False)
        if "audio" in html_sum_en.lower() and "data:audio" in html_sum_en:
            print("  ✅ English Summary: OK")
        else:
            print("  ❌ English Summary: FAIL (invalid HTML)")
    except Exception as e:
        print(f"  ❌ English Summary: FAIL ({e})")
    
    # Test Kannada Summary
    print("\n[TEST 4] Kannada Summary Alert...")
    try:
        html_sum_kn = summary_html(5, language="Kannada", autoplay=False)
        if "audio" in html_sum_kn.lower() and "data:audio" in html_sum_kn:
            print("  ✅ Kannada Summary: OK")
        else:
            print("  ❌ Kannada Summary: FAIL (invalid HTML)")
    except Exception as e:
        print(f"  ❌ Kannada Summary: FAIL ({e})")
    
    # Test Save MP3
    print("\n[TEST 5] Save MP3 Files...")
    try:
        os.makedirs("data/alerts", exist_ok=True)
        path_en = save_alert_mp3(8200, 2, risk="CRITICAL", language="English")
        path_kn = save_alert_mp3(8200, 2, risk="CRITICAL", language="Kannada")
        
        if os.path.exists(path_en) and os.path.exists(path_kn):
            print(f"  ✅ Saved English: {path_en}")
            print(f"  ✅ Saved Kannada: {path_kn}")
        else:
            print("  ❌ FAIL: Files not saved")
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
    
    print("\n" + "=" * 70)
    print("🌍 World's First Kannada Fraud Alert Tool Ready!")
    print("=" * 70)
