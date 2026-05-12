"""
PaySentinel: Kannada + English Voice Alerts using gTTS
World's first fraud detection tool to speak Kannada!
"""

import base64
import os
import tempfile
import time
import logging
import hashlib
from functools import lru_cache
from gtts import gTTS

logger = logging.getLogger("paysentinel.voice")
if not logger.handlers:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)


# ============================================================================
# OFFLINE TTS ENGINE (pyttsx3) — fallback when gTTS / internet is unavailable
# ============================================================================

_PYTTSX3_ENGINE = None
_PYTTSX3_AVAILABLE = False

def _init_pyttsx3():
    global _PYTTSX3_ENGINE, _PYTTSX3_AVAILABLE
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Slightly slower for clarity
        engine.setProperty('volume', 0.9)
        _PYTTSX3_ENGINE = engine
        _PYTTSX3_AVAILABLE = True
        logger = __import__('logging').getLogger('paysentinel.voice')
        logger.info("[VOICE] pyttsx3 offline engine initialized")
    except Exception as e:
        _PYTTSX3_AVAILABLE = False

# Initialize on module load
_init_pyttsx3()


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
# HINDI ALERT TEMPLATES
# ============================================================================

HI = {
    "critical": "चेतावनी! गंभीर खतरा। {amt} रुपये का संदिग्ध लेनदेन {hour} बजे पाया गया।",
    "high": "चेतावनी! {amt} रुपये का असामान्य लेनदेन। कृपया जांच करें।",
    "medium": "ध्यान दें। {amt} रुपये का लेनदेन थोड़ा असामान्य है।",
    "summary": "{count} संदिग्ध लेनदेन पाए गए। कृपया समीक्षा करें।",
}

# ============================================================================
# TAMIL ALERT TEMPLATES
# ============================================================================

TA = {
    "critical": "எச்சரிக்கை! {amt} ரூபாய் பரிவர்த்தனை மிகவும் சந்தேகமானது.",
    "high": "கவனிக்கவும். {amt} ரூபாய் அசாதாரண பரிவர்த்தனை.",
    "medium": "கவனிக்கவும். {amt} ரூபாய் பரிவர்த்தனை சற்று அசாதாரணமானது.",
    "summary": "{count} சந்தேகமான பரிவர்த்தனைகள் கண்டறியப்பட்டன."
}

# ============================================================================
# TELUGU ALERT TEMPLATES
# ============================================================================

TE = {
    "critical": "హెచ్చరిక! ₹{amt} అనుమానాస్పద లావాదేవీ.",
    "high": "జాగ్రత్త. ₹{amt} అసాధారణ లావాదేవీ.",
    "medium": "దయచేసి గమనించండి. ₹{amt} లావాదేవీ.",
    "summary": "{count} అనుమానాస్పద లావాదేవీలు కనుగొనబడ్డాయి."
}

_audio_cache: dict[str, str] = {}  # key: hash(text+lang), value: base64 audio


# ============================================================================
# PRIVATE FUNCTION: Generate Base64 Audio HTML
# ============================================================================

# ============================================================================
# OFFLINE FALLBACK: Generate WAV via pyttsx3 when gTTS is unavailable
# ============================================================================

def _html_offline(text: str, lang: str) -> str:
    """Generate voice alert using offline pyttsx3 when gTTS fails."""
    if not _PYTTSX3_AVAILABLE or _PYTTSX3_ENGINE is None:
        return f'<p style="color:rgba(220,231,247,0.4);font-size:11px">Voice unavailable (offline mode)</p>'
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            _PYTTSX3_ENGINE.save_to_file(text, tmp_path)
            _PYTTSX3_ENGINE.runAndWait()
            # Convert WAV to base64
            with open(tmp_path, 'rb') as f:
                audio_b64 = base64.b64encode(f.read()).decode('utf-8')
        finally:
            if os.path.exists(tmp_path): os.unlink(tmp_path)
        return (f'<div style="background:rgba(255,112,67,0.05);'
                f'border:1px solid rgba(255,112,67,0.2);border-radius:12px;padding:8px 12px">'
                f'<div style="font-size:9px;color:rgba(255,112,67,0.7);margin-bottom:4px">'
                f'OFFLINE VOICE</div>'
                f'<audio controls style="width:100%;height:32px">'
                f'<source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">'
                f'</audio></div>')
    except Exception as e:
        return f'<p style="font-size:11px;color:rgba(220,231,247,0.4)">Voice unavailable: {e}</p>'


@lru_cache(maxsize=128)
def _html(text, lang, autoplay=True, slow=False):
    """
    Generate HTML audio player with base64-encoded gTTS audio.
    Resilient with retry logic, custom caching, and secure temp files.
    """
    # 1. Check custom audio cache
    cache_key = hashlib.md5(f"{text}_{lang}".encode()).hexdigest()
    if cache_key in _audio_cache:
        audio_base64 = _audio_cache[cache_key]
    else:
        max_retries = 2
        audio_base64 = None
        
        for attempt in range(max_retries):
            tmp_path = None
            try:
                # 2. Create temporary file for MP3 securely
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tmp_path = tmp.name
                
                # 3. Generate speech using gTTS
                tts = gTTS(text=text, lang=lang, slow=slow)
                tts.save(tmp_path)
                
                # 4. Read MP3 file and base64 encode
                with open(tmp_path, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode("utf-8")
                
                # 5. Populate cache with simple eviction
                _audio_cache[cache_key] = audio_base64
                if len(_audio_cache) > 50:
                    oldest = next(iter(_audio_cache))
                    del _audio_cache[oldest]
                
                # Generate HTML audio element with premium styling
                autoplay_attr = "autoplay" if autoplay else ""
                lang_label = {
                    "kn": "ಕನ್ನಡ ಎಚ್ಚರಿಕೆ",
                    "hi": "हिंदी चेतावनी",
                    "ta": "தமிழ் எச்சரிக்கை",
                    "te": "తెలుగు హెచ్చరిక",
                    "en": "VOICE ALERT"
                }.get(lang, "VOICE ALERT")

                return (
                    f'<div style="background:rgba(0,245,212,0.05);border:1px solid rgba(0,245,212,0.15);'
                    f'border-radius:12px;padding:10px 12px;margin:4px 0">'
                    f'<div style="font-family:Chakra Petch, sans-serif;font-size:9px;letter-spacing:.2em;'
                    f'text-transform:uppercase;color:rgba(0,245,212,0.6);margin-bottom:6px">'
                    f'{lang_label}'
                    f'</div>'
                    f'<audio {autoplay_attr} controls style="width:100%;height:36px;'
                    f'border-radius:8px;outline:none">'
                    f'<source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">'
                    f'</audio></div>'
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.warning(f"[VOICE] gTTS failed after {max_retries} attempts, using offline fallback: {e}")
                    return _html_offline(text, lang)
                time.sleep(0.5)
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

        if not audio_base64:
            return _html_offline(text, lang)

    # 6. Generate HTML audio element with premium styling
    autoplay_attr = "autoplay" if autoplay else ""
    lang_label = {
        "kn": "ಕನ್ನಡ ಎಚ್ಚರಿಕೆ",
        "hi": "हिंदी चेतावनी",
        "ta": "தமிழ் எச்சரிக்கை",
        "te": "తెలుగు హెచ్చరిక",
        "en": "VOICE ALERT"
    }.get(lang, "VOICE ALERT")

    return (
        f'<div style="background:rgba(0,245,212,0.05);border:1px solid rgba(0,245,212,0.15);'
        f'border-radius:12px;padding:10px 12px;margin:4px 0">'
        f'<div style="font-family:Chakra Petch, sans-serif;font-size:9px;letter-spacing:.2em;'
        f'text-transform:uppercase;color:rgba(0,245,212,0.6);margin-bottom:6px">'
        f'{lang_label}'
        f'</div>'
        f'<audio {autoplay_attr} controls style="width:100%;height:36px;'
        f'border-radius:8px;outline:none">'
        f'<source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">'
        f'</audio></div>'
    )


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
    elif language.lower() in ["hindi", "हिन्दी", "hi"]:
        template = HI[risk]
        lang_code = "hi"
    elif language.lower() in ["tamil", "தமிழ்", "ta"]:
        template = TA.get(risk, TA["high"])
        lang_code = "ta"
    elif language.lower() in ["telugu", "తెలుగు", "te"]:
        template = TE.get(risk, TE["high"])
        lang_code = "te"
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
    elif language.lower() in ["hindi", "हिन्दी", "hi"]:
        template = HI["summary"]
        lang_code = "hi"
    elif language.lower() in ["tamil", "தமிழ்", "ta"]:
        template = TA["summary"]
        lang_code = "ta"
    elif language.lower() in ["telugu", "తెలుగు", "te"]:
        template = TE["summary"]
        lang_code = "te"
    else:
        template = EN["summary"]
        lang_code = "en"
    
    # Format template with count
    text = template.format(count=count)
    
    # Generate and return HTML audio
    return _html(text, lang_code, autoplay=autoplay)


def generate_alert_sequence(transactions, language):
    """Generate a sequence of voice alerts for multiple flagged transactions."""
    alerts = []
    for txn in transactions[:3]:  # max 3 alerts in sequence
        amount = float(txn.get('amount', 0))
        hour = int(txn.get('hour', 0))
        risk = str(txn.get('risk_level', 'HIGH')).lower()
        html = alert_html(amount, hour, risk=risk, language=language, autoplay=False)
        alerts.append(html)
    return '\n'.join(alerts)


# ============================================================================
# PUBLIC FUNCTION: Generate and Save MP3 Alert File
# ============================================================================

def save_alert_mp3(amount, hour, risk="HIGH", language="English", output_path=None):
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
        Directory to save MP3 file (default: root/data/alerts)
    
    Returns:
    --------
    str
        Path to saved MP3 file, or error message if failed
    """
    
    try:
        # Create output directory if it doesn't exist
        if output_path is None:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_path = os.path.join(root, "data", "alerts")
            
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
