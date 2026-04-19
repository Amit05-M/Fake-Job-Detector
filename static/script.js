const FAKE_EXAMPLE = `Urgent Hiring — Work From Home Data Entry Job
Salary: ₹45,000 - ₹70,000 per week
Location: Any city in India — fully remote

We are urgently hiring for home-based data entry jobs across India.
No experience required. No qualification needed. Freshers welcome.
You will earn guaranteed ₹45,000 per week working just 2-3 hours daily.

Requirements:
- Must be 18+
- Basic smartphone required
- Registration fee of ₹500 only (refundable)
- Send your resume on WhatsApp: +91-9999988888

Apply today — only 5 seats left! Contact us on Telegram or WhatsApp only.
Send your Aadhaar number and bank details to confirm your seat.
jobs.india.hiring2024@gmail.com`;

const REAL_EXAMPLE = `Software Engineer — Backend (Java)
Company: Infosys Limited
Location: Bangalore, Karnataka (Hybrid)
CTC: ₹8 LPA - ₹14 LPA

About Infosys:
Infosys is a global leader in next-generation digital services and consulting.
Visit us at https://www.infosys.com/careers

Responsibilities:
- Design and develop scalable backend services using Java and Spring Boot
- Collaborate with cross-functional teams on product features
- Write unit tests and participate in code reviews

Requirements:
- B.Tech/BE in Computer Science or related field
- 2-4 years of Java development experience
- Strong knowledge of Spring Boot, REST APIs, SQL

Selection Process:
- Online coding test
- Technical interview round 1 and 2
- HR round

Apply at: https://infosys.com/careers or LinkedIn
Email: careers@infosys.com`;


function loadExample(type) {
  document.getElementById('jobText').value =
    type === 'fake' ? FAKE_EXAMPLE : REAL_EXAMPLE;
  document.getElementById('result').classList.add('hidden');
}

async function analyze() {
  const text = document.getElementById('jobText').value.trim();
  if (!text) { alert('Please paste a job post first.'); return; }

  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('result').classList.add('hidden');

  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_text: text })
    });

    const data = await res.json();
    if (data.error) { alert('Error: ' + data.error); return; }
    renderResult(data);

  } catch (err) {
    alert('Cannot connect to server. Make sure app.py is running.');
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

function renderResult(data) {
  const { score, verdict, ml_confidence, flags, summary, missing_info } = data;

  // Score circle color
  const circle = document.getElementById('scoreCircle');
  circle.className = 'score-circle';
  if (score >= 60)      circle.classList.add('red');
  else if (score >= 30) circle.classList.add('amber');
  else                  circle.classList.add('green');

  document.getElementById('scoreNumber').textContent = score;
  document.getElementById('verdict').textContent = verdict;
  document.getElementById('mlConfidence').textContent = 'ML model: ' + ml_confidence;

  const subs = {
    'Likely Fake':      'High risk — do not pay any fees or share Aadhaar/bank details',
    'Suspicious':       'Proceed carefully — verify the company on LinkedIn or Naukri first',
    'Likely Legitimate':'Low risk — still verify before sharing personal info'
  };
  document.getElementById('verdictSub').textContent = subs[verdict] || '';
  document.getElementById('summary').textContent = summary;

  // Flags
  document.getElementById('flags').innerHTML = flags.map(f => `
    <div class="flag-item">
      <div class="flag-dot dot-${f.severity}"></div>
      <div>
        <div class="flag-text">${f.text}</div>
        <div class="flag-meta">${f.category} · ${f.severity}</div>
      </div>
    </div>
  `).join('');

  // Missing info
  const missingCard = document.getElementById('missingCard');
  const missingDiv  = document.getElementById('missing');
  if (missing_info && missing_info.length > 0) {
    missingCard.classList.remove('hidden');
    missingDiv.innerHTML = `<div class="missing-grid">
      ${missing_info.map(m => `<span class="missing-tag">${m}</span>`).join('')}
    </div>`;
  } else {
    missingCard.classList.add('hidden');
  }

  document.getElementById('result').classList.remove('hidden');
  document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
}