"""Offline Unit Test Suite for FinMitra.
100% network-independent and offline. Standard unittest compatible.
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import app
from backend.prompt import SYSTEM_PROMPT
from backend.schemas import ChatRequest, BudgetCalculateRequest

client = TestClient(app)


class TestValidationAndSchemas(unittest.TestCase):
    """Tests Pydantic models and request validation."""

    def test_chat_request_valid(self):
        req = ChatRequest(message="How to save on a low income?")
        self.assertEqual(req.message, "How to save on a low income?")
        self.assertIsNone(req.conversation_history)

    def test_chat_request_rejects_empty_and_whitespace(self):
        with self.assertRaises(ValueError):
            ChatRequest(message="")
        with self.assertRaises(ValueError):
            ChatRequest(message="   \n\t  ")

    def test_chat_endpoint_validation_422_on_empty(self):
        resp = client.post("/chat", json={"message": "   "})
        self.assertEqual(resp.status_code, 422)
        data = resp.json()
        self.assertIn("error", data)
        self.assertEqual(data.get("code"), "VALIDATION_ERROR")

    def test_chat_endpoint_validation_422_on_missing_body(self):
        resp = client.post("/chat", json={})
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(resp.json().get("code"), "VALIDATION_ERROR")


class TestBudgetCalculationAPI(unittest.TestCase):
    """Tests /api/budget/calculate with various financial conditions."""

    def test_surplus_calculation(self):
        payload = {
            "income": 30000,
            "essential_expenses": 15000,
            "non_essential_expenses": 5000,
            "savings": 3000
        }
        resp = client.post("/api/budget/calculate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["remaining_balance"], 7000.0)
        self.assertEqual(data["essential_ratio"], 50.0)
        self.assertEqual(data["non_essential_ratio"], 16.7)
        self.assertEqual(data["savings_ratio"], 10.0)
        self.assertIn("Surplus", data["status"])
        self.assertTrue(len(data["insights"]) > 0)

    def test_deficit_calculation(self):
        payload = {
            "income": 20000,
            "essential_expenses": 16000,
            "non_essential_expenses": 6000,
            "savings": 1000
        }
        resp = client.post("/api/budget/calculate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["remaining_balance"], -3000.0)
        self.assertIn("Deficit", data["status"])
        self.assertTrue(any("₹3,000" in insight or "exceed" in insight for insight in data["insights"]))

    def test_zero_sum_budget(self):
        payload = {
            "income": 25000,
            "essential_expenses": 15000,
            "non_essential_expenses": 5000,
            "savings": 5000
        }
        resp = client.post("/api/budget/calculate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["remaining_balance"], 0.0)
        self.assertIn("Balanced", data["status"])

    def test_zero_income_edge_case(self):
        payload = {
            "income": 0,
            "essential_expenses": 0,
            "non_essential_expenses": 0,
            "savings": 0
        }
        resp = client.post("/api/budget/calculate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["remaining_balance"], 0.0)
        self.assertEqual(data["status"], "Zero Income")

    def test_negative_input_rejected_by_api(self):
        payload = {"income": -1000}
        resp = client.post("/api/budget/calculate", json=payload)
        self.assertEqual(resp.status_code, 422)


class TestSystemEndpoints(unittest.TestCase):
    """Tests static serving, health, and info endpoints."""

    def test_health_check_returns_200_and_valid_schema(self):
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "FinMitra")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("ai_status", data)
        self.assertIn("model", data)

    def test_api_info_endpoint(self):
        resp = client.get("/api/info")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["name"], "FinMitra")
        self.assertIn("SDG 1", data["track"])
        self.assertIn("endpoints", data)

    def test_static_index_html_serves_ok(self):
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("FINMITRA", resp.text)
        self.assertIn("menu-toggle", resp.text)
        self.assertIn("nav-menu", resp.text)

    def test_static_assets_serve(self):
        for path in ["/css/style.css", "/js/app.js", "/js/chat.js", "/js/budget.js"]:
            resp = client.get(path)
            self.assertEqual(resp.status_code, 200, f"Failed to serve {path}")


class TestSystemPromptInvariants(unittest.TestCase):
    """Verifies that the system prompt adheres to SDG 1 and competition constraints."""

    def test_prompt_contains_sdg1_focus(self):
        self.assertTrue("SDG 1" in SYSTEM_PROMPT or "No Poverty" in SYSTEM_PROMPT)

    def test_prompt_avoids_mandatory_50_30_20(self):
        self.assertIn("50/30/20", SYSTEM_PROMPT)
        self.assertTrue("NEVER enforce" in SYSTEM_PROMPT or "optional" in SYSTEM_PROMPT.lower())

    def test_prompt_contains_inr_currency_default(self):
        self.assertIn("₹", SYSTEM_PROMPT)

    def test_prompt_security_defenses(self):
        self.assertTrue("sensitive" in SYSTEM_PROMPT.lower())
        self.assertTrue("bank" in SYSTEM_PROMPT.lower())


if __name__ == "__main__":
    unittest.main()
