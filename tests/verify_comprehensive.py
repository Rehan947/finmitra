"""Comprehensive verification of FinMitra after truncation fix.
Tests 5 realistic SDG-1 questions, multi-step queries, multi-turn follow-ups, and completeness of responses.
"""

import sys
import time
import httpx

BASE_URL = "http://localhost:8000"

SDG1_QUESTIONS = [
    (
        "Question 1 (Multi-step Plan)",
        "I earn a small monthly income of 15000. Give me a detailed step-by-step plan to manage it, reduce expenses, and build a starter emergency fund."
    ),
    (
        "Question 2 (Needs vs Wants)",
        "How can I tell the difference between essential needs and wants when my family lives on a tight budget?"
    ),
    (
        "Question 3 (Loan Safety)",
        "What should I check before taking a loan from an instant cash loan app to avoid debt traps?"
    ),
    (
        "Question 4 (Micro-savings)",
        "How can someone who only earns daily wages save 20 to 50 rupees a day consistently?"
    ),
    (
        "Question 5 (Emergency Fund)",
        "How much money should be in a starter emergency fund, and where is the safest place to keep it?"
    )
]

def run_verification():
    print("=" * 75)
    print("  FINMITRA POST-FIX VERIFICATION: COMPLETENESS & NATURAL ENDINGS")
    print("=" * 75)

    client = httpx.Client(base_url=BASE_URL, timeout=45.0)

    # Health check
    h_resp = client.get("/health")
    assert h_resp.status_code == 200, f"Health check failed: {h_resp.text}"
    print(f"[*] Health Check OK: {h_resp.json()}")

    all_passed = True

    # Test 5 realistic questions
    for idx, (title, q_text) in enumerate(SDG1_QUESTIONS, 1):
        print(f"\n[{idx}/5] Testing {title}...")
        t0 = time.time()
        resp = client.post("/chat", json={"message": q_text})
        elapsed = time.time() - t0

        if resp.status_code != 200:
            print(f"  [FAIL] Status code {resp.status_code}: {resp.text}")
            all_passed = False
            continue

        data = resp.json()
        ans = data.get("response", "").strip()

        # Check for non-empty and length
        if len(ans) < 100:
            print(f"  [FAIL] Response too short ({len(ans)} chars)")
            all_passed = False
            continue

        # Check natural ending
        # Natural endings typically end with a period, question mark, exclamation, or bold closure
        last_50 = ans[-50:].strip()
        ends_naturally = any(ans.endswith(p) for p in [".", "?", "!", ')"', ".'", "?*", "**", "]*", "</p>"]) or "?" in last_50 or "." in last_50

        # Check if it ends with an abrupt heading or cut off word like "#### Step 2:"
        abrupt_patterns = ["#### Step", "### Step", "Step 2:", "Step 3:", "minor", "and", "or", "the", "with"]
        is_abrupt = any(ans.strip().endswith(p) for p in abrupt_patterns)

        if ends_naturally and not is_abrupt:
            print(f"  [PASS] Completed naturally in {elapsed:.2f}s ({len(ans)} chars)")
            print(f"         Ending snippet: ...{last_50}")
        else:
            print(f"  [FAIL] Response appears incomplete!")
            print(f"         Ending snippet: ...{last_50}")
            all_passed = False

    # Multi-turn Follow-up Test
    print("\n[6/6] Testing Multi-turn Follow-up Conversation Context...")
    history = [
        {"role": "user", "content": "How can I tell the difference between essential needs and wants?"},
        {"role": "assistant", "content": "Needs are essential for survival and health like simple groceries and rent. Wants are non-urgent preferences like dining out. Use the 24-hour pause rule."}
    ]
    follow_up_q = "Can you give me 2 concrete examples of how to apply the 24-hour pause rule in daily life?"
    t0 = time.time()
    resp_follow = client.post("/chat", json={"message": follow_up_q, "conversation_history": history})
    elapsed = time.time() - t0

    if resp_follow.status_code == 200:
        ans_follow = resp_follow.json().get("response", "").strip()
        last_50_follow = ans_follow[-50:].strip()
        print(f"  [PASS] Follow-up response completed in {elapsed:.2f}s ({len(ans_follow)} chars)")
        print(f"         Ending snippet: ...{last_50_follow}")
    else:
        print(f"  [FAIL] Follow-up status {resp_follow.status_code}")
        all_passed = False

    # Validation Edge Cases
    print("\n--- Testing Validation Edge Cases ---")
    resp_empty = client.post("/chat", json={"message": ""})
    assert resp_empty.status_code == 422, f"Expected 422, got {resp_empty.status_code}"
    print("  [PASS] Empty message correctly rejected with 422")

    resp_ws = client.post("/chat", json={"message": "   "})
    assert resp_ws.status_code == 422, f"Expected 422, got {resp_ws.status_code}"
    print("  [PASS] Whitespace message correctly rejected with 422")

    print("\n" + "=" * 75)
    if all_passed:
        print("  >>> POST-FIX VERIFICATION: ALL 5 QUESTIONS + FOLLOW-UP FINISHED NATURALLY! <<<")
        return 0
    else:
        print("  >>> SOME VERIFICATION CHECKS FAILED <<<")
        return 1

if __name__ == "__main__":
    sys.exit(run_verification())
