"""
PaySentinel UX: Alert Trigger Flow & Accessibility Design

How to present fraud alerts to low-literacy merchants in a way that:
1. Ensures they see/hear it immediately
2. Builds urgency proportional to risk
3. Respects their language preference
4. Doesn't overwhelm them with multiple alerts
5. Serves deaf/hard-of-hearing merchants
"""

# ════════════════════════════════════════════════════════════════════════════════
# ALERT TRIGGER FLOW: When Should Audio Play?
# ════════════════════════════════════════════════════════════════════════════════

ALERT_TRIGGER_FLOW = """
════════════════════════════════════════════════════════════════════════════════
                     WHEN SHOULD THE ALERT PLAY?
════════════════════════════════════════════════════════════════════════════════

RISK LEVEL    | TRIGGER          | LATENCY    | REPEAT  | WHY
──────────────┼──────────────────┼────────────┼─────────┼─────────────────────
LOW           | Silent badge     | N/A        | None    | Don't alarm merchant
              | (Show on UI only)| N/A        | N/A     | Curiosity only

MEDIUM        | Subtle sound     | 2 sec      | 2x      | Needs attention
              | (chime)          | after       | (30s)   | but not panic
              |                  | detection   |         | 

HIGH          | Alert tone       | Immediate  | 3x      | Urgent action
              | (alarm bell)     | (<100ms)   | (60s)   | needed

CRITICAL      | Urgent sound     | Immediate  | Loop    | Stop everything
              | + TTS voice      | (<50ms)    | every   | NOW
              |                  |            | 5s      |


DETAILED FLOW BY RISK LEVEL:
──────────────────────────────

🟢 LOW RISK (0-30)
   Merchant is doing their normal work
   └─ Dashboard shows: 📌 Small badge on transaction
   └─ No sound (would be annoying)
   └─ Text: "New customer payment - everything looks fine"
   └─ Action: Optional click to learn more
   

🟡 MEDIUM RISK (30-60)
   Something doesn't match their pattern, but could be legitimate
   ├─ Display: Subtle chime (1s)
   ├─ Wait 2 seconds
   ├─ Play TTS: "Attention needed - please check transaction"
   ├─ Wait 30 seconds
   ├─ Repeat chime + TTS once more (if merchant hasn't acknowledged)
   └─ Dashboard shows: ⚠️ Yellow alert card
   

🔴 HIGH RISK (60-85)
   Looks like fraud, merchant must verify or reject immediately
   ├─ IMMEDIATE (no delay): Alert horn sound (800ms)
   ├─ PLAY TTS: Urgent alert message (tone: concerned)
   ├─ Wait 30 seconds
   ├─ Play AGAIN: TTS + horn (repetition builds urgency)
   ├─ Wait 30 seconds
   ├─ Play THIRD TIME: TTS only (voice fatigue prevention)
   └─ Dashboard shows: 🔴 Red alert card, transaction locked
   

🔴🔴 CRITICAL RISK (85-100)
   Account under active attack - MUST STOP NOW
   ├─ IMMEDIATE: Loud alarm (continuous beeping, 2s)
   ├─ PLAY TTS: Emergency message (tone: angry/commanding)
   ├─ Loop every 5 seconds until merchant acknowledges:
   │  ├─ Alarm + TTS (5s off, 10s on pattern)
   │  └─ Keeps escalating attention
   ├─ Dashboard shows: 🔴🔴 CRITICAL banner (red, large)
   ├─ Force-show alert (modal that can't be dismissed without action)
   └─ Suggest immediate bank call (show dial button)


════════════════════════════════════════════════════════════════════════════════
"""

print(ALERT_TRIGGER_FLOW)


# ════════════════════════════════════════════════════════════════════════════════
# HANDLING MULTIPLE ALERTS
# ════════════════════════════════════════════════════════════════════════════════

MULTIPLE_ALERTS = """
════════════════════════════════════════════════════════════════════════════════
                   HANDLING MULTIPLE ALERTS (Alert Queuing)
════════════════════════════════════════════════════════════════════════════════

SCENARIO 1: Two alerts arrive at the same time
───────────────────────────────────────────────

Old Approach (BAD):
  Alert 1: "Beep beep beep"
  Alert 2: "Beep beep beep"
  Merchant: "What's happening?? Two alerts??" (confused)

Better Approach (GOOD):
  ├─ Compare risk scores: Alert 1 (₹15,000) = 85/100, Alert 2 (₹500) = 40/100
  ├─ Queue only CRITICAL alerts (>75)
  ├─ Play Alert 1 (CRITICAL) first
  ├─ Queue Alert 2 (MEDIUM) for display after Alert 1 acknowledged
  ├─ Dashboard shows: Alert 1 in focus + "1 more alert waiting" badge
  └─ Merchant action: Deal with worst first, then see second


SCENARIO 2: Alert firing during previous alert playback
─────────────────────────────────────────────────────────

Example:
  Time 0:00 → Alert 1 plays (₹20,000, CRITICAL)
  Time 0:05 → New Alert 2 arrives (₹10,000, HIGH)
  Time 0:10 → Alert 1 still playing...

Smart Approach:
  ├─ Check risk score of Alert 2
  ├─ If Alert 2 risk > Alert 1 risk → INTERRUPT and play Alert 2 first
  ├─ If Alert 2 risk < Alert 1 risk → Queue for after Alert 1 finishes
  └─ Show counter: "3 alerts in queue - showing worst first"


SCENARIO 3: Rapid-fire structuring attack (5+ alerts in 1 minute)
──────────────────────────────────────────────────────────────────

Example: Bot sending ₹5k from same sender 6 times

Smart Approach:
  ├─ Recognize as coordinated attack (same sender, time_window < 60s)
  ├─ Merge into single CRITICAL alert: "ATTACK! 6 payments from same person"
  ├─ Don't play 6 separate alerts
  ├─ But DO show transaction list for their records
  └─ Priority: 1 urgent voice warning > 6 confusing alerts


ALERT PRIORITY ALGORITHM:
─────────────────────────

Priority = (risk_score * 2) - (time_since_arrival_sec * 0.1)

Example:
  Alert A: 90/100, arrived 5 seconds ago → Priority = 180 - 0.5 = 179.5
  Alert B: 70/100, arrived 2 seconds ago → Priority = 140 - 0.2 = 139.8
  Alert C: 50/100, arrived 1 second ago  → Priority = 100 - 0.1 = 99.9
  
  Play order: A → B → C (highest priority first)


IMPLEMENTATION:
───────────────

class AlertQueue:
    def __init__(self, max_queue_size=10):
        self.queue = []
        self.max_size = max_queue_size
        self.is_playing = False
    
    def add_alert(self, alert: Dict):
        '''Add alert and reorder by priority'''
        # Check for duplicate/same-sender attacks
        if self._is_coordinated_attack(alert):
            self._merge_with_existing(alert)
            return
        
        # Add to queue
        if len(self.queue) < self.max_size:
            self.queue.append(alert)
            self.queue.sort(key=lambda a: a['priority'], reverse=True)
        else:
            # Queue full - discard lowest priority
            self.queue.pop()
            self.add_alert(alert)
    
    def _is_coordinated_attack(self, alert: Dict) -> bool:
        '''Check if same sender in last 60s'''
        sender = alert['sender']
        for existing in self.queue:
            if (existing['sender'] == sender and
                abs(existing['timestamp'] - alert['timestamp']) < 60):
                return True
        return False
    
    def _merge_with_existing(self, alert: Dict):
        '''Merge into existing alert (update count, increase priority)'''
        for existing in self.queue:
            if existing['sender'] == alert['sender']:
                existing['count'] += 1
                existing['priority'] = max(85, existing['priority'] + 5)
                break


════════════════════════════════════════════════════════════════════════════════
"""

print(MULTIPLE_ALERTS)


# ════════════════════════════════════════════════════════════════════════════════
# LANGUAGE & ACCESSIBILITY SETTINGS
# ════════════════════════════════════════════════════════════════════════════════

LANGUAGE_SETTINGS = """
════════════════════════════════════════════════════════════════════════════════
           LANGUAGE & ACCESSIBILITY SETTINGS (Low-Literacy Merchants)
════════════════════════════════════════════════════════════════════════════════

USER FLOW: First-Time Setup
───────────────────────────

When merchant opens app for first time:
  
  ┌─────────────────────────────────────────┐
  │  Welcome! Let's set up your preferences │
  └─────────────────────────────────────────┘
  
  1️⃣  LANGUAGE SELECTION (with audio examples)
      ┌─ What language would you like alerts in? ─┐
      │  🔊 ಕನ್ನಡ (Kannada)                      │
      │  🔊 English                                │
      │  🔊 हिंदी (Hindi)                         │
      │  🔊 தமிழ் (Tamil)                        │
      └────────────────────────────────────────┘
      → Each option has PLAY SAMPLE button
      → Merchant listens to alert example
      → Can compare voices
      → Selects favorite
  
  
  2️⃣  ACCESSIBILITY OPTIONS
      ┌─ Do you have hearing difficulty? ─┐
      │  ○ No, I hear fine                 │
      │  ○ Some difficulty (use flashlight)│
      │  ○ Deaf/hard of hearing (text only)│
      └──────────────────────────────────┘
      
      If selected "Some difficulty" or "Deaf":
        └─ ✓ Enable flash alert
        └─ ✓ Enable vibration alert
        └─ ✓ Enable SMS alerts (+91-XXXXXXXXXX)
  
  
  3️⃣  ALERT FREQUENCY PREFERENCE
      ┌─ How often should we alert you? ─┐
      │  🔊 Every alert (default)        │
      │  🔇 Only HIGH/CRITICAL alerts    │
      │  🤫 Only CRITICAL alerts         │
      └────────────────────────────────┘
  
  
  4️⃣  MULTIPLE DEVICE PREFERENCE
      ┌─ Alert device selection ─┐
      │  ☑️ This phone (primary) │
      │  ☐ Smartwatch            │
      │  ☐ Send SMS to backup    │
      └──────────────────────────┘


SAVED PREFERENCES (User Settings Screen)
──────────────────────────────────────────

Settings visible in App:
  
  ALERTS & SOUND
  ├─ Language: ಕನ್ನಡ (Kannada) [CHANGE]
  ├─ Alert Voice: Female (Shruthi) [CHANGE]
  ├─ Play Sound: ON [toggle]
  ├─ Alert Frequency: All alerts [CHANGE]
  └─ [🔊 Play Sample Alert]
  
  ACCESSIBILITY
  ├─ Hearing Difficulty: Some difficulty [CHANGE]
  ├─ Flash Alert: ON [toggle]
  ├─ Vibration: ON [toggle]
  └─ SMS Backup: +91-98765-43210 [CHANGE]
  
  ADVANCED
  ├─ Do Not Disturb (business hours): [TIME RANGE]
  ├─ Multiple Alerts: Queue by priority [toggle]
  └─ Test Alert: [Send me a sample alert]


════════════════════════════════════════════════════════════════════════════════
"""

print(LANGUAGE_SETTINGS)


# ════════════════════════════════════════════════════════════════════════════════
# ACCESSIBILITY FOR DEAF/HARD-OF-HEARING
# ════════════════════════════════════════════════════════════════════════════════

ACCESSIBILITY = """
════════════════════════════════════════════════════════════════════════════════
              ACCESSIBILITY FOR DEAF & HARD-OF-HEARING MERCHANTS
════════════════════════════════════════════════════════════════════════════════

PROBLEM:
  ~5-10% of Indian merchants have hearing difficulty
  Current: Alerts are audio-only (completely misses them)
  Impact: They'd have NO warning of fraud until money is gone

SOLUTION: Multi-Sensory Alerts
────────────────────────────────


🟢 LOW RISK: No audio needed
  │
  └─ Dashboard badge: 📌 (stays there for review)


🟡 MEDIUM RISK: Audio + Backup channels
  │
  ├─ Audio: Subtle chime (if hearing aid compatible)
  ├─ Visual: 🟡 Yellow banner with text
  ├─ Vibration: Single vibration (0.5s)
  └─ Optional: SMS to merchant's backup phone


🔴 HIGH RISK: Aggressive multi-sensory
  │
  ├─ Audio: Loud alarm (accessibility mode: slower beeps)
  ├─ Visual: 🔴 Flashing red banner + large text
  │          "FRAUD ALERT: ₹15,000 from UNKNOWN SENDER"
  ├─ Vibration: Pattern (short-long-short) × 3
  ├─ Screen: Screen stays ON (max brightness)
  ├─ SMS: "ALERT: ₹15,000 from unknown. TAP APP NOW"
  └─ Chat: WhatsApp notification to merchant (if linked)


🔴🔴 CRITICAL: Maximum urgency + external alerts
  │
  ├─ Audio: CONTINUOUS alarm + TTS (repeating)
  ├─ Visual: Flashing red (entire screen), NO other app visible
  ├─ Vibration: Intense pattern (long-long-long) × infinite
  ├─ Screen: FORCED awake, max brightness, full volume
  ├─ SMS: "CRITICAL: Account attack! Amount ₹15,000. CALL BANK!"
  ├─ SMS: "Fraud alert - Bank number included"
  ├─ WhatsApp: Urgent message + location pin (if linked)
  └─ Email: Immediate notification (if linked)


SPECIFIC ACCESSIBILITY FEATURES:
─────────────────────────────────

1️⃣  SCREEN FLASH
    Instead of: Sound alert
    Use: Bright white-red flash (proven to get attention)
    
    Implementation:
    @keyframes alert_flash {
      0% { background: white; }
      50% { background: #ff0000; }  /* Red */
      100% { background: white; }
    }
    animation: alert_flash 0.5s infinite;
    
    For CRITICAL: Flash every 2 seconds until acknowledged


2️⃣  HAPTIC VIBRATION PATTERNS
    
    MEDIUM: Single pulse
    ├─ Vibrate: 500ms
    
    HIGH: Alert pattern
    ├─ Vibrate: 200ms
    ├─ Pause:    100ms
    ├─ Vibrate: 200ms
    ├─ Pause:    100ms
    ├─ Vibrate: 200ms
    └─ (Repeat 3×)
    
    CRITICAL: Emergency pattern
    ├─ Vibrate: 500ms
    ├─ Pause:   200ms
    ├─ Vibrate: 500ms
    └─ (Continuous)
    
    Implementation:
    import haptic from 'react-native-haptic-feedback';
    
    if (risk_level == "high"):
        haptic.trigger("notification")
    elif risk_level == "critical":
        haptic.trigger("impactHeavy")
        # Repeat every 5 seconds


3️⃣  SMS BACKUP ALERTING
    
    Setup Flow:
    1. Merchant enables: "I'd like SMS alerts"
    2. Enter backup phone number: +91-98765-43210
    3. Verify OTP: "OTP: 1234 received"
    
    SMS Template by Risk Level:
    
    HIGH:
    ┌─ FRAUD ALERT PaySentinel
    │ ₹15,000 from unknown sender
    │ TAP YOUR APP IMMEDIATELY
    │ https://paysentinel.app/alert/abc123
    └─
    
    CRITICAL:
    ┌─ 🚨 CRITICAL FRAUD ATTACK 🚨
    │ Your UPI is under attack!
    │ ₹100,000 attempted
    │ CALL YOUR BANK NOW
    │ ICICI: 1800-1801-0101
    │ AXIS: 1860-5005-005
    │ HDFC: 1800-270-3800
    └─


4️⃣  WHATSAPP INTEGRATION (High engagement for merchants)
    
    Setup: Link WhatsApp number to PaySentinel
    
    HIGH RISK:
    ┌─ 🔴 FRAUD ALERT
    │ Amount: ₹15,000
    │ From: Unknown
    │ Time: 14:32
    │ [VERIFY TRANSACTION] [BLOCK SENDER]
    └─ (Clickable buttons in WhatsApp)
    
    Merchant can reply:
    ├─ "BLOCK" → Transaction blocked immediately
    ├─ "OK" → Acknowledged, can review
    └─ "FRAUD" → Escalated to bank


5️⃣  VISUAL INDICATORS (For partially deaf)
    
    Dashboard Alert Card:
    ┌─ 🔴🔴 CRITICAL FRAUD ALERT 🔴🔴
    │ ₹100,000 ← VERY LARGE FONT
    │ From Unknown Sender ← BOLD RED TEXT
    │ Status: BLOCKED ← GREEN CHECK
    │ 
    │ [CALL YOUR BANK] [BLOCK SENDER]
    └─
    
    Font sizes:
    ├─ Amount: 48px (huge, visible from distance)
    ├─ Risk level: 32px
    ├─ Reason: 20px
    ├─ Time: 16px
    
    Colors:
    ├─ Critical: Pure red (#FF0000)
    ├─ High: Orange (#FF6600)
    ├─ Medium: Yellow (#FFCC00)
    ├─ Low: Green (#00CC00)


TESTING WITH DEAF MERCHANTS:
────────────────────────────

When user selects "Deaf/hard of hearing" in settings:
  1. Disable audio output (save resources)
  2. Test SMS delivery (send test SMS)
  3. Verify vibration patterns (haptic test)
  4. Flash alerts visible? (brightness test)
  5. Provide emergency contacts (quick call buttons)


════════════════════════════════════════════════════════════════════════════════
"""

print(ACCESSIBILITY)


# ════════════════════════════════════════════════════════════════════════════════
# COMPLETE UX FLOW DIAGRAM
# ════════════════════════════════════════════════════════════════════════════════

COMPLETE_FLOW = """
════════════════════════════════════════════════════════════════════════════════
                       COMPLETE ALERT UX FLOW (High Risk)
════════════════════════════════════════════════════════════════════════════════

TRANSACTION ARRIVES:
                ↓
    Risk Score: 72/100 (HIGH)
    Pattern: Amount Anomaly
    Language: Kannada
                ↓
    ┌─────────────────────────────────┐
    │ Alert Queue Check               │
    │ • Priority: 72 - 0 = 72         │
    │ • Is CRITICAL? NO               │
    │ • Queue size: 1                 │
    │ • Merge attack? NO              │
    └─────────────────────────────────┘
                ↓
    ┌─────────────────────────────────┐
    │ Trigger Audio Alert             │
    │ • Sound: Alert horn (800ms)     │
    │ • Volume: Max                   │
    │ • Language: Kannada             │
    │ • Emotion: Concerned            │
    └─────────────────────────────────┘
    
    🔊 HORN SOUND (800ms)
                ↓ (after 500ms)
    🔊 TTS PLAYS: "ಸೂಚನೆ! ಹೊಸ ಯಾರೋ..."
                ↓ (message duration ~10s)
    
    ┌─────────────────────────────────┐
    │ Dashboard Update                │
    │ • Show alert card               │
    │ • Color: 🔴 Red                 │
    │ • Highlight transaction         │
    │ • Lock transaction (no accept)  │
    └─────────────────────────────────┘
    
    🟡 MERCHANT SCREEN:
    ┌──────────────────────────────────────────┐
    │ 🔴🔴 HIGH FRAUD ALERT 🔴🔴             │
    │                                          │
    │ Amount: ₹15,000                          │
    │ From: Unknown Sender                     │
    │ Pattern: Unusually Large Amount          │
    │ Your normal: ~₹2,000                    │
    │ This: 7.5× bigger                        │
    │                                          │
    │ Time: 14:32:15                          │
    │ Status: 🚫 CANNOT ACCEPT                │
    │                                          │
    │ ┌──────────────────────────────────┐   │
    │ │ [BLOCK THIS SENDER]              │   │
    │ │ [VERIFY WITH BUYER]              │   │
    │ │ [HELP]                           │   │
    │ └──────────────────────────────────┘   │
    └──────────────────────────────────────────┘
    
    MERCHANT ACTION:
    
    Path A: Immediate Block (Likely Fraud)
    ├─ Tap [BLOCK THIS SENDER]
    ├─ Confirmation: "Sender blocked ✓"
    ├─ Transaction: Rejected & Logged
    ├─ Dashboard: Remove alert, show success
    └─ Feedback: "You protected ₹15,000!"
    
    Path B: Verify with Buyer (Legitimate)
    ├─ Tap [VERIFY WITH BUYER]
    ├─ Copy buyer contact: Copy phone / WhatsApp
    ├─ Call/Message: Ask if they sent it
    ├─ Return to app:
    │  ├─ If NO → Block immediately
    │  └─ If YES → [ACCEPT THIS PAYMENT]
    └─ Accept → Transaction processed
    
    Path C: No Action / Dismissal
    ├─ Merchant ignores alert
    ├─ Wait 30 seconds...
    ├─ ALERT REPEATS:
    │  ├─ 🔊 Horn again (500ms)
    │  ├─ 🔊 TTS: "ಸೂಚನೆ ಪುನರಾವರ್ತನೆ..." (Repeat)
    │  └─ 🟡 Banner blinks faster
    ├─ Wait 60 seconds...
    ├─ ALERT REPEATS 3RD TIME:
    │  ├─ TTS only (voice fatigue)
    │  └─ Banner still blinking
    ├─ Wait 120 seconds...
    └─ Auto-block transaction (time limit)


MERCHANT SETTINGS FLOW:
──────────────────────

Home Screen
    ↓ (Tap Settings ⚙️)
Settings Menu
    ├─ Alerts & Sound
    │  ├─ Language: ಕನ್ನಡ [CHANGE]
    │  ├─ Voice: Female [CHANGE]
    │  ├─ Play Sound: ON [toggle]
    │  ├─ [🔊 Play Sample]
    │  └─ (Goes to PREVIEW below)
    │
    ├─ Accessibility
    │  ├─ Hearing Difficulty: Some [CHANGE]
    │  ├─ Flash Alert: ON
    │  ├─ Vibration: ON
    │  └─ SMS Backup: +91... [CHANGE]
    │
    ├─ Risk Preferences
    │  ├─ Show all alerts [toggle]
    │  ├─ Only HIGH/CRITICAL [toggle]
    │  └─ Only CRITICAL [toggle]
    │
    └─ Advanced
       ├─ Do Not Disturb: 22:00 - 06:00 [CHANGE]
       ├─ [📧 Test SMS Alert]
       └─ [💬 Test WhatsApp Alert]


PREVIEW MODE (When merchant clicks "Play Sample"):
──────────────────────────────────────────────────

┌─────────────────────────────────────────┐
│  ALERT PREVIEW (Not Real)               │
├─────────────────────────────────────────┤
│                                         │
│  🔊 Listen to your alert voice:         │
│                                         │
│  [🔊 PLAY SAMPLE] (starts audio)       │
│                                         │
│  Message:                               │
│  "ಸೂಚನೆ! ₹15,000 ಹೊಸ ಅವತಾರದಿಂದ       │
│   ಬಂದಿದೆ. ನಿಮ್ಮ ಸಾಮಾನ್ಯ ಮೊತ್ತಕ್ಕಿಂತ   │
│   ದೊಡ್ಡ. ತಕ್ಷಣ ಅನುಮೋದಿಸಬೇಡಿ."         │
│                                         │
│  🔊 Volume: [====●====] 80%            │
│                                         │
│  ⚡ Speed:  [======●===] 1.0x          │
│                                         │
│  [LIKE THIS] [NOT CLEAR] [CHANGE VOICE]│
│                                         │
└─────────────────────────────────────────┘

After [LIKE THIS]:
└─ Saved! ✓
└─ Return to Settings
└─ Kannada + Female + 1.0x speed


════════════════════════════════════════════════════════════════════════════════
"""

print(COMPLETE_FLOW)
