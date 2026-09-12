/**
 * FinMitra — AI Chat Module
 * Manages chat interactions, streaming/request handling, markdown rendering, copy & retry.
 */

class ChatManager {
  constructor() {
    this.messagesContainer = document.getElementById("chat-messages");
    this.textarea = document.getElementById("chat-textarea");
    this.sendBtn = document.getElementById("chat-send-btn");
    this.errorBanner = document.getElementById("chat-error-banner");
    this.errorMessage = document.getElementById("chat-error-text");
    this.retryBtn = document.getElementById("chat-retry-btn");
    this.chipsContainer = document.getElementById("chat-chips-bar");

    this.messages = [];
    this.isLoading = false;
    this.lastFailedMessage = null;

    this.init();
  }

  init() {
    if (!this.textarea || !this.sendBtn) return;

    // Send button click
    this.sendBtn.addEventListener("click", () => this.handleSend());

    // Textarea keyboard shortcuts
    this.textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handleSend();
      }
    });

    // Auto-resize textarea
    this.textarea.addEventListener("input", () => {
      this.textarea.style.height = "auto";
      this.textarea.style.height = Math.min(this.textarea.scrollHeight, 140) + "px";
      this.updateSendButtonState();
    });

    // Retry button click
    if (this.retryBtn) {
      this.retryBtn.addEventListener("click", () => {
        if (this.lastFailedMessage) {
          this.hideError();
          this.sendMessage(this.lastFailedMessage);
        }
      });
    }

    // Suggested prompt chips
    if (this.chipsContainer) {
      this.chipsContainer.addEventListener("click", (e) => {
        const chip = e.target.closest(".chat-chip");
        if (chip) {
          const promptText = chip.getAttribute("data-prompt") || chip.textContent.trim();
          this.sendPromptDirectly(promptText);
        }
      });
    }

    // Initial greeting if empty
    if (this.messages.length === 0) {
      this.appendAssistantMessage(
        "Namaste! I am **FinMitra**, your everyday financial companion.\n\n" +
        "I'm here to help you navigate practical budgeting, building a safety buffer, cutting unnecessary costs, and understanding financial choices—especially on a tight budget.\n\n" +
        "What financial question or goal would you like to explore today?"
      );
    }
  }

  updateSendButtonState() {
    const text = this.textarea.value.trim();
    this.sendBtn.disabled = this.isLoading || text.length === 0;
  }

  sendPromptDirectly(promptText) {
    this.textarea.value = promptText;
    this.textarea.focus();
    this.handleSend();
  }

  handleSend() {
    if (this.isLoading) return;
    const text = this.textarea.value.trim();
    if (!text) return;

    this.hideError();
    this.textarea.value = "";
    this.textarea.style.height = "auto";
    this.updateSendButtonState();

    this.sendMessage(text);
  }

  async sendMessage(userText) {
    this.isLoading = true;
    this.updateSendButtonState();

    // 1. Render user message
    this.appendUserMessage(userText);
    this.messages.push({ role: "user", content: userText });

    // 2. Show loading indicator
    this.showTypingIndicator();
    this.scrollToBottom();

    try {
      // 3. Send request to backend /chat
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: userText,
          conversation_history: this.messages.slice(-4)
        })
      });

      this.removeTypingIndicator();

      if (!response.ok) {
        let errData = {};
        try {
          errData = await response.json();
        } catch (_) {}

        const status = response.status;
        const errCode = errData.code || "";
        let userFacingError = "FINMITRA is temporarily unable to reach the AI service. Please try again shortly.";

        if (status === 401 || errCode === "AUTH_FAILED" || errCode === "API_KEY_MISSING") {
          userFacingError = "FINMITRA's AI service is not authenticated yet. Please try again after the service configuration is completed.";
        } else if (status === 429 || errCode === "RATE_LIMIT_OR_QUOTA") {
          userFacingError = "FINMITRA is temporarily receiving too many requests. Please wait a moment and try again.";
        } else if (status === 504 || errCode === "TIMEOUT") {
          userFacingError = "The AI service took too long to respond. Please try again.";
        } else if (status === 422 || errCode === "VALIDATION_ERROR") {
          userFacingError = errData.error || "Please enter a valid financial question (up to 4000 characters).";
        } else if (status === 502 || errCode === "EMPTY_RESPONSE") {
          userFacingError = errData.error || "FINMITRA is temporarily unable to reach the AI service. Please try again shortly.";
        } else if (errData.error) {
          userFacingError = errData.error;
        }

        this.lastFailedMessage = userText;
        this.showError(userFacingError);
        return;
      }

      const data = await response.json();
      const botResponse = data.response || "No response received.";

      // 4. Render assistant response
      this.appendAssistantMessage(botResponse);
      this.messages.push({ role: "assistant", content: botResponse });
      this.lastFailedMessage = null;

    } catch (error) {
      console.error("Chat network error:", error);
      this.removeTypingIndicator();
      this.lastFailedMessage = userText;
      this.showError("FINMITRA is temporarily unable to reach the AI service. Please try again shortly.");
    } finally {
      this.isLoading = false;
      this.updateSendButtonState();
      this.scrollToBottom();
    }
  }

  appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "message-row user";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    row.appendChild(bubble);
    this.messagesContainer.appendChild(row);
  }

  appendAssistantMessage(markdownText) {
    const row = document.createElement("div");
    row.className = "message-row assistant";

    const avatar = document.createElement("div");
    avatar.className = "chat-avatar";
    avatar.textContent = "FM";

    const contentWrapper = document.createElement("div");
    contentWrapper.style.display = "flex";
    contentWrapper.style.flexDirection = "column";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = this.renderMarkdown(markdownText);

    const actions = document.createElement("div");
    actions.className = "message-actions";

    const copyBtn = document.createElement("button");
    copyBtn.className = "msg-action-btn";
    copyBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg> Copy
    `;
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(markdownText).then(() => {
        copyBtn.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="green" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg> Copied!
        `;
        setTimeout(() => {
          copyBtn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg> Copy
          `;
        }, 2000);
      });
    });

    actions.appendChild(copyBtn);
    contentWrapper.appendChild(bubble);
    contentWrapper.appendChild(actions);

    row.appendChild(avatar);
    row.appendChild(contentWrapper);

    this.messagesContainer.appendChild(row);
  }

  showTypingIndicator() {
    if (document.getElementById("typing-indicator")) return;

    const indicator = document.createElement("div");
    indicator.id = "typing-indicator";
    indicator.className = "typing-indicator";
    indicator.innerHTML = `
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <span class="typing-label">FinMitra is preparing practical guidance...</span>
    `;
    this.messagesContainer.appendChild(indicator);
  }

  removeTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) {
      indicator.remove();
    }
  }

  showError(message) {
    if (this.errorMessage) this.errorMessage.textContent = message;
    if (this.errorBanner) this.errorBanner.style.display = "flex";
  }

  hideError() {
    if (this.errorBanner) this.errorBanner.style.display = "none";
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  renderMarkdown(text) {
    if (!text) return "";

    // Escape HTML tags to prevent XSS
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Headers
    html = html.replace(/^#### (.*$)/gim, "<h5 class='msg-h5'>$1</h5>");
    html = html.replace(/^### (.*$)/gim, "<h4 class='msg-h4'>$1</h4>");
    html = html.replace(/^## (.*$)/gim, "<h3 class='msg-h3'>$1</h3>");
    html = html.replace(/^# (.*$)/gim, "<h3 class='msg-h3'>$1</h3>");

    // Horizontal divider
    html = html.replace(/^---$/gim, "<hr class='msg-hr'>");
    html = html.replace(/^\*\*\*$/gim, "<hr class='msg-hr'>");

    // Bold (**text**)
    html = html.replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>");

    // Inline code (`code`)
    html = html.replace(/`([^`]+)`/gim, "<code class='msg-code'>$1</code>");

    // Process lists line by line
    const lines = html.split("\n");
    const processed = [];
    let inOl = false;
    let inUl = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const olMatch = line.match(/^\s*(\d+)[\.\)]\s+(.*)$/);
      const ulMatch = line.match(/^\s*[-*•]\s+(.*)$/);

      if (olMatch) {
        if (inUl) {
          processed.push("</ul>");
          inUl = false;
        }
        if (!inOl) {
          processed.push("<ol class='msg-ol'>");
          inOl = true;
        }
        processed.push(`<li>${olMatch[2]}</li>`);
      } else if (ulMatch) {
        if (inOl) {
          processed.push("</ol>");
          inOl = false;
        }
        if (!inUl) {
          processed.push("<ul class='msg-ul'>");
          inUl = true;
        }
        processed.push(`<li>${ulMatch[1]}</li>`);
      } else {
        if (inOl) {
          processed.push("</ol>");
          inOl = false;
        }
        if (inUl) {
          processed.push("</ul>");
          inUl = false;
        }
        processed.push(line);
      }
    }

    if (inOl) processed.push("</ol>");
    if (inUl) processed.push("</ul>");

    html = processed.join("\n");

    // Paragraph wrapping
    const paragraphs = html.split(/\n\s*\n/);
    const result = paragraphs.map(p => {
      p = p.trim();
      if (!p) return "";
      if (p.startsWith("<ol") || p.startsWith("<ul") || p.startsWith("<h3") || p.startsWith("<h4") || p.startsWith("<h5") || p.startsWith("<hr")) {
        return p;
      }
      return "<p class='msg-p'>" + p.replace(/\n/g, "<br>") + "</p>";
    }).filter(Boolean).join("");

    return result;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.finmitraChat = new ChatManager();
});
