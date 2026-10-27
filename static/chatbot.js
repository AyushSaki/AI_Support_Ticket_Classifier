/**
 * Chatbot frontend
 */
const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const suggestionsEl = document.getElementById("suggestions");

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addMessage(role, text, meta = {}) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  let metaHtml = "";
  if (role === "bot" && meta.intent) {
    metaHtml = `<div class="meta">Detected: <code>${meta.intent}</code> · ${meta.confidence_pct || ""}</div>`;
  }
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  div.innerHTML = `
    <div class="bubble">${text}${metaHtml}</div>
    <span class="time">${time}</span>
  `;
  chatWindow.appendChild(div);
  scrollToBottom();
}

function showSuggestions(list) {
  suggestionsEl.innerHTML = "";
  if (!list || !list.length) return;
  list.slice(0, 3).forEach((s) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "suggestion-chip";
    btn.textContent = s;
    btn.addEventListener("click", () => {
      chatInput.value = s;
      sendMessage();
    });
    suggestionsEl.appendChild(btn);
  });
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  chatInput.value = "";
  sendBtn.disabled = true;
  suggestionsEl.innerHTML = "";

  // temporary typing indicator
  const typing = document.createElement("div");
  typing.className = "msg bot typing";
  typing.innerHTML = `<div class="bubble"><span class="dots">●●●</span></div>`;
  chatWindow.appendChild(typing);
  scrollToBottom();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typing.remove();
    addMessage("bot", data.reply, {
      intent: data.intent,
      confidence_pct: data.confidence_pct,
    });
    if (data.suggestions && data.suggestions.length) {
      showSuggestions(data.suggestions);
    }
  } catch (err) {
    typing.remove();
    addMessage("bot", "Sorry, something went wrong. Please try again.");
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage();
});

// Quick starters
const starters = [
  "My card hasn't arrived yet",
  "How do I change my PIN?",
  "Payment was declined",
  "Transfer still pending",
];
showSuggestions(starters);
scrollToBottom();
