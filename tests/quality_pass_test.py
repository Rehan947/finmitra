"""Focused quality pass test verifying all 6 required prompts against live FinMitra server."""

import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000"

PROMPTS = [
    (
        "Prompt A",
        "I have a limited monthly income. What practical steps can I take to manage my expenses and build a small emergency fund?",
        None
    ),
    (
        "Prompt B",
        "My income is ₹15000 per month and my essential expenses are ₹11000. How can I start saving?",
        None
    ),
    (
        "Prompt C",
        "Should I follow the 50-30-20 rule if I have a very low income?",
        None
    ),
    (
        "Prompt D",
        "How can I reduce unnecessary expenses?",
        None
    ),
    (
        "Prompt E",
        "What is an emergency fund?",
        None
    ),
    (
        "Prompt F (Follow-up)",
        "My income changes every month. What should I do?",
        [
            {"role": "user", "content": "What is an emergency fund?"},
            {"role": "assistant", "content": "An emergency fund is money kept strictly for urgent, unexpected expenses like sudden medical bills. Aim for a small starter goal like ₹1,000 first."}
        ]
    )
]

def run_quality_pass():
    print("=" * 80)
    print("  FINMITRA FOCUSED QUALITY PASS — 6 PROMPTS VERIFICATION")
    print("=" * 80)

    client = httpx.Client(base_url=BASE_URL, timeout=45.0)

    # Health check
    h = client.get("/health")
    assert h.status_code == 200, "Health check failed"
    print(f"[*] Health Check OK: {h.json()}\n")

    results = []

    for idx, (label, query, history) in enumerate(PROMPTS, 1):
        print("-" * 80)
        print(f"[{idx}/6] {label}: \"{query}\"")
        payload = {"message": query}
        if history:
            payload["conversation_history"] = history

        # Add pause between requests to respect rate limits
        if idx > 1:
            time.sleep(3)

        t0 = time.time()
        resp = client.post("/chat", json=payload)
        elapsed = time.time() - t0

        if resp.status_code != 200:
            print(f"  [FAIL] HTTP {resp.status_code}: {resp.text}")
            results.append((label, False, "HTTP failure"))
            continue

        data = resp.json()
        text = data.get("response", "").strip()
        word_count = len(text.split())

        # Quality criteria
        # 1. Complete response (ends naturally with punctuation)
        last_chars = text[-40:].strip()
        ends_naturally = any(text.endswith(p) for p in [".", "?", "!", ')"', ".'", "?*", "**", "]*"]) or "?" in last_chars or "." in last_chars
        is_abrupt = any(text.strip().endswith(p) for p in ["#### Step", "### Step", "Step 2:", "Step 3:", "minor", "and", "or", "the", "with"])
        complete = ends_naturally and not is_abrupt

        # 2. Indian context check (prefer ₹, no unnecessary $)
        has_rupee = "₹" in text or "rupee" in text.lower()
        has_dollar = "$" in text

        # 3. 50/30/20 non-mandatory check for Prompt C
        rule_c_passed = True
        if "50-30-20" in query:
            rule_c_passed = any(kw in text.lower() for kw in ["not mandatory", "not realistic", "exceed 50%", "more than 50%", "flexible", "guideline, not a rule", "essential expenses often take", "textbook", "optional"])

        # 4. Word count check (typically 150-450 words)
        reasonable_length = 120 <= word_count <= 500

        print(f"  Latency: {elapsed:.2f}s | Words: {word_count} | Chars: {len(text)}")
        print(f"  Complete ending: {complete} (Ending: ...{last_chars})")
        print(f"  Indian currency context (₹): {has_rupee} | Dollar ($) present: {has_dollar}")
        if "50-30-20" in query:
            print(f"  50/30/20 treated as non-mandatory: {rule_c_passed}")

        print(f"\n  [Response Preview]:\n  {text[:320]}...\n")

        all_checks = complete and not has_dollar and rule_c_passed and reasonable_length
        results.append((label, all_checks, f"words: {word_count}, latency: {elapsed:.2f}s"))

    print("=" * 80)
    print("  SUMMARY OF QUALITY PASS:")
    print("=" * 80)
    passed_count = sum(1 for _, ok, _ in results if ok)
    for label, ok, detail in results:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} {label} ({detail})")

    print(f"\n  Result: {passed_count} / {len(results)} passed ({passed_count/len(results)*100:.1f}%)")
    return 0 if passed_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(run_quality_pass())
