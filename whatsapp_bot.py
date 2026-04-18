from twilio.twiml.messaging_response import MessagingResponse
from analyzer import analyze_job_post

def handle_whatsapp_message(incoming_text):
    """
    Takes the raw WhatsApp message text,
    runs ML analysis, returns a formatted reply string.
    """
    incoming_text = incoming_text.strip()

    # Too short to analyze
    if len(incoming_text) < 30:
        return (
            "Hi! I am the Fake Job Detector bot.\n\n"
            "Forward me any job post you received — from WhatsApp, "
            "Naukri, LinkedIn, or email — and I will tell you if it is "
            "real or fake.\n\n"
            "Just paste the full job post text and send!"
        )

    # Run ML model
    result = analyze_job_post(incoming_text)

    score   = result["score"]
    verdict = result["verdict"]
    summary = result["summary"]
    flags   = result["flags"]
    missing = result.get("missing_info", [])

    # Pick emoji based on verdict
    if verdict == "Likely Fake":
        emoji = "🚨"
        warning = "Do NOT pay any fees or share Aadhaar/bank details."
    elif verdict == "Suspicious":
        emoji = "⚠️"
        warning = "Verify the company on LinkedIn or MCA portal before applying."
    else:
        emoji = "✅"
        warning = "Still verify the company independently before sharing personal info."

    # Format top flags (max 3)
    top_flags = [f for f in flags if f["severity"] != "positive"][:3]
    flag_lines = ""
    if top_flags:
        flag_lines = "\n\nRed flags found:\n"
        for f in top_flags:
            flag_lines += f"• {f['text']}\n"

    # Format missing info (max 3)
    missing_lines = ""
    if missing:
        missing_lines = "\n\nMissing from this post:\n"
        for m in missing[:3]:
            missing_lines += f"• {m}\n"

    # Build final reply
    reply = (
        f"{emoji} *FAKE JOB DETECTOR RESULT*\n"
        f"{'─' * 30}\n\n"
        f"*Verdict:* {verdict}\n"
        f"*Risk score:* {score}/100\n"
        f"*ML confidence:* {result.get('ml_confidence', '')}\n\n"
        f"{summary}"
        f"{flag_lines}"
        f"{missing_lines}\n\n"
        f"⚡ {warning}\n\n"
        f"Report fraud at: cybercrime.gov.in"
    )

    return reply


def build_twilio_response(reply_text):
    """Wraps reply in Twilio TwiML format."""
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)