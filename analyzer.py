# Fake Job Detector India
# Copyright (c) 2026 Amit Mastud
# GitHub: github.com/Amit05-M/fake-job-detector
# All rights reserved.

import joblib
import re

# Load trained model and vectorizer once at startup
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Indian scam patterns (extra layer on top of ML)
INDIA_SCAM_PATTERNS = [
    (r"registration fee|joining fee|training fee|deposit required", "high",   "Asks for money upfront — major red flag"),
    (r"whatsapp|telegram",                                           "high",   "Contact via WhatsApp/Telegram instead of official email"),
    (r"\bgmail\.com\b|\byahoo\.com\b|\bhotmail\.com\b",             "high",   "Personal email used instead of company domain"),
    (r"guaranteed job|100% placement|sure shot",                     "high",   "Unrealistic guarantee — no real company promises this"),
    (r"no experience required|freshers only|no qualification",       "medium", "Vague requirements — common in fake posts"),
    (r"work from home.*earn|earn.*work from home",                   "medium", "Suspicious work-from-home earning claim"),
    (r"lakh.*per.*day|lakh.*per.*week|per day.*lakh",               "high",   "Unrealistic daily/weekly salary in lakhs"),
    (r"urgent.*hiring|immediate.*joining|walk.?in.*today",           "medium", "Urgency pressure tactic"),
    (r"send.*resume.*whatsapp|apply.*whatsapp",                      "high",   "Asking to apply via WhatsApp"),
    (r"data entry.*home|home.*data entry",                           "medium", "Home-based data entry — very common scam format"),
    (r"part.?time.*[5-9]\d{3,}|[5-9]\d{3,}.*part.?time",           "medium", "Unrealistically high pay for part-time work"),
]

# Positive trust signals
POSITIVE_PATTERNS = [
    (r"https?://",                                                   "Company website link provided"),
    (r"tcs|infosys|wipro|hcl|accenture|cognizant|capgemini",        "Known Indian IT company mentioned"),
    (r"linkedin\.com",                                               "LinkedIn profile referenced"),
    (r"campus.*recruitment|off.?campus|pool.*campus",               "Legitimate campus recruitment format"),
    (r"interview.*process|technical.*round|hr.*round",              "Describes proper interview process"),
]

def analyze_job_post(job_text):
    text_clean = job_text.lower()
    text_clean = re.sub(r"[^a-zA-Z0-9\s₹]", " ", text_clean)

    # ── ML Prediction ──
    features = vectorizer.transform([text_clean])
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0]

    ml_fake_prob  = proba[1]  # probability of being fake
    ml_real_prob  = proba[0]

    # ── Rule-based flags ──
    flags = []
    rule_score = 0

    # Check Indian scam patterns
    for pattern, severity, message in INDIA_SCAM_PATTERNS:
        if re.search(pattern, text_clean):
            flags.append({
                "text": message,
                "severity": severity,
                "category": "India scam pattern"
            })
            rule_score += 25 if severity == "high" else 12

    # Check positive signals
    for pattern, message in POSITIVE_PATTERNS:
        if re.search(pattern, text_clean):
            flags.append({
                "text": message,
                "severity": "positive",
                "category": "Trust signal"
            })
            rule_score -= 10

    # ── Combine ML + Rules into final score ──
    # ML gives 0-100 fake probability, rules adjust it
    ml_score   = ml_fake_prob * 100
    rule_score = max(-30, min(50, rule_score))  # clamp rules
    final_score = int(min(100, max(0, ml_score * 0.7 + rule_score * 0.3)))

    # ── Verdict ──
    if final_score >= 60:
        verdict = "Likely Fake"
    elif final_score >= 30:
        verdict = "Suspicious"
    else:
        verdict = "Likely Legitimate"

    # ── Default flag if none triggered ──
    if not flags:
        flags.append({
            "text": "No major red flags detected in language patterns",
            "severity": "positive",
            "category": "General"
        })

    # ── Missing info check ──
    missing = []
    if not re.search(r"https?://", job_text):
        missing.append("Company website URL")
    if not re.search(r"interview|selection process", text_clean):
        missing.append("Interview / selection process details")
    if not re.search(r"salary|ctc|lpa|lakh|stipend|compensation", text_clean):
        missing.append("Salary or CTC details")
    if not re.search(r"@(?!gmail|yahoo|hotmail)", text_clean):
        missing.append("Official company email domain")
    if not re.search(r"linkedin|naukri|glassdoor|indeed", text_clean):
        missing.append("Reference to a verified job portal")

    # ── Summary ──
    if verdict == "Likely Fake":
        summary = (f"Our ML model flagged this post with {ml_fake_prob:.0%} fake probability. "
                   f"Combined with {len([f for f in flags if f['severity'] != 'positive'])} "
                   f"suspicious pattern(s), this post scores {final_score}/100 risk. "
                   f"Do not share personal information or pay any fees.")
    elif verdict == "Suspicious":
        summary = (f"The ML model gave this a {ml_fake_prob:.0%} fake probability. "
                   f"Some elements look suspicious. Verify the company independently "
                   f"on LinkedIn or Naukri before applying. Risk score: {final_score}/100.")
    else:
        summary = (f"The ML model gives this post only {ml_fake_prob:.0%} fake probability. "
                   f"It appears mostly legitimate. Risk score: {final_score}/100. "
                   f"Still verify the company before sharing personal details.")

    return {
        "score":        final_score,
        "verdict":      verdict,
        "ml_confidence": f"{ml_real_prob:.0%} confident it is real",
        "flags":        flags,
        "summary":      summary,
        "missing_info": missing
    }