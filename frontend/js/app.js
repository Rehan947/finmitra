/**
 * FinMitra — Main UI Application Controller
 * Handles SPA navigation, tab switching, health status, and cross-feature workflows.
 */

document.addEventListener("DOMContentLoaded", () => {
  const navButtons = document.querySelectorAll(".nav-btn[data-tab]");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const brandLogo = document.getElementById("brand-logo");

  // Mobile Navigation Drawer Elements
  const menuToggleBtn = document.getElementById("menu-toggle-btn");
  const drawerCloseBtn = document.getElementById("drawer-close-btn");
  const navMenu = document.getElementById("nav-menu");
  const drawerBackdrop = document.getElementById("drawer-backdrop");

  function openDrawer() {
    if (!navMenu) return;
    navMenu.classList.add("open");
    if (drawerBackdrop) drawerBackdrop.classList.add("open");
    if (menuToggleBtn) menuToggleBtn.setAttribute("aria-expanded", "true");
    document.body.classList.add("drawer-open");
  }

  function closeDrawer() {
    if (!navMenu) return;
    navMenu.classList.remove("open");
    if (drawerBackdrop) drawerBackdrop.classList.remove("open");
    if (menuToggleBtn) menuToggleBtn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("drawer-open");
  }

  if (menuToggleBtn) {
    menuToggleBtn.addEventListener("click", () => {
      const isOpen = navMenu && navMenu.classList.contains("open");
      if (isOpen) {
        closeDrawer();
      } else {
        openDrawer();
      }
    });
  }

  if (drawerCloseBtn) {
    drawerCloseBtn.addEventListener("click", closeDrawer);
  }

  if (drawerBackdrop) {
    drawerBackdrop.addEventListener("click", closeDrawer);
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && navMenu && navMenu.classList.contains("open")) {
      closeDrawer();
    }
  });

  // Tab switching function
  function switchTab(tabId) {
    closeDrawer();

    // Update active nav button
    navButtons.forEach(btn => {
      if (btn.getAttribute("data-tab") === tabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // Update active tab pane
    tabPanes.forEach(pane => {
      if (pane.id === `tab-${tabId}`) {
        pane.classList.add("active");
      } else {
        pane.classList.remove("active");
      }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Focus chat textarea if navigating to chat
    if (tabId === "chat" && window.finmitraChat && window.finmitraChat.textarea) {
      setTimeout(() => {
        window.finmitraChat.textarea.focus();
      }, 150);
    }
  }

  // Bind nav click events
  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  // Logo click returns to Landing / Home
  if (brandLogo) {
    brandLogo.addEventListener("click", () => switchTab("landing"));
  }

  // Global CTA bindings (e.g., Start Chatting, Explore Tools)
  document.querySelectorAll("[data-action='start-chat']").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      switchTab("chat");
    });
  });

  document.querySelectorAll("[data-action='explore-budget']").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      switchTab("budget");
    });
  });

  document.querySelectorAll("[data-action='explore-literacy']").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      switchTab("literacy");
    });
  });

  // Cross-feature prompt sender: Ask FinMitra about a specific topic
  document.querySelectorAll(".ask-finmitra-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const promptText = btn.getAttribute("data-prompt");
      if (promptText) {
        switchTab("chat");
        if (window.finmitraChat) {
          window.finmitraChat.sendPromptDirectly(promptText);
        }
      }
    });
  });

  // Fetch API Health Status to update UI indicators
  async function checkHealth() {
    try {
      const resp = await fetch("/health");
      if (resp.ok) {
        const data = await resp.json();
        const statusEl = document.getElementById("ai-status-indicator");
        if (statusEl) {
          if (data.ai_status === "provider_reachable" || data.ai_status === "ready") {
            statusEl.innerHTML = `<span class="status-dot"></span> FinMitra Online (${data.model})`;
          } else if (data.ai_status === "configured") {
            statusEl.innerHTML = `<span class="status-dot"></span> FinMitra Ready`;
          } else if (data.ai_status === "quota_limited") {
            statusEl.innerHTML = `<span class="status-dot" style="background-color: #f59e0b;"></span> High Traffic (Quota)`;
          } else if (data.ai_status === "authentication_failed") {
            statusEl.innerHTML = `<span class="status-dot" style="background-color: #ef4444;"></span> Key Setup Needed`;
          } else {
            statusEl.innerHTML = `<span class="status-dot" style="background-color: #d97706;"></span> Setup Pending`;
          }
        }
      }
    } catch (err) {
      console.warn("FinMitra health check warning:", err);
    }
  }

  checkHealth();
});
