import base64
import os
import tempfile

from gtts import gTTS

KN = {
    "critical": "ಎಚ್ಚರಿಕೆ! ತುರ್ತು ಅಪಾಯ. {amt} ರೂಪಾಯಿ ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ {hour} ಗಂಟೆಗೆ ಪತ್ತೆಯಾಗಿದೆ.",
    "high": "ಎಚ್ಚರಿಕೆ! {amt} ರೂಪಾಯಿ ಅಸಾಮಾನ್ಯ ವ್ಯವಹಾರ {hour} ಗಂಟೆಗೆ. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ.",
    "medium": "ಗಮನ ಕೊಡಿ. {amt} ರೂಪಾಯಿ ವ್ಯವಹಾರ ಸ್ವಲ್ಪ ಅಸಾಮಾನ್ಯ.",
    "summary": "{count} ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರಗಳು ಪತ್ತೆ. ವರದಿ ಪರಿಶೀಲಿಸಿ.",
}

EN = {
    "critical": "Critical alert. Suspicious transaction of rupees {amt} detected at {hour} hours.",
    "high": "Warning. Transaction of rupees {amt} at {hour} hours is highly suspicious.",
    "medium": "Notice. Transaction of rupees {amt} is slightly unusual.",
    "summary": "{count} suspicious transactions detected. Please review the report.",
}


def _audio_html(text, lang, autoplay=True):
    try:
        tmp = tempfile.mktemp(suffix=".mp3")
        gTTS(text=text, lang=lang, slow=False).save(tmp)
        with open(tmp, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        os.unlink(tmp)
        ap = "autoplay" if autoplay else ""
        return f'<audio {ap} controls style="width:100%;margin-top:6px"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except Exception as e:
        return f"<p style='color:orange'>Audio unavailable: {e}</p>"


def alert_html(amount, hour, risk="HIGH", language="English", autoplay=True):
    lk = risk.lower()
    lk = lk if lk in ["critical", "high", "medium"] else "high"

    if language == "Kannada":
        text = KN[lk].format(amt=f"{amount:,.0f}", hour=hour)
        lang = "kn"
    else:
        text = EN[lk].format(amt=f"{amount:,.0f}", hour=hour)
        lang = "en"
    return _audio_html(text, lang, autoplay)


def summary_html(count, language="English"):
    text = (KN if language == "Kannada" else EN)["summary"].format(count=count)
    lang = "kn" if language == "Kannada" else "en"
    return _audio_html(text, lang, autoplay=False)
