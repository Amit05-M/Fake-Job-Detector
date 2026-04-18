// Runs on job site pages automatically
// Extracts job post text intelligently from each site

function extractJobText() {
  const url = window.location.href;
  let text = "";

  // ── Naukri ──
  if (url.includes("naukri.com")) {
    const selectors = [
      ".job-desc",
      ".dang-inner-html",
      ".job-details-content",
      "[class*='description']",
      "[class*='jobDescription']"
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) { text += el.innerText + " "; }
    }
    // Also grab title and company
    const title   = document.querySelector(".jd-header-title, h1");
    const company = document.querySelector(".jd-header-comp-name, .comp-name");
    const salary  = document.querySelector(".salary-estimate, [class*='salary']");
    if (title)   text = title.innerText + " " + text;
    if (company) text = company.innerText + " " + text;
    if (salary)  text += " " + salary.innerText;
  }

  // ── LinkedIn ──
  else if (url.includes("linkedin.com")) {
    const selectors = [
      ".jobs-description__content",
      ".description__text",
      "[class*='job-description']",
      ".jobs-box__html-content"
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) { text += el.innerText + " "; }
    }
    const title   = document.querySelector("h1.job-details-jobs-unified-top-card__job-title, h1");
    const company = document.querySelector(".job-details-jobs-unified-top-card__company-name, .topcard__org-name-link");
    if (title)   text = title.innerText + " " + text;
    if (company) text = company.innerText + " " + text;
  }

  // ── Indeed ──
  else if (url.includes("indeed.com")) {
    const selectors = [
      "#jobDescriptionText",
      ".jobsearch-jobDescriptionText",
      "[class*='jobDescription']"
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) { text += el.innerText + " "; }
    }
    const title   = document.querySelector("h1.jobsearch-JobInfoHeader-title, h1");
    const company = document.querySelector("[data-testid='inlineHeader-companyName'], .jobsearch-CompanyInfoContainer");
    if (title)   text = title.innerText + " " + text;
    if (company) text = company.innerText + " " + text;
  }

  // ── Fallback: any other job site ──
  else {
    // Try common patterns used by most job sites
    const fallbackSelectors = [
      "article",
      "[class*='description']",
      "[class*='job-detail']",
      "[class*='posting']",
      "main"
    ];
    for (const sel of fallbackSelectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText.length > 100) {
        text += el.innerText + " ";
        break;
      }
    }
  }

  // Final cleanup
  text = text.replace(/\s+/g, " ").trim();
  return text;
}

// Listen for message from popup.js asking for page text
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getJobText") {
    const text = extractJobText();
    sendResponse({ text: text });
  }
  return true;
});