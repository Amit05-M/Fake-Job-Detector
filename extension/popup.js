const API_URL = "https://fake-job-detector-np6q.onrender.com";
// ── Button listeners ──
document.getElementById("analyzePageBtn").addEventListener("click", analyzePage);
document.getElementById("analyzeManualBtn").addEventListener("click", analyzeManual);
document.getElementById("backBtn").addEventListener("click", goHome);
document.getElementById("retryBtn").addEventListener("click", goHome);

// ── Analyze current browser tab ──
async function analyzePage() {
  showLoading();
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Inject content script and get job text
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"]
    });

    const response = await chrome.tabs.sendMessage(tab.id, { action: "getJobText" });
    const jobText  = response?.text || "";

    if (!jobText || jobText.length < 50) {
      showError("Could not extract job text from this page.\n\nTry pasting the job post manually instead.");
      return;
    }

    await runAnalysis(jobText);

  } catch (err) {
    showError("Make sure you are on a job listing page (Naukri, LinkedIn, Indeed).\n\nOr paste the job text manually.");
  }
}

// ── Analyze manually pasted text ──
async function analyzeManual() {
  const text = document.getElementById("manualText").value.trim();
  if (!text || text.length < 50) {
    alert("Please paste a job post first (at least 50 characters).");
    return;
  }
  showLoading();
  await runAnalysis(text);
}

// ── Call Flask API ──
async function runAnalysis(jobText) {
  try {
    const res = await fetch(API_URL + "/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_text: jobText })
    });

    if (!res.ok) throw new Error("Server error: " + res.status);

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    renderResult(data);

  } catch (err) {
    if (err.message.includes("Failed to fetch")) {
      showError("Cannot reach the ML server.\n\nMake sure app.py is running:\npython app.py");
    } else {
      showError("Error: " + err.message);
    }
  }
}

// ── Render result ──
function renderResult(data) {
  const { score, verdict, ml_confidence, flags, summary, missing_info } = data;

  // Score circle
  const circle = document.getElementById("scoreCircle");
  circle.className = "score-circle";
  if (score >= 60)      circle.classList.add("red");
  else if (score >= 30) circle.classList.add("amber");
  else                  circle.classList.add("green");

  document.getElementById("scoreNum").textContent  = score;
  document.getElementById("verdict").textContent   = verdict;
  document.getElementById("mlConf").textContent    = ml_confidence || "";

  const subs = {
    "Likely Fake":      "Do not apply or share personal info",
    "Suspicious":       "Verify company before applying",
    "Likely Legitimate":"Still verify independently"
  };
  document.getElementById("verdictSub").textContent = subs[verdict] || "";
  document.getElementById("summary").textContent    = summary;

  // Flags
  document.getElementById("flags").innerHTML = (flags || []).map(f => `
    <div class="flag-item">
      <div class="flag-dot dot-${f.severity}"></div>
      <div class="flag-text">${f.text}</div>
    </div>
  `).join("");

  // Missing info
  const wrap = document.getElementById("missingWrap");
  if (missing_info && missing_info.length > 0) {
    wrap.style.display = "block";
    document.getElementById("missing").innerHTML =
      missing_info.map(m => `<span class="missing-tag">${m}</span>`).join("");
  } else {
    wrap.style.display = "none";
  }

  show("result");
}

// ── UI helpers ──
function showLoading() { show("loading"); }
function goHome()      { show("home"); }

function showError(msg) {
  document.getElementById("errorMsg").textContent = msg;
  show("error");
}

function show(section) {
  ["home", "loading", "result", "error"].forEach(id => {
    document.getElementById(id).classList.toggle("hidden", id !== section);
  });
}