"""
Intent-aware Support Chatbot.
Uses the trained classifier to detect intent, then returns helpful responses.
"""
from .predictor import predict
import random

# Curated responses for common intents (fallback + generic for the rest)
INTENT_RESPONSES = {
    "card_arrival": [
        "I understand you're waiting for your card. Cards usually arrive within 5–7 business days after request. You can track the delivery status in the app under 'Cards' → 'Track delivery'. Would you like me to help you check the estimated arrival date?",
        "Sorry for the wait! Most cards are delivered within a week. If it's been longer than 10 business days, I recommend contacting support to reissue. Shall I guide you on how to request a replacement?",
    ],
    "card_delivery_estimate": [
        "Card delivery typically takes 5–7 business days, depending on your location. You can see the estimated date in the app under Cards → Track delivery.",
    ],
    "activate_my_card": [
        "To activate your card: 1) Open the app 2) Go to Cards 3) Select the new card 4) Tap 'Activate'. You'll need the last 4 digits and the expiry date. Need step-by-step help?",
    ],
    "change_pin": [
        "You can change your PIN in the app: Cards → Select card → Security → Change PIN. You'll need to verify with your current PIN or biometrics.",
    ],
    "card_not_working": [
        "Sorry your card isn't working. Common fixes: 1) Make sure it's activated 2) Check if it's frozen in the app 3) Try a different terminal. If none work, we can freeze it and order a replacement.",
    ],
    "compromised_card": [
        "If you suspect your card is compromised, freeze it immediately in the app (Cards → Freeze). Then report it so we can cancel and issue a new one. Would you like the steps?",
    ],
    "declined_card_payment": [
        "A declined payment can happen for several reasons: insufficient funds, fraud protection, or merchant restrictions. Check your balance and recent notifications. I can help you review common causes.",
    ],
    "card_payment_fee_charged": [
        "Some card payments incur fees (e.g. cash advances or certain foreign transactions). You can view fee details in the transaction history. Want me to explain typical fee types?",
    ],
    "transfer_not_received_by_recipient": [
        "Transfers can take from a few minutes up to 1–3 business days depending on the type (instant vs standard). Please share the approximate time you sent it and I can suggest next steps.",
    ],
    "pending_transfer": [
        "Pending transfers usually clear within a few hours to 1 business day. You can track status under Payments → Transfer history.",
    ],
    "cancel_transfer": [
        "If the transfer is still pending you may be able to cancel it from Payments → Transfer history → Cancel. Once completed, cancellation isn't possible and you'd need a reverse transfer from the recipient.",
    ],
    "balance_not_updated_after_bank_transfer": [
        "Incoming transfers can take 1–3 business days to appear. Weekends and holidays can add delay. Check the expected clearing date in the transfer details.",
    ],
    "cash_withdrawal_charge": [
        "ATM withdrawals can incur fees depending on the network and location (especially abroad). Fee details appear in the transaction. Want tips on avoiding ATM fees?",
    ],
    "wrong_amount_of_cash_received": [
        "Sorry about the wrong cash amount. Please keep the receipt and note the ATM location/time. We can open a dispute — shall I guide you through reporting it?",
    ],
    "exchange_rate": [
        "Exchange rates are updated regularly and shown before you confirm a transfer or card payment in foreign currency. You can also check the current rate in the app under Payments → Exchange.",
    ],
    "age_limit": [
        "Account eligibility and age limits depend on your region and product. Generally you need to be 18+ for a full account. Check the terms in the app or on our website for your country.",
    ],
    "verify_my_identity": [
        "Identity verification usually requires a government ID and a selfie. Go to Profile → Verify identity and follow the steps. It typically takes a few minutes to a few hours.",
    ],
    "why_verify_identity": [
        "We verify identity to keep accounts secure and comply with regulations. It helps protect you from fraud and unlocks higher limits.",
    ],
    "get_physical_card": [
        "You can order a physical card from the app: Cards → Order physical card. Delivery usually takes 5–7 business days.",
    ],
    "apple_pay_or_google_pay": [
        "To add your card to Apple Pay / Google Pay: open the wallet app → Add card → follow the prompts, or start from our app under Cards → Add to Wallet.",
    ],
    "contactless_not_working": [
        "If contactless isn't working: 1) Ensure the card is activated 2) Try a different terminal 3) Check that contactless isn't disabled in the app. Still stuck? We can look deeper.",
    ],
    "lost_or_stolen_card": [
        "If your card is lost or stolen, freeze it immediately in the app, then request a replacement. Freezing takes effect right away.",
    ],
    "terminate_account": [
        "To close your account, go to Profile → Account settings → Close account, or contact support. Make sure any remaining balance is withdrawn first.",
    ],
}

GENERIC_RESPONSES = [
    "Thanks for reaching out. Based on what you said, this looks related to **{intent}**. A support agent can help further if needed. Meanwhile, you can check the Help section in the app for this topic.",
    "I've classified your message as **{intent}**. Would you like me to share common steps people take for this issue?",
    "Got it — this appears to be about **{intent}**. I can either give you quick self-serve tips or escalate to a human agent. What do you prefer?",
]

GREETINGS = [
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy"
]

GREETING_REPLIES = [
    "Hello! 👋 I'm TicketAI, your banking support assistant. How can I help you today?",
    "Hi there! I can help with cards, transfers, payments, fees and more. What's going on?",
]

THANKS = ["thank", "thanks", "thx", "appreciate"]
THANKS_REPLIES = [
    "You're welcome! Anything else I can help with?",
    "Happy to help! Feel free to ask if more issues come up.",
]


def get_bot_reply(user_message: str, confidence_threshold: float = 0.35) -> dict:
    """
    Generate a chatbot reply.
    Returns dict with: reply, intent, confidence, needs_human, suggestions
    """
    text = (user_message or "").strip()
    if not text:
        return {
            "reply": "Please type a message so I can help.",
            "intent": None,
            "confidence": 0.0,
            "needs_human": False,
            "suggestions": ["Track my card", "Change PIN", "Transfer delayed"],
        }

    lower = text.lower()

    # Simple greeting / thanks handling
    if any(g in lower for g in GREETINGS) and len(text.split()) <= 4:
        return {
            "reply": random.choice(GREETING_REPLIES),
            "intent": "greeting",
            "confidence": 1.0,
            "needs_human": False,
            "suggestions": ["My card hasn't arrived", "Change my PIN", "Payment was declined"],
        }

    if any(t in lower for t in THANKS) and len(text.split()) <= 5:
        return {
            "reply": random.choice(THANKS_REPLIES),
            "intent": "thanks",
            "confidence": 1.0,
            "needs_human": False,
            "suggestions": [],
        }

    # Use the classifier
    result = predict(text, top_k=3, confidence_threshold=confidence_threshold)
    intent = result.get("intent")
    conf = result.get("confidence", 0.0)
    needs_human = result.get("needs_human_review", True)

    # Pick response
    if intent and intent in INTENT_RESPONSES and conf >= confidence_threshold:
        reply = random.choice(INTENT_RESPONSES[intent])
    elif intent and conf >= confidence_threshold:
        reply = random.choice(GENERIC_RESPONSES).format(intent=intent.replace("_", " "))
    else:
        reply = (
            "I'm not fully sure I understood. Could you rephrase or give a bit more detail? "
            "You can also ask about cards, transfers, payments, fees, or PIN changes."
        )
        needs_human = True

    suggestions = []
    for item in result.get("top_k", [])[:3]:
        suggestions.append(item["intent"].replace("_", " ").title())

    return {
        "reply": reply,
        "intent": intent,
        "confidence": conf,
        "confidence_pct": result.get("confidence_pct", f"{conf*100:.1f}%"),
        "needs_human": needs_human,
        "suggestions": suggestions,
        "top_k": result.get("top_k", []),
    }
