// Vishnu Gita — Frontend Chat Logic

// Works on both local and deployed (Render/any host)
const API_URL = window.location.origin + "/chat";
let chatHistory = [];
let isLoading = false;

const chatWindow  = document.getElementById("chatWindow");
const inputBox    = document.getElementById("inputBox");
const sendBtn     = document.getElementById("sendBtn");
const sourcesBar  = document.getElementById("sourcesBar");
const sourcesList = document.getElementById("sourcesList");
const statusDot   = document.getElementById("statusDot");
const statusText  = document.getElementById("statusText");
const scrollBtn   = document.getElementById("scrollBtn");

// ── Auto-resize textarea ──
inputBox.addEventListener("input", onInputChange);

function onInputChange() {
  inputBox.style.height = "auto";
  inputBox.style.height = Math.min(inputBox.scrollHeight, 130) + "px";
}

// ── Keyboard handler ──
function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ── Fill suggestion chips ──
function fillSuggestion(btn) {
  inputBox.value = btn.textContent;
  onInputChange();
  inputBox.focus();
  // Highlight the chip briefly
  btn.style.background = "rgba(240,192,64,0.3)";
  btn.style.borderColor = "#f0c040";
  setTimeout(() => {
    btn.style.background = "";
    btn.style.borderColor = "";
  }, 600);
  sendMessage();
}

// ── Scroll handling ──
chatWindow.addEventListener("scroll", () => {
  const nearBottom = chatWindow.scrollHeight - chatWindow.scrollTop - chatWindow.clientHeight < 120;
  scrollBtn.classList.toggle("visible", !nearBottom);
});

function scrollToBottom(smooth = true) {
  chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: smooth ? "smooth" : "instant" });
}

// ── Render markdown-like text ──
function renderText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/_(.*?)_/g, "<em>$1</em>");
}

// ── Add a message bubble ──
function addMessage(role, content) {
  const msg = document.createElement("div");
  msg.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "bot" ? "ॐ" : "You";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  // Split into paragraphs
  const paras = content.split(/\n+/).filter(p => p.trim());
  bubble.innerHTML = paras.map(p => `<p>${renderText(p)}</p>`).join("");

  // Copy button (only for bot)
  if (role === "bot") {
    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn";
    copyBtn.textContent = "COPY";
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(content).then(() => {
        copyBtn.textContent = "COPIED!";
        setTimeout(() => { copyBtn.textContent = "COPY"; }, 1500);
      });
    };
    bubble.appendChild(copyBtn);
  }

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatWindow.appendChild(msg);
  scrollToBottom();
  return msg;
}

// ── Typing indicator ──
function showTyping() {
  const msg = document.createElement("div");
  msg.className = "message bot typing";
  msg.id = "typingIndicator";
  msg.innerHTML = `
    <div class="avatar">ॐ</div>
    <div class="bubble">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>`;
  chatWindow.appendChild(msg);
  scrollToBottom();
}
function hideTyping() {
  document.getElementById("typingIndicator")?.remove();
}

// ── Sources ──
function showSources(sources) {
  if (!sources?.length) { sourcesBar.style.display = "none"; return; }
  const cleaned = sources.filter(s => s?.trim());
  if (!cleaned.length) { sourcesBar.style.display = "none"; return; }
  sourcesList.innerHTML = cleaned
    .map(s => `<span class="source-chip">${s}</span>`)
    .join("");
  sourcesBar.style.display = "flex";
}

// ── Main send function ──
async function sendMessage() {
  const question = inputBox.value.trim();
  if (!question || isLoading) return;

  // Hide welcome card on first message
  const welcome = document.querySelector(".welcome-card");
  if (welcome) welcome.style.display = "none";

  // Reset input
  inputBox.value = "";
  inputBox.style.height = "auto";
  sourcesBar.style.display = "none";

  addMessage("user", question);
  chatHistory.push({ role: "user", content: question });

  isLoading = true;
  sendBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        history: chatHistory.slice(-8)
      })
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    hideTyping();
    addMessage("bot", data.answer);
    showSources(data.sources);
    chatHistory.push({ role: "assistant", content: data.answer });
    if (chatHistory.length > 24) chatHistory = chatHistory.slice(-24);

  } catch (err) {
    hideTyping();
    addMessage("bot",
      `Unable to connect to the wisdom source. Please ensure the backend server is running.\n\n_${err.message}_`
    );
    setStatus("offline");
  } finally {
    isLoading = false;
    sendBtn.disabled = false;
    inputBox.focus();
  }
}

// ── Status helpers ──
function setStatus(state) {
  statusDot.className = `status-dot ${state}`;
  if (state === "online")  statusText.textContent = "Connected";
  if (state === "offline") statusText.textContent = "Offline";
  if (state === "")        statusText.textContent = "Connecting...";
}

// ── Health check on load ──
window.addEventListener("load", async () => {
  try {
    const res = await fetch(window.location.origin + "/health");
    if (res.ok) setStatus("online");
    else setStatus("offline");
  } catch {
    setStatus("offline");
  }
});
