const messagesEl = document.getElementById("messages");
const welcomeEl = document.getElementById("welcome-state");
const inputEl = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
}

function askSuggestion(btn) {
  inputEl.value = btn.textContent;
  autoResize(inputEl);
  sendQuestion();
}

function scrollBottom() {
  const area = document.getElementById("chat-area");
  area.scrollTop = area.scrollHeight;
}

function addMessage(role, html, sources = []) {
  if (welcomeEl) welcomeEl.style.display = "none";

  const msg = document.createElement("div");
  msg.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role === "user" ? "user-av" : "ai-av"}`;
  avatar.textContent = role === "user" ? "You" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = html;

  if (sources.length) {
    const tags = document.createElement("div");
    tags.className = "sources-tag";
    sources.forEach(s => {
      const chip = document.createElement("span");
      chip.className = "source-chip";
      chip.textContent = "📄 " + s;
      tags.appendChild(chip);
    });
    bubble.appendChild(tags);
  }

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  scrollBottom();
  return msg;
}

function addTyping() {
  if (welcomeEl) welcomeEl.style.display = "none";
  const msg = document.createElement("div");
  msg.className = "message ai";
  msg.id = "typing-msg";

  const avatar = document.createElement("div");
  avatar.className = "avatar ai-av";
  avatar.textContent = "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble typing-bubble";
  bubble.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  messagesEl.appendChild(msg);
  scrollBottom();
}

function removeTyping() {
  const t = document.getElementById("typing-msg");
  if (t) t.remove();
}

function formatAnswer(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>")
    .replace(/^/, "<p>")
    .replace(/$/, "</p>");
}

async function sendQuestion() {
  const question = inputEl.value.trim();
  if (!question) return;

  addMessage("user", question);
  inputEl.value = "";
  inputEl.style.height = "auto";
  sendBtn.disabled = true;
  addTyping();

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    removeTyping();

    if (data.error) {
      addMessage("ai", `<span class="error-text">⚠️ ${data.error}</span>`);
    } else {
      addMessage("ai", formatAnswer(data.answer), data.sources || []);
    }
  } catch (err) {
    removeTyping();
    addMessage("ai", `<span class="error-text">⚠️ Connection error. Make sure the server is running.</span>`);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}
