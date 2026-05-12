"""
PaySentinel Voice Alert Tests.
Run: pytest tests/test_voice.py -v
"""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from voice_alerts import alert_html, summary_html, generate_alert_sequence, KN, EN, HI, TA, TE


class TestAlertTemplates:
    @pytest.mark.parametrize("templates,lang", [
        (KN, "Kannada"), (EN, "English"), (HI, "Hindi"), (TA, "Tamil"), (TE, "Telugu")
    ])
    def test_all_risk_levels_exist(self, templates, lang):
        for key in ['critical', 'high', 'medium', 'summary']:
            assert key in templates, f"{lang} missing: {key}"

    @pytest.mark.parametrize("templates,lang", [
        (KN, "Kannada"), (EN, "English"), (HI, "Hindi"), (TA, "Tamil"), (TE, "Telugu")
    ])
    def test_templates_have_placeholders(self, templates, lang):
        for key in ['critical', 'high', 'medium']:
            assert '{amt}' in templates[key]


class TestLanguageRouting:
    @pytest.mark.parametrize("lang", ["English","Kannada","Hindi","Tamil","Telugu","kn"])
    def test_language_produces_audio(self, lang):
        html = alert_html(5000, 14, risk="HIGH", language=lang, autoplay=False)
        assert "audio" in html.lower()

    def test_unknown_language_defaults(self):
        html = alert_html(5000, 14, risk="HIGH", language="Swahili", autoplay=False)
        assert "audio" in html.lower()

    @pytest.mark.parametrize("risk", ["CRITICAL", "HIGH", "MEDIUM", "unknown"])
    def test_all_risk_levels(self, risk):
        html = alert_html(5000, 14, risk=risk, language="English", autoplay=False)
        assert len(html) > 0


class TestSummaryAlerts:
    @pytest.mark.parametrize("count", [0, 1, 5, 100])
    def test_summary_accepts_counts(self, count):
        html = summary_html(count, language="English", autoplay=False)
        assert len(html) > 0


class TestAlertSequence:
    def test_sequence_generates_alerts(self):
        txns = [{'amount': 5000, 'hour': 2, 'risk_level': 'CRITICAL'},
                {'amount': 3000, 'hour': 23, 'risk_level': 'HIGH'}]
        html = generate_alert_sequence(txns, language="English")
        assert html.count("<audio") >= 2

    def test_sequence_caps_at_three(self):
        txns = [{'amount': 100*i, 'hour': i, 'risk_level': 'HIGH'} for i in range(10)]
        html = generate_alert_sequence(txns, language="English")
        assert html.count("<audio") == 3

    def test_empty_sequence(self):
        assert generate_alert_sequence([], language="English") == ""
