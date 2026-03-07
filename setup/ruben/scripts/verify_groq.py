"""
verify_groq.py — Verify Groq API access is working correctly.
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()


def verify():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("✗ GROQ_API_KEY is not set. Run scripts/setup_groq.sh first.")
        sys.exit(1)

    print(f"  API key found: {api_key[:8]}{'*' * (len(api_key) - 8)}")

    

    print("  Sending test request to Groq API...")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Reply with exactly: GROQ_OK"}],
        max_tokens=10,
    )

    reply = response.choices[0].message.content.strip()
    print(f"  Response: {reply}")

    if "GROQ_OK" in reply:
        print("\n✓ Groq API is working correctly!\n")
    else:
        print("\n⚠ Groq responded but returned unexpected content. Check manually.\n")


if __name__ == "__main__":
    print("\n── Groq API Verification ──────────────────────")
    
    try:
        verify()
    except Exception as e:
        print(f"\n✗ Groq verification failed: {e}\n")
        sys.exit(1)
