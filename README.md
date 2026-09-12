# FINMITRA — Your Everyday Financial Companion

> **NEXT GEN CHATBOT ARENA — 3-Hour SDG Web-Based Chatbot Challenge**  
> **Track:** UN SDG 1 — No Poverty  
> **Tagline:** Your Everyday Financial Companion  

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.141-009688.svg)](https://fastapi.tiangolo.com)
[![Google GenAI](https://img.shields.io/badge/AI-Google%20Gemini%203.5%20Flash-4285F4.svg)](https://ai.google.dev)
[![SDG 1](https://img.shields.io/badge/UN%20SDG-1%20No%20Poverty-E5243B.svg)](https://sdgs.un.org/goals/goal1)

---

## 🌟 Overview & Problem Fit

Poverty is fundamentally exacerbated by **financial exclusion, lack of accessible financial literacy, and vulnerability to sudden life emergencies**. When low-income earners, daily wage workers, and students face unexpected expenses, the lack of an emergency cushion often forces them into predatory high-interest debt cycles.

**FINMITRA** is an empathetic, non-judgmental everyday financial companion built specifically to advance **UN Sustainable Development Goal 1: No Poverty**. 

FINMITRA empowers users to:
- **Build Realistic Budgets**: Adapt financial management to tight or variable monthly incomes without intimidating jargon.
- **Form Micro-Savings Habits**: Learn to save small amounts consistently (e.g. ₹20/day) to create starter emergency funds.
- **Distinguish Needs from Wants**: Practice behavioural frameworks like the 24-hour purchase pause.
- **Escape Debt & Avoid Scams**: Recognize predatory lending apps, understand APR vs simple interest, and avoid OTP fraud.
- **Access Verified Support**: Discover legitimate consumer protection portals and basic zero-balance banking rights without fabricated government schemes.

---

## 🚀 Live API Specification (Core Arena Evaluation)

FINMITRA exposes a production-ready, standardized external REST API endpoint:

### Primary Endpoint: `POST /chat`

- **URL:** `http://localhost:8000/chat` (or deployed base URL + `/chat`)
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`

#### Request Schema:
```json
{
  "message": "How can I start saving money with a limited income?"
}
```
*Optional multi-turn support:*
```json
{
  "message": "Can you give me 2 specific steps for that?",
  "conversation_history": [
    {"role": "user", "content": "How can I start an emergency fund?"},
    {"role": "assistant", "content": "Start with a small starter goal of ₹500..."}
  ]
}
```

#### Successful Response (HTTP 200 OK):
```json
{
  "response": "Saving money on a tight income can feel daunting, but remember that **no amount is too small to begin with**.\n\n### 1. The Micro-Buffer Rule\nStart by setting aside just ₹20 to ₹50 per day in a separate jar or digital account..."
}
```

#### Error Response Format (HTTP 422 / 429 / 500):
```json
{
  "error": "Message cannot be empty or whitespace only.",
  "code": "VALIDATION_ERROR"
}
```

---

### Example cURL Command
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I start saving money on a limited income?"}'
```

### Example Python Code
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "How much should I keep in an emergency fund?"}
)
print(response.json()["response"])
```

### Additional Endpoints:
- `GET /health` — Operational status & Gemini connectivity (`{"status": "healthy", "service": "FinMitra", "ai_status": "ready", "model": "gemini-3.5-flash"}`)
- `POST /api/budget/calculate` — Educational monthly budget breakdown and insight generation
- `GET /api/info` — Challenge metadata & endpoint summary
- `GET /docs` — Interactive Swagger/OpenAPI documentation
- `GET /` — Responsive web application

---

## 🛠️ Architecture & Tech Stack

```
finmitra/
├── .env                  # Secure server-side secrets (never exposed to client)
├── .env.example          # Template environment file
├── .gitignore            # Git safeguards for credentials & venvs
├── requirements.txt      # Production dependencies
├── run.py                # Fast ASGI server launcher
├── start.bat             # 1-click Windows startup script
├── backend/
│   ├── app.py            # FastAPI router, CORS, validation, static file mounts
│   ├── ai_service.py     # Google GenAI SDK (gemini-3.5-flash) with quota handling
│   ├── prompt.py         # SDG 1 FinMitra system prompt & safety guardrails
│   └── schemas.py        # Pydantic v2 validation models
├── frontend/
│   ├── index.html        # 7-view responsive single-page web app
│   ├── css/
│   │   └── style.css     # Accessible, calm emerald/teal design system
│   └── js/
│       ├── app.js        # SPA tab router & health status
│       ├── chat.js       # Live AI chat, markdown rendering, copy & retry
│       └── budget.js     # Real-time budget calculator & visualizer
└── tests/
    └── test_suite.py     # 33-test automated verification suite
```

### Technology Highlights:
- **Backend:** FastAPI + Uvicorn with Pydantic v2 schemas.
- **AI Engine:** Official `google-genai` SDK (v2.22.0) utilizing Google Gemini (`gemini-3.5-flash` with fallback to `gemini-3.5-flash-lite`).
- **Frontend:** Pure semantic HTML5, modern CSS3, and vanilla ES6 JavaScript. Zero build-step dependencies, ultra-fast load times, and flawless mobile responsiveness.

---

## 🛡️ Responsible AI & Security

1. **Non-Advisor Disclosure:** FinMitra clearly establishes that it provides financial education and literacy frameworks, not certified investment, tax, or legal advice.
2. **Zero Sensitive Credential Collection:** FinMitra never asks for or logs bank account numbers, PINs, passwords, OTPs, or government IDs.
3. **Anti-Hallucination Policy:** FinMitra strictly refrains from fabricating government schemes, interest rates, or eligibility rules. Public resources are categorized responsibly.
4. **Prompt-Injection Resistance:** Server-side system prompt defenses prevent extraction of system instructions or server API keys.
5. **Secret Protection:** The `GEMINI_API_KEY` is strictly confined to server-side memory and never exposed in client JavaScript or git history.

---

## ⚡ Quick Start & Local Execution

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key (`GEMINI_API_KEY`)

### 2. Setup Environment
```bash
git clone <repo-url> finmitra
cd finmitra

# Configure environment
cp .env.example .env
# Edit .env and enter your GEMINI_API_KEY
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
```bash
python run.py
```
Or on Windows: double-click `start.bat`.

The application will be live locally at:
- **Web Interface:** `http://localhost:8000/`
- **Interactive API Docs:** `http://localhost:8000/docs`

### 🌐 Live Public HTTPS Deployment

FinMitra is publicly accessible over secure HTTPS:
- **Live Web Interface:** `https://576928297f5834.lhr.life/`
- **Interactive API Swagger Docs:** `https://576928297f5834.lhr.life/docs`
- **Health Check Endpoint:** `https://576928297f5834.lhr.life/health`
- **Product Metadata Endpoint:** `https://576928297f5834.lhr.life/api/info`

---

## 🧪 Verification & Automated Tests

FinMitra provides both an offline unit test suite and a live integration test suite:

### 1. Offline Unit Test Suite (Zero Dependencies & Network-Independent)
Tests schemas, validation, budget calculations, system prompt invariants, and error mappings:
```bash
python -m unittest tests/test_unit.py -v
```

### 2. Full System & Integration Test Suite
```bash
python tests/test_suite.py
```

### Test Suite Coverage:
- `GET /` & Static Assets (CSS, JS, branding)
- `GET /health` & `GET /api/info`
- `POST /api/budget/calculate` (Surplus, Deficit, Zero-income, Ratios)
- Validation edge cases (Empty message, whitespace, missing fields, malformed JSON)
- Live AI Chat integration with `gemini-3.5-flash` (SDG 1 relevance, non-empty response)
- Multi-turn conversation context handling
- Prompt injection resistance and secret leakage prevention

---

## 👥 Target Audience & SDG 1 Impact

- **Students & First-Time Earners**: Learning to manage a first salary or allowance.
- **Daily Wage & Informal Workers**: Setting up micro-savings safety nets.
- **Low-Income Families**: Budgeting for essentials while avoiding high-interest debt traps.
- **Financially Inexperienced Individuals**: Navigating digital banking and avoiding fraud.
