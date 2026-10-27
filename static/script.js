/**
 * Frontend logic for AI Support Ticket Classifier
 */

const form = document.getElementById("classify-form");
const textarea = document.getElementById("ticket-text");
const classifyBtn = document.getElementById("classify-btn");
const clearBtn = document.getElementById("clear-btn");
const resultEl = document.getElementById("result");
const loadingEl = document.getElementById("loading");
const intentName = document.getElementById("intent-name");
const confidenceValue = document.getElementById("confidence-value");
const reviewBanner = document.getElementById("review-banner");
const topKList = document.getElementById("top-k-list");

// Example tickets for quick testing
const EXAMPLES = [
  "My card hasn't arrived yet after two weeks",
  "I was charged a fee for a cash withdrawal",
  "How do I change my PIN?",
  "The transfer I made yesterday still hasn't arrived",
  "My card payment was declined at the store",
  "I need to activate my new card",
];

function showLoading(show) {
  loadingEl.classList.toggle("hidden", !show);
  classifyBtn.disabled = show;
}

function setConfidenceClass(el, conf) {
  el.classList.remove("high", "medium", "low");
  if (conf >= 0.7) el.classList.add("high");
  else if (conf >= 0.45) el.classList.add("medium");
  else el.classList.add("low");
}

function renderResult(data) {
  if (data.error) {
    intentName.textContent = "Error";
    confidenceValue.textContent = "—";
    reviewBanner.classList.add("hidden");
    topKList.innerHTML = `<li>${data.error}</li>`;
    resultEl.classList.remove("hidden");
    return;
  }

  intentName.textContent = data.intent;
  confidenceValue.textContent = data.confidence_pct;
  setConfidenceClass(confidenceValue, data.confidence);

  if (data.needs_human_review) {
    reviewBanner.classList.remove("hidden");
  } else {
    reviewBanner.classList.add("hidden");
  }

  topKList.innerHTML = "";
  (data.top_k || []).forEach((item, i) => {
    const li = document.createElement("li");
    const pct = (item.confidence * 100).toFixed(1);
    li.innerHTML = `
      <span class="intent">${i + 1}. ${item.intent}</span>
      <span class="bar-wrap">
        <span class="bar"><span class="bar-fill" style="width: ${pct}%"></span></span>
        <span class="pct">${item.confidence_pct}</span>
      </span>
    `;
    topKList.appendChild(li);
  });

  resultEl.classList.remove("hidden");
}

async function classify() {
  const text = textarea.value.trim();
  if (!text) {
    textarea.focus();
    return;
  }

  showLoading(true);
  resultEl.classList.add("hidden");

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    renderResult(data);

    // Optionally refresh history section after a short delay
    // (simple approach: user can reload if they want latest history)
  } catch (err) {
    renderResult({ error: "Request failed: " + err.message });
  } finally {
    showLoading(false);
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  classify();
});

clearBtn.addEventListener("click", () => {
  textarea.value = "";
  resultEl.classList.add("hidden");
  textarea.focus();
});

// Double-click textarea to insert a random example
textarea.addEventListener("dblclick", () => {
  if (!textarea.value.trim()) {
    const ex = EXAMPLES[Math.floor(Math.random() * EXAMPLES.length)];
    textarea.value = ex;
  }
});

// Smooth scroll for nav
document.querySelectorAll(".nav-item").forEach((link) => {
  link.addEventListener("click", (e) => {
    const href = link.getAttribute("href");
    if (href && href.startsWith("#")) {
      e.preventDefault();
      document.querySelectorAll(".nav-item").forEach((l) => l.classList.remove("active"));
      link.classList.add("active");
      const target = document.querySelector(href);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});
