"""
PaySentinel Alert Scripts: Tone-Based Voice Alerts for Low-Literacy Merchants

This file contains 10 carefully crafted alert scripts covering all risk levels.
Each prioritizes emotional connection, clarity, and trust over technical jargon.

TARGET USERS: Kannada-speaking merchants, age 30-60, low digital literacy, 
high anxiety about fraud (they lose money instantly if scammed)

TONE PHILOSOPHY:
- Sound like a helpful shop assistant, not a robot
- Use "we" to build partnership ("We just noticed...")
- Mention the merchant's own patterns (trust signal)
- Urgency matches risk level
- Clear action: what to do RIGHT NOW
"""

# ════════════════════════════════════════════════════════════════════════════════
# RISK LEVEL 1: LOW RISK (2 examples)
# ════════════════════════════════════════════════════════════════════════════════
# Tone: Friendly & curious, like mentioning something interesting
# Speed: Normal, conversational
# Vibe: "Hey, just wanted to let you know about something"

LOW_RISK_EXAMPLE_1 = """
ENGLISH:
"Hi {merchant_name}. We noticed a payment of ₹{amount} from someone new 
today at {hour} o'clock. It looks normal, but we're just checking. If you 
recognize this person, you're all good. Thanks for using PaySentinel."

KANNADA:
"ನಮಸ್ಕಾರ {merchant_name}. ಇಂದು {hour} ಗಂಟೆಗೆ ಒಬ್ಬ ನವ ಮಂದಿಯಿಂದ ₹{amount} 
ಪಾವತಿ ಬಂದಿದೆ. ಸಾಮಾನ್ಯವೆನಿಸುತ್ತದೆ, ಆದರೆ ನಾವು ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇವೆ. ನೀವು 
ಈ ವ್ಯಕ್ತಿಯನ್ನು ತಿಳಿದುಕೊಂಡಿದ್ದರೆ ನೀವು ಠಿಕ್ಕಾಣೆ. PaySentinel ಬಳಸಿದ್ದಕ್ಕಾಗಿ 
ಧನ್ಯವಾದಗಳು."

TONE USED: Casual, friendly, no alarm
Why it works: Normalizes the system as "just helping you keep track"
Risk of missing: Low—merchant familiar with sender makes own judgment
"""

LOW_RISK_EXAMPLE_2 = """
ENGLISH:
"Hi {merchant_name}! Quick note: We saw a payment of ₹{amount} from 
{sender_name} at {hour} o'clock. Looks totally fine to us, but if anything 
feels off, just let us know. You're in control here."

KANNADA:
"ಹೆಲೋ {merchant_name}! ತ್ವರಿತ ಗಮನಾರ್ಹ: ನಾವು {sender_name} ಬಿಡುವಿನಿಂದ 
{hour} ಗಂಟೆಗೆ ₹{amount} ಪಾವತಿ ಕಂಡೆವು. ನಮ್ಮ ಮತ್ತೆ ಒಟ್ಟೀ ಸರಿಯೆನಿಸುತ್ತದೆ, 
ಆದರೆ ಯಾವುದೇ ಜಿಜ್ಞಾಸೆ ಬಂದರೆ ನಮಗೆ ತಿಳಿಸಿ. ನೀವು ನಿಯಂತ್ರಣದಲ್ಲಿದ್ದೀರಿ."

TONE USED: Relaxed, empowering ("You're in control")
Why it works: Gives merchant confidence in their own judgment
Secondary signal: Trust the system, but trust yourself more
"""

# ════════════════════════════════════════════════════════════════════════════════
# RISK LEVEL 2: MEDIUM RISK (3 examples)
# ════════════════════════════════════════════════════════════════════════════════
# Tone: Concerned neighbor who cares, not alarmist
# Speed: Slightly slower, more deliberate
# Vibe: "Hey, I noticed something that doesn't match your pattern"

MEDIUM_RISK_EXAMPLE_1 = """
ENGLISH:
"Hi {merchant_name}, I need your attention for a moment. We got a payment 
of ₹{amount} from someone unusual at {hour}. This is bigger than what you 
usually get from new people. Can you verify this is someone you know? 
If not, don't accept it."

KANNADA:
"ಸ್ವಲ್ಪ ಕ್ಷಣ ನಿಮ್ಮ ಗಮನ ಬೇಕು {merchant_name}. ನಾವು {hour} ಗಂಟೆಗೆ ಯಾರೋ 
ಅಸಾಧಾರಣ ವ್ಯಕ್ತಿಯಿಂದ ₹{amount} ಪಾವತಿ ಪಡೆದೆವು. ಇದು ಹೊಸ ಜನರಿಂದ ನೀವು 
ಸಾಮಾನ್ಯವಾಗಿ ಪಡೆಯುವುದಕ್ಕಿಂತ ದೊಡ್ಡದಾಗಿದೆ. ಇದು ನಿಮಗೆ ತಿಳಿದ ಯಾರೋ 
ಆ? ಅಲ್ಲದಿದ್ದರೆ, ಸ್ವೀಕರಿಸಬೇಡಿ."

TONE USED: Respectful attention-getter with specific reason
Personalizations: Uses their actual amount, time, and history
Action: Clear negative instruction ("don't accept")
"""

MEDIUM_RISK_EXAMPLE_2 = """
ENGLISH:
"Hi {merchant_name}, something caught our eye. We're seeing three payments 
from {sender_name} in just {time_window} minutes. That's fast. Are they 
supposed to send money three times in a row like this? Let me know."

KANNADA:
"ಸ್ವಾಗತ {merchant_name}, ನಮ್ಮ ಕಣ್ಣಿಗೆ ಏನೋ ಬಿದ್ದಿದೆ. ನಾವು {sender_name} 
ಬಿಡುವಿನಿಂದ ಕೇವಲ {time_window} ನಿಮಿಷಗಳಲ್ಲಿ ಮೂರು ಪಾವತಿ ನೋಡುತ್ತಿದ್ದೇವೆ. 
ಅದು ವೇಗವಾಗಿದೆ. ಅವರು ಈ ರೀತಿ ಮೂರು ಬಾರಿ ಪಾವತಿ ಮಾಡಬೇಕೇ? ನನಗೆ ತಿಳಿಸಿ."

TONE USED: Collaborative problem-solving ("something caught our eye")
Pattern detection: Highlights velocity/structuring
Invitation: "Let me know" — gives merchant veto power
"""

MEDIUM_RISK_EXAMPLE_3 = """
ENGLISH:
"Hi {merchant_name}, just checking in. We got a payment at {hour} o'clock, 
which is unusual for you—you usually trade during shop hours. Everything 
okay? If this was planned, no worries. Just making sure."

KANNADA:
"ಸಮೀಕ್ಷೆ ಹೆಡೆದಿದೆ {merchant_name}. ನಾವು {hour} ಗಂಟೆಗೆ ಪಾವತಿ ಪಡೆದೆವು, 
ನಿಮಗೆ ಸಾಮಾನ್ಯವಿಲ್ಲ—ನೀವು ಸಾಮಾನ್ಯವಾಗಿ ಶಿಲ್ಪ ಗಂಟೆಗಳಲ್ಲಿ ವ್ಯಾಪಾರ ಮಾಡುತ್ತೀರಿ. 
ಎಲ್ಲಾ ಸರಿ? ಇದು ಯೋಜನೆ ಮಾಡಿದ್ದರೆ, ಚಿಂತೆ ಬೇಡಿ. ಕೇವಲ ಖಚಿತ ಮಾಡುತ್ತಿದೆ."

TONE USED: Caring, pattern-aware
Personalization: References their known habits
Assumption of innocence: "If this was planned, no worries"
"""

# ════════════════════════════════════════════════════════════════════════════════
# RISK LEVEL 3: HIGH RISK (3 examples)
# ════════════════════════════════════════════════════════════════════════════════
# Tone: Urgent but calm, like a fire alarm (not panic, but ACTION NOW)
# Speed: Noticeably faster, clipped words
# Vibe: "This looks bad. Here's what to do."

HIGH_RISK_EXAMPLE_1 = """
ENGLISH:
"ALERT! {merchant_name}, this is urgent. Someone just sent ₹{amount} 
around {hour} o'clock. This is way bigger than your biggest transactions. 
This looks like fraud. Do NOT accept this. Block this sender right now. 
Do you hear me? Block them now."

KANNADA:
"ಎಚ್ಚರಣೆ! {merchant_name}, ಇದು ತುರ್ತು. ಯಾರೋ ಕೇವಲ {hour} ಗಂಟೆಗೆ 
₹{amount} ಕಳುಹಿಸಿದ್ದಾರೆ. ಇದು ನಿಮ್ಮ ದೊಡ್ಡ ವಹನೆಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ. ಇದು 
ವಂಚನೆ ಹೋಲುತ್ತದೆ. ಇದನ್ನು ಸ್ವೀಕರಿಸಬೇಡಿ. ಈ ಪೋಷಕರನ್ನು ಈಗಲೇ ನಿರ್ಬಂಧಿಸಿ. 
ನೀವು ಕೇಳುತ್ತಿರುವಿರೋ? ಈಗಲೇ ನಿರ್ಬಂಧಿಸಿ."

TONE USED: Urgent, repetitive for emphasis ("Do you hear me? Block them now.")
Magnitude signal: "Way bigger than your biggest transactions"
Command language: Clear imperatives (ALERT, Do NOT, Block right now)
Repetition: Repeats the key action twice
"""

HIGH_RISK_EXAMPLE_2 = """
ENGLISH:
"URGENT! {merchant_name}, stop. We're seeing a pattern. {count} payments 
in {time_window} from the same person. That's structuring—a scam technique. 
This is not real. STOP accepting from this sender. Now."

KANNADA:
"ತುರ್ತುವಾಗಿ! {merchant_name}, ನಿಲ್ಲಿಸಿ. ನಾವು ಒಂದು ಮಾದರಿ ನೋಡುತ್ತಿದ್ದೇವೆ. 
ಅದೇ ವ್ಯಕ್ತಿಯಿಂದ {time_window} ನಲ್ಲಿ {count} ಪಾವತಿ. ಅದು ರಚನೆ—ವಂಚನೆ 
ತಂತ್ರ. ಇದು ನಿಜವಲ್ಲ. ಈ ಪೋಷಕರನಿಂದ ಸ್ವೀಕರಿಸುವುದನ್ನು ಹೆಚ್ಚು ಮಾಡಬೇಡಿ. ಈಗ."

TONE USED: Technical term + plain language ("That's structuring—a scam technique")
Pattern education: Names the technique so merchant learns
Finality: "This is not real" — definitive conclusion
"""

HIGH_RISK_EXAMPLE_3 = """
ENGLISH:
"WARNING: {merchant_name}, we need immediate action. An unknown sender just 
tried to send ₹{amount} at {hour} o'clock—it's 10 times your normal daily amount. 
This is extremely suspicious. REJECT this transaction immediately. If you 
already accepted it, CALL YOUR BANK NOW."

KANNADA:
"ಎಚ್ಚರಣೆ: {merchant_name}, ನಮಗೆ ತಕ್ಷಣ ಕ್ರಿಯೆ ಬೇಕು. ಅಜ್ಞಾತ ಪೋಷಕರು ಕೇವಲ 
{hour} ಗಂಟೆಗೆ ₹{amount} ಕಳುಹಿಸಲು ಪ್ರಯತ್ನಿಸಿದ್ದಾರೆ—ಇದು ನಿಮ್ಮ ಸಾಮಾನ್ಯ 
ದೈನಂದಿನ ಮೊತ್ತದ 10 ಪಟ್ಟು. ಇದು ಬಹಳ ಅನುಮಾನಾಸ್ಪದ. ಈ ವಹನೆಯನ್ನು ತಕ್ಷಣ 
ತಿರಸ್ಕರಿಸಿ. ನೀವು ಈಗಾಗಲೇ ಅನುಮೋದಿಸಿದ್ದರೆ, ನಿಮ್ಮ ಬ್ಯಾಂಕಿಗೆ ಈಗ ಕರೆ ಮಾಡಿ."

TONE USED: Magnitude + comparison (10x normal)
Two pathways: Prevent if not accepted yet; damage control if already accepted
Authority signal: Bank involvement for credibility
"""

# ════════════════════════════════════════════════════════════════════════════════
# RISK LEVEL 4: CRITICAL RISK (2 examples)
# ════════════════════════════════════════════════════════════════════════════════
# Tone: Emergency dispatcher (calm but life-or-death)
# Speed: Very fast, staccato
# Vibe: "This is happening RIGHT NOW. You MUST act."

CRITICAL_RISK_EXAMPLE_1 = """
ENGLISH:
"CRITICAL ALERT! {merchant_name}, THIS IS AN EMERGENCY. Someone is 
attacking your account RIGHT NOW. ₹{amount} attempted at {hour}. This is 
a coordinated scam. DO NOT ACCEPT. DO NOT TRANSFER MONEY. IF YOU ALREADY 
ACCEPTED, BLOCK YOUR ACCOUNT IMMEDIATELY. CALL YOUR BANK NOW. ₹{amount} 
IS AT RISK."

KANNADA:
"ನಿರ್ಣಾಯಕ ಎಚ್ಚರಣೆ! {merchant_name}, ಇದು ಜರುರಿ ಸಂದರ್ಭ. ಯಾರೋ ನಿಮ್ಮ ಖಾತೆಗೆ 
ಸದ್ಯ ದಾಳಿ ಮಾಡುತ್ತಿದ್ದಾರೆ. {hour} ಗಂಟೆಗೆ ₹{amount} ಪ್ರಯತ್ನ. ಇದು 
ಸಂಘೀಕೃತ ವಂಚನೆ. ಸ್ವೀಕರಿಸಬೇಡಿ. ಹಣ ವಹಿಸಬೇಡಿ. ಈಗಾಗಲೇ ಸ್ವೀಕರಿಸಿದ್ದರೆ, 
ನಿಮ್ಮ ಖಾತೆಯನ್ನು ತಕ್ಷಣ ಮುಚ್ಚಿ. ನಿಮ್ಮ ಬ್ಯಾಂಕಿಗೆ ಈಗ ಕರೆ ಮಾಡಿ. ₹{amount} 
ಅಪಾಯದಲ್ಲಿದೆ."

TONE USED: Military emergency protocol
All-caps for key words
Repetition of amount (creates urgency + memory)
Multiple scenarios covered (not accepted, already accepted)
External escalation: Bank number reference
"""

CRITICAL_RISK_EXAMPLE_2 = """
ENGLISH:
"URGENT EMERGENCY! {merchant_name}, your account is under active attack. 
{count} fraudulent transactions in {time_window}. They are trying to drain 
your account. Every second counts. BLOCK THIS SENDER NOW. REPORT TO YOUR 
BANK IMMEDIATELY. Save this message for proof. Amount at risk: ₹{amount}. 
ACT NOW."

KANNADA:
"ತುರ್ತುವಾಗಿ ಜರುರಿ! {merchant_name}, ನಿಮ್ಮ ಖಾತೆ ಸಕ್ರಿಯ ದಾಳಿಯ ಅಡಿಯಲ್ಲಿದೆ. 
{time_window} ನಲ್ಲಿ {count} ವಂಚನೆಗ್ರಾಹಿ ವಹನೆ. ಅವರು ನಿಮ್ಮ ಖಾತೆಯನ್ನು 
ಖಾಲಿ ಮಾಡಲು ಪ್ರಯತ್ನಿಸುತ್ತಿದ್ದಾರೆ. ಪ್ರತಿ ಸೆಕೆಂಡ ಪ್ರಮುಖ. ಈ ಪೋಷಕರನ್ನು 
ತಕ್ಷಣ ನಿರ್ಬಂಧಿಸಿ. ನಿಮ್ಮ ಬ್ಯಾಂಕಿಗೆ ತಕ್ಷಣ ವರದಿ ಮಾಡಿ. ಈ ಸಂದೇಶವನ್ನು 
ಪುರಾವೆಗಾಗಿ ಉಳಿಸಿ. ಅಪಾಯದಲ್ಲಿರುವ ಮೊತ್ತ: ₹{amount}. ಈಗಲೇ ಕ್ರಿಯೆ ಮಾಡಿ."

TONE USED: Active threat description
Time pressure explicitly stated: "Every second counts"
Evidence/proof mechanism: "Save this message"
Coordinated action: Multiple steps (block, report, save)
Finality: "ACT NOW" — no equivocation
"""

# ════════════════════════════════════════════════════════════════════════════════
# TONE ANALYSIS SUMMARY
# ════════════════════════════════════════════════════════════════════════════════

TONE_ANALYSIS = """
RISK LEVEL    | TONE              | SPEED        | REPEAT | IMPERATIVES | CALL-TO-ACTION
──────────────┼───────────────────┼──────────────┼────────┼─────────────┼─────────────────
LOW           | Friendly, curious | Normal       | None   | None        | Optional ("let us know")
MEDIUM        | Concerned, caring | Slightly ↑   | 1x     | Polite      | Check/Verify
HIGH          | Urgent, firm      | Fast         | 2x     | Strong      | DO NOT/Block/Now
CRITICAL      | Emergency, terse  | Very fast    | 3x+    | Military    | ACT NOW/CALL BANK

KEY PATTERNS IN MERCHANT LANGUAGE:
1. LOW:      "We just noticed..." (collaborative)
2. MEDIUM:   "Something caught our eye..." (attentive)
3. HIGH:     "This looks bad..." (diagnosis)
4. CRITICAL: "This is an emergency..." (life-or-death)

PERSONALIZATION ELEMENTS USED:
- {merchant_name}: Personal address (trust, attention)
- {amount}: Specific rupee amount (credibility)
- {hour}: Exact time (credibility)
- {sender_name}: Specific person (pattern recognition)
- {count} + {time_window}: Structuring signal
- Comparison to their history: "bigger than your biggest transactions"
"""

print("""
════════════════════════════════════════════════════════════════════════════════
                    PaySentinel: 10 Alert Script Samples
════════════════════════════════════════════════════════════════════════════════
""")

print(LOW_RISK_EXAMPLE_1)
print("\n" + "─"*80 + "\n")
print(LOW_RISK_EXAMPLE_2)
print("\n" + "─"*80 + "\n")
print(MEDIUM_RISK_EXAMPLE_1)
print("\n" + "─"*80 + "\n")
print(MEDIUM_RISK_EXAMPLE_2)
print("\n" + "─"*80 + "\n")
print(MEDIUM_RISK_EXAMPLE_3)
print("\n" + "─"*80 + "\n")
print(HIGH_RISK_EXAMPLE_1)
print("\n" + "─"*80 + "\n")
print(HIGH_RISK_EXAMPLE_2)
print("\n" + "─"*80 + "\n")
print(HIGH_RISK_EXAMPLE_3)
print("\n" + "─"*80 + "\n")
print(CRITICAL_RISK_EXAMPLE_1)
print("\n" + "─"*80 + "\n")
print(CRITICAL_RISK_EXAMPLE_2)
print("\n" + "─"*80 + "\n")
print(TONE_ANALYSIS)
