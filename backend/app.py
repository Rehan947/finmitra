"""Main FastAPI application for FinMitra — SDG 1 Financial Companion."""

import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from backend.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    BudgetCalculateRequest,
    BudgetCalculateResponse,
    HealthResponse,
)
from backend.ai_service import ai_service, AIServiceError

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("finmitra.app")

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FinMitra service...")
    if ai_service.is_ready():
        logger.info(f"AI Service ready with model: {ai_service.primary_model}")
    else:
        logger.warning("AI Service starting WITHOUT valid GEMINI_API_KEY.")
    yield
    logger.info("Shutting down FinMitra service.")


app = FastAPI(
    title="FINMITRA API",
    description="SDG 1 No Poverty — Your Everyday Financial Companion API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS securely from environment or permissive for public evaluation
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*").strip()
if allowed_origins_raw == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )


# Exception handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0]["msg"] if errors else "Invalid request data."
    logger.warning(f"Validation error on {request.url.path}: {first_error}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": first_error, "code": "VALIDATION_ERROR"}
    )


# Exception handler for custom AI service errors
@app.exception_handler(AIServiceError)
async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    logger.warning(f"AIServiceError on {request.url.path}: {exc.user_message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.user_message, "code": exc.error_code}
    )


# General catch-all exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {type(exc).__name__} - {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An unexpected server error occurred. Please try again.", "code": "SERVER_ERROR"}
    )


# -------------------------------------------------------------
# Core Competition API Endpoints
# -------------------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful financial companion response"},
        422: {"model": ErrorResponse, "description": "Validation failure or empty message"},
        429: {"model": ErrorResponse, "description": "Quota / Rate limit reached"},
        500: {"model": ErrorResponse, "description": "AI provider or server failure"}
    },
    summary="Chat with FinMitra Financial Assistant",
    tags=["Chat"]
)
async def chat_endpoint(payload: ChatRequest):
    """
    Accepts a user financial message and returns an empathetic, practical SDG 1 response.
    
    - **message**: User query (required, 1-4000 chars)
    - **conversation_history**: Optional array of previous messages for multi-turn context
    """
    start_time = time.time()
    logger.info(f"Received /chat request (len: {len(payload.message)})")

    # Generate response via AI Service
    response_text = await ai_service.generate_chat_response(
        message=payload.message,
        conversation_history=payload.conversation_history
    )

    elapsed = time.time() - start_time
    logger.info(f"Generated /chat response in {elapsed:.2f}s (resp len: {len(response_text)})")
    return ChatResponse(response=response_text)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check and AI service status",
    tags=["System"]
)
async def health_check():
    """Returns the operational status of FinMitra and AI readiness without outbound billable calls."""
    ai_health = ai_service.get_health_status()
    return HealthResponse(
        status="healthy",
        service="FinMitra",
        version="1.0.0",
        ai_status=ai_health["status"],
        model=ai_health["primary_model"]
    )


@app.get(
    "/api/info",
    summary="FinMitra product and challenge metadata",
    tags=["System"]
)
async def api_info():
    return {
        "name": "FinMitra",
        "tagline": "Your Everyday Financial Companion",
        "challenge": "NEXT GEN CHATBOT ARENA — 3-Hour SDG Web-Based Chatbot Challenge",
        "track": "SDG 1 — No Poverty",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "budget_calculate": "POST /api/budget/calculate",
            "docs": "GET /docs"
        },
        "target_audience": [
            "Students",
            "Young Professionals",
            "Low-Income Households",
            "Financially Inexperienced Users"
        ]
    }


@app.post(
    "/api/budget/calculate",
    response_model=BudgetCalculateResponse,
    summary="Calculate educational monthly budget breakdown",
    tags=["Budget"]
)
async def calculate_budget(data: BudgetCalculateRequest):
    """Calculates income, essential vs non-essential expenses, savings, and actionable insights."""
    income = float(data.income)
    essential = float(data.essential_expenses)
    non_essential = float(data.non_essential_expenses)
    savings = float(data.savings)

    remaining = income - essential - non_essential - savings

    # Percentage calculations
    if income > 0:
        essential_ratio = round((essential / income) * 100, 1)
        non_essential_ratio = round((non_essential / income) * 100, 1)
        savings_ratio = round((savings / income) * 100, 1)
    else:
        essential_ratio = 0.0
        non_essential_ratio = 0.0
        savings_ratio = 0.0

    insights = []
    if income <= 0:
        status_label = "Zero Income"
        insights.append("Enter your regular monthly earnings to see a personalized breakdown.")
    elif remaining < 0:
        status_label = "Deficit (Overspending)"
        deficit_amt = abs(remaining)
        insights.append(f"Expenses and savings exceed your monthly income by ₹{deficit_amt:,.2f}.")
        insights.append("Prioritize essential needs first (rent, food, basic utilities) and review non-essential expenses.")
        insights.append("Ask FinMitra: 'How can I reduce expenses when my budget has a deficit?'")
    elif remaining == 0:
        status_label = "Balanced (Zero-Sum Budget)"
        insights.append("Every rupee of your income is allocated toward needs, wants, or savings.")
        if savings_ratio >= 15:
            insights.append("Strong savings discipline! Ensure your emergency fund has at least 1 month of essentials.")
        else:
            insights.append("Consider steadily increasing your emergency cushion as opportunities arise.")
    else:
        status_label = "Surplus (Extra Buffer Available)"
        insights.append(f"You have an unallocated monthly surplus of ₹{remaining:,.2f}.")
        insights.append("Recommended action: Direct a portion of this buffer into your starter emergency fund.")
        if non_essential_ratio > 30:
            insights.append("Your non-essential spending is over 30% of income; trimming it slightly can accelerate savings.")

    return BudgetCalculateResponse(
        income=income,
        essential_expenses=essential,
        non_essential_expenses=non_essential,
        savings=savings,
        remaining_balance=round(remaining, 2),
        essential_ratio=essential_ratio,
        non_essential_ratio=non_essential_ratio,
        savings_ratio=savings_ratio,
        status=status_label,
        insights=insights
    )


# -------------------------------------------------------------
# Frontend Static Files & SPA Serving
# -------------------------------------------------------------

# Mount static subdirectories if they exist
if os.path.exists(os.path.join(frontend_dir, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
if os.path.exists(os.path.join(frontend_dir, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")


@app.get("/", summary="FinMitra Web Application", tags=["Web"])
async def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "FinMitra is running. Frontend index.html not yet generated."})
