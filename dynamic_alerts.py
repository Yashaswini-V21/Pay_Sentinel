"""
PaySentinel Dynamic Alert Message Generator

Generates human, contextual alerts based on specific fraud patterns detected.
Integrates with the hybrid ML model to provide reason-aware voice alerts.

Features:
- Detects fraud pattern (velocity, structuring, late-night, etc.)
- Pulls merchant history (normal transaction size, hours, senders)
- Generates alert in merchant's preferred language
- Adds emotional urgency matching risk level
- Includes educational element ("This is called...")
"""

import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
from enum import Enum

# ════════════════════════════════════════════════════════════════════════════════
# ALERT PATTERNS & TRIGGERS
# ════════════════════════════════════════════════════════════════════════════════

class FraudPattern(Enum):
    """Fraud detection pattern types"""
    VELOCITY_ATTACK = "velocity"           # 3+ txns from same sender in 30min
    STRUCTURING = "structuring"            # Large amounts, repeated
    LATE_NIGHT = "late_night"              # After-hours transaction
    NEW_SENDER = "new_sender"              # Unknown UPI handle
    AMOUNT_ANOMALY = "amount_anomaly"      # Way above merchant's normal
    ROUND_AMOUNT = "round_amount"          # Unusual round numbers
    SENDER_SPOOFING = "spoofing"           # Known sender, but different device
    MERCHANT_INACTIVE = "inactive"         # Transaction during non-working hours


class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = (0, 30, "low")
    MEDIUM = (30, 60, "medium")
    HIGH = (60, 85, "high")
    CRITICAL = (85, 100, "critical")
    
    @classmethod
    def from_score(cls, score: float):
        """Get risk level from risk score (0-100)"""
        for level in cls:
            if level.value[0] <= score < level.value[1]:
                return level
        return cls.CRITICAL


# ════════════════════════════════════════════════════════════════════════════════
# CONTEXT GATHERING
# ════════════════════════════════════════════════════════════════════════════════

class MerchantContext:
    """Captures merchant's baseline behavior for personalized alerts"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Parameters:
        df: Historical transactions with columns:
            - amount, hour, sender, date, is_biz_hours
        """
        self.df = df
        self.avg_amount = df['amount'].mean()
        self.max_amount = df['amount'].max()
        self.normal_hours = df[df['is_biz_hours'] == 1]['hour'].mode()
        self.unique_senders = df['sender'].nunique()
        self.vel_1h = len(df[df['hour'] == datetime.now().hour])  # This hour
        
    def get_amount_context(self, new_amount: float) -> str:
        """Describe how unusual the amount is"""
        ratio = new_amount / self.avg_amount
        
        if ratio > 20:
            return f"This is {ratio:.0f}x bigger than your normal transaction"
        elif ratio > 10:
            return f"This is {ratio:.0f} times larger than your average sale"
        elif ratio > 5:
            return f"This is way bigger than your typical transactions"
        elif ratio > 2:
            return f"This is roughly double your usual amount"
        else:
            return f"This is higher than you normally get"
    
    def get_time_context(self, hour: int) -> str:
        """Describe timing anomaly"""
        if hour < 6:
            return f"at {hour}:00 AM—middle of the night for you"
        elif hour > 22:
            return f"at {hour}:00 PM—after your usual hours"
        elif hour < 9:
            return f"at {hour}:00 AM—before your shop opens"
        elif hour > 21:
            return f"at {hour}:00 PM—after your shop closes"
        else:
            return f"at {hour}:00, which is unusual for you"
    
    def get_sender_context(self, sender: str, is_new: bool) -> str:
        """Describe sender anomaly"""
        if is_new:
            return f"from someone you've never traded with before"
        else:
            return f"from {sender}, but something seems different"


# ════════════════════════════════════════════════════════════════════════════════
# DYNAMIC MESSAGE TEMPLATES
# ════════════════════════════════════════════════════════════════════════════════

class AlertMessageGenerator:
    """Generates personalized alert messages based on fraud pattern"""
    
    def __init__(self, language: str = "en"):
        """
        Parameters:
        language: "en" (English), "kn" (Kannada), "hi" (Hindi), "ta" (Tamil)
        """
        self.language = language
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load language-specific templates"""
        if self.language == "en":
            return EN_TEMPLATES
        elif self.language == "kn":
            return KN_TEMPLATES
        elif self.language == "hi":
            return HI_TEMPLATES
        else:
            return EN_TEMPLATES  # Default to English
    
    def generate(
        self,
        merchant_name: str,
        amount: float,
        hour: int,
        risk_score: float,
        fraud_pattern: FraudPattern,
        merchant_context: MerchantContext,
        sender_name: str = "Unknown",
        count: int = 1,
        time_window_min: int = 0,
    ) -> str:
        """
        Generate personalized alert message
        
        Parameters:
        - merchant_name: Customer's name
        - amount: Transaction amount in rupees
        - hour: Hour of transaction (0-23)
        - risk_score: ML model risk score (0-100)
        - fraud_pattern: Detected pattern
        - merchant_context: MerchantContext instance with baseline
        - sender_name: UPI ID of sender
        - count: Number of transactions (for velocity)
        - time_window_min: Time window for velocity (minutes)
        
        Returns:
        Personalized alert text ready for TTS
        """
        
        risk_level = RiskLevel.from_score(risk_score)
        template = self._get_template(fraud_pattern, risk_level)
        
        # Build context strings
        amount_context = merchant_context.get_amount_context(amount)
        time_context = merchant_context.get_time_context(hour)
        sender_context = merchant_context.get_sender_context(sender_name, count == 1)
        
        # Format message
        message = template.format(
            merchant_name=merchant_name,
            amount=int(amount),
            hour=hour,
            amount_context=amount_context,
            time_context=time_context,
            sender_context=sender_context,
            sender_name=sender_name,
            count=count,
            time_window=time_window_min,
            risk_level=risk_level.name,
        )
        
        return message
    
    def _get_template(self, pattern: FraudPattern, risk_level: RiskLevel) -> str:
        """Select appropriate template"""
        template_key = f"{pattern.value}_{risk_level.value[2]}"
        return self.templates.get(
            template_key,
            self.templates.get("generic_alert", "Alert! Unusual transaction detected.")
        )


# ════════════════════════════════════════════════════════════════════════════════
# ENGLISH TEMPLATES
# ════════════════════════════════════════════════════════════════════════════════

EN_TEMPLATES = {
    # VELOCITY ATTACK
    "velocity_low": (
        "Hi {merchant_name}. We noticed {count} payments from the same person "
        "in just {time_window} minutes. That's quick! Everything okay? "
        "Just checking. Let us know if something feels off."
    ),
    "velocity_medium": (
        "{merchant_name}, we need your attention. We're seeing {count} payments "
        "from {sender_name} in only {time_window} minutes. That pattern looks unusual. "
        "Is this someone you authorized? Please verify."
    ),
    "velocity_high": (
        "ALERT! {merchant_name}, this is suspicious. {count} transactions from "
        "{sender_name} in {time_window} minutes. This looks like a scam technique "
        "called 'structuring.' DO NOT accept more payments from this sender. "
        "Block them now."
    ),
    "velocity_critical": (
        "CRITICAL ALERT! {merchant_name}, YOUR ACCOUNT IS UNDER ATTACK. "
        "{count} fraudulent transactions in {time_window} minutes. "
        "They are draining your account. BLOCK THIS SENDER NOW. "
        "CALL YOUR BANK IMMEDIATELY. Amount at risk: ₹{amount}."
    ),
    
    # STRUCTURING (Large amounts, repeat)
    "structuring_medium": (
        "{merchant_name}, just noticed something. Someone sent ₹{amount} {time_context}. "
        "{amount_context}. {sender_context}. "
        "Is this planned, or does it feel odd? Let me know."
    ),
    "structuring_high": (
        "WARNING: {merchant_name}, we detected suspicious activity. ₹{amount} {time_context}. "
        "{amount_context}. This could be a scam. "
        "REJECT this transaction. Do NOT accept or transfer money."
    ),
    "structuring_critical": (
        "CRITICAL! {merchant_name}, URGENT. ₹{amount} from an unknown sender {time_context}. "
        "{amount_context}. This is extremely suspicious. "
        "BLOCK IMMEDIATELY. If already accepted, CALL YOUR BANK NOW."
    ),
    
    # LATE NIGHT
    "late_night_low": (
        "Hi {merchant_name}. Quick note: Payment of ₹{amount} came in {time_context}. "
        "A bit unusual, but looks normal otherwise. Just wanted to flag it."
    ),
    "late_night_medium": (
        "{merchant_name}, we noticed ₹{amount} {time_context}. You usually sleep then. "
        "If this is legitimate, great. If not, let us know."
    ),
    "late_night_high": (
        "ALERT: {merchant_name}, ₹{amount} {time_context}. This is when you're typically off. "
        "Combined with the amount being unusual, this looks risky. "
        "DO NOT ACCEPT. Verify with the sender first."
    ),
    
    # NEW SENDER
    "new_sender_low": (
        "Hi {merchant_name}. New customer alert: ₹{amount} from someone trading with you "
        "for the first time. Looks normal, but you might want to check them out."
    ),
    "new_sender_medium": (
        "{merchant_name}, we're seeing ₹{amount} from a first-time sender {time_context}. "
        "Something feels slightly off. Can you verify this is real?"
    ),
    "new_sender_high": (
        "ALERT: {merchant_name}, ₹{amount} from an unknown sender {time_context}. "
        "{amount_context}. This is suspicious. "
        "DO NOT ACCEPT until you verify directly with the buyer."
    ),
    
    # AMOUNT ANOMALY
    "amount_anomaly_medium": (
        "{merchant_name}, unusual payment: ₹{amount}. {amount_context}. "
        "Everything else looks normal, but this size is rare for you. "
        "Just making sure this was planned?"
    ),
    "amount_anomaly_high": (
        "WARNING: {merchant_name}, ₹{amount} from {sender_name}. "
        "{amount_context}. This is extremely unusual. "
        "VERIFY this is real before accepting. This could be fraud."
    ),
    "amount_anomaly_critical": (
        "CRITICAL ALERT! {merchant_name}, ₹{amount}—THIS IS A RED FLAG. "
        "{amount_context}. REJECT immediately. "
        "This is likely a scam. DO NOT accept this money."
    ),
    
    # Generic fallback
    "generic_alert": (
        "{merchant_name}, unusual transaction detected: ₹{amount} from {sender_name} "
        "{time_context}. Risk level: {risk_level}. "
        "Please verify this is legitimate before accepting."
    ),
}


# ════════════════════════════════════════════════════════════════════════════════
# KANNADA TEMPLATES
# ════════════════════════════════════════════════════════════════════════════════

KN_TEMPLATES = {
    # VELOCITY ATTACK
    "velocity_low": (
        "ಸ್ವಾಗತ {merchant_name}. ನಾವು ಅದೇ ವ್ಯಕ್ತಿಯಿಂದ ಕೇವಲ {time_window} ನಿಮಿಷಗಳಲ್ಲಿ "
        "{count} ಪಾವತಿ ನೋಡುತ್ತಿದ್ದೇವೆ. ಅದು ವೇಗವಾಗಿದೆ! ಎಲ್ಲಾ ಸರಿ? "
        "ಕೇವಲ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇವೆ. ಯಾವುದೇ ಜಿಜ್ಞಾಸೆ ಬಂದರೆ ನಮಗೆ ತಿಳಿಸಿ."
    ),
    "velocity_medium": (
        "{merchant_name}, ನಿಮ್ಮ ಗಮನ ಬೇಕು. ನಾವು ಕೇವಲ {time_window} ನಿಮಿಷಗಳಲ್ಲಿ "
        "{sender_name} ಬಿಡುವಿನಿಂದ {count} ಪಾವತಿ ನೋಡುತ್ತಿದ್ದೇವೆ. ಆ ಮಾದರಿ ಅಸಾಮಾನ್ಯ. "
        "ಇದು ನೀವು ಅನುಮೋದಿಸಿದ ವ್ಯಕ್ತಿ? ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ."
    ),
    "velocity_high": (
        "ಎಚ್ಚರಣೆ! {merchant_name}, ಇದು ಅನುಮಾನಾಸ್ಪದ. {count} ವಹನೆ {sender_name} "
        "ಬಿಡುವಿನಿಂದ {time_window} ನಿಮಿಷಗಳಲ್ಲಿ. ಇದು ರಚನೆ ಎಂಬ ವಂಚನೆ ತಂತ್ರ ತೋರುತ್ತದೆ. "
        "ಈ ಪೋಷಕರಿಂದ ಹೆಚ್ಚಿನ ಪಾವತಿ ಸ್ವೀಕರಿಸಬೇಡಿ. ಈಗಲೇ ನಿರ್ಬಂಧಿಸಿ."
    ),
    "velocity_critical": (
        "ನಿರ್ಣಾಯಕ ಎಚ್ಚರಣೆ! {merchant_name}, ನಿಮ್ಮ ಖಾತೆ ದಾಳಿಗೆ ಗುರಿ. "
        "{time_window} ನಿಮಿಷಗಳಲ್ಲಿ {count} ವಂಚನೆಗ್ರಾಹಿ ವಹನೆ. "
        "ಅವರು ನಿಮ್ಮ ಖಾತೆಯನ್ನು ಸೂತ್ರ ಮಾಡುತ್ತಿದ್ದಾರೆ. ಈ ಪೋಷಕರನ್ನು ತಕ್ಷಣ ನಿರ್ಬಂಧಿಸಿ. "
        "ನಿಮ್ಮ ಬ್ಯಾಂಕಿಗೆ ಈಗ ಕರೆ ಮಾಡಿ. ಅಪಾಯದಲ್ಲಿರುವ ಮೊತ್ತ: ₹{amount}."
    ),
    
    # STRUCTURING
    "structuring_medium": (
        "{merchant_name}, ಏನೋ ಗಮನಕ್ಕೆ ಬಂದಿದೆ. ಯಾರೋ {time_context} ₹{amount} ಕಳುಹಿಸಿದ್ದಾರೆ. "
        "{amount_context}. {sender_context}. "
        "ಇದು ಯೋಜನೆ ಮಾಡಿದ್ದಾ, ಅಥವಾ ಏನೋ ಅಸಾಮಾನ್ಯ ತೋರುತ್ತದೆ? ನಮಗೆ ತಿಳಿಸಿ."
    ),
    "structuring_high": (
        "ಎಚ್ಚರಣೆ: {merchant_name}, ನಾವು ಅನುಮಾನಾಸ್ಪದ ಚಟುವಟಿಕೆ ಕಂಡೆವು. "
        "{time_context} ₹{amount}. {amount_context}. ಇದು ವಂಚನೆ ಆಗಿರಬಹುದು. "
        "ಈ ವಹನೆಯನ್ನು ತಿರಸ್ಕರಿಸಿ. ಹಣ ಸ್ವೀಕರಿಸಬೇಡಿ ಅಥವಾ ವಹಿಸಬೇಡಿ."
    ),
    
    # Generic fallback
    "generic_alert": (
        "{merchant_name}, ಅಸಾಮಾನ್ಯ ವಹನೆ ಸನ್ನಿವೇಶಿಸಿದೆ: {time_context} "
        "{sender_name} ಬಿಡುವಿನಿಂದ ₹{amount}. ಅಪಾಯ ಮಾತ್ರೆ: {risk_level}. "
        "ದಯವಿಟ್ಟು ಸ್ವೀಕರಿಸುವ ಮೊದಲು ಪರಿಶೀಲಿಸಿ."
    ),
}


# ════════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Sample merchant transaction history
    sample_data = pd.DataFrame({
        'amount': [500, 1000, 2000, 1500, 800, 1200, 900],
        'hour': [10, 11, 14, 15, 10, 12, 11],
        'sender': ['shop1@okhdfcbank', 'shop2@okaxis', 'shop3@ybl', 
                   'shop1@okhdfcbank', 'shop4@okicici', 'shop2@okaxis', 'shop5@paytm'],
        'date': pd.date_range('2026-04-15', periods=7),
        'is_biz_hours': [1, 1, 1, 1, 1, 1, 1],
    })
    
    # Create context
    context = MerchantContext(sample_data)
    
    # Create generator (English)
    generator_en = AlertMessageGenerator(language="en")
    
    # Example 1: Velocity attack (CRITICAL)
    message = generator_en.generate(
        merchant_name="Ramesh",
        amount=10000,
        hour=22,
        risk_score=92,
        fraud_pattern=FraudPattern.VELOCITY_ATTACK,
        merchant_context=context,
        sender_name="unknown_bot@okaxis",
        count=5,
        time_window_min=15
    )
    
    print("EXAMPLE 1: Velocity Attack (CRITICAL)")
    print("─" * 60)
    print(f"Risk: 92/100 | Pattern: Velocity Attack | Language: English")
    print("\nGenerated Message:")
    print(message)
    print("\n" + "="*60 + "\n")
    
    # Example 2: Amount anomaly (HIGH) - Kannada
    generator_kn = AlertMessageGenerator(language="kn")
    message_kn = generator_kn.generate(
        merchant_name="ರಮೇಶ್",
        amount=25000,
        hour=14,
        risk_score=78,
        fraud_pattern=FraudPattern.AMOUNT_ANOMALY,
        merchant_context=context,
        sender_name="unknown@unknown",
        count=1,
        time_window_min=0
    )
    
    print("EXAMPLE 2: Amount Anomaly (HIGH)")
    print("─" * 60)
    print(f"Risk: 78/100 | Pattern: Amount Anomaly | Language: Kannada")
    print("\nGenerated Message:")
    print(message_kn)
