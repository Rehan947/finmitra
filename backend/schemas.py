"""Pydantic request and response schemas for FinMitra API."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ChatMessageItem(BaseModel):
    role: str = Field(..., description="Role of the sender: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=10000, description="Message text content")


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User question or financial query",
        examples=["How can I start saving money on a limited income?"]
    )
    conversation_history: Optional[List[ChatMessageItem]] = Field(
        default=None,
        description="Optional prior messages for conversation context (up to 10 turns)"
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty or whitespace only.")
        return trimmed


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant response text")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Human-readable error explanation")
    code: Optional[str] = Field(default=None, description="Standard error code")


class BudgetCalculateRequest(BaseModel):
    income: float = Field(..., ge=0, description="Total monthly income")
    essential_expenses: float = Field(default=0.0, ge=0, description="Essential costs: housing, food, utilities, debt minimums")
    non_essential_expenses: float = Field(default=0.0, ge=0, description="Discretionary costs: dining out, entertainment, subscriptions")
    savings: float = Field(default=0.0, ge=0, description="Monthly amount dedicated to savings or emergency fund")


class BudgetCalculateResponse(BaseModel):
    income: float
    essential_expenses: float
    non_essential_expenses: float
    savings: float
    remaining_balance: float
    essential_ratio: float
    non_essential_ratio: float
    savings_ratio: float
    status: str
    insights: List[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    ai_status: str
    model: str
