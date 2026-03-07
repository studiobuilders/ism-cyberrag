"""
verify_ollama.py — Verify Ollama is running and a model is available.
"""

import sys


def verify():
    try:
        import ollama
    except ImportError:
        print("✗ ollama package not installed. Run: pip install ollama")
        sys.exit(1)

    print("  Checking Ollama service...")
    try:
        models = ollama.list()
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Is Ollama running? Try: ollama serve")
        sys.exit(1)

    model_names = [m.model for m in models.models]
    if not model_names:
        print("✗ No models found. Run: ollama pull llama3.2")
        sys.exit(1)

    print(f"  Available models: {', '.join(model_names)}")

    # Use first available model for a quick test
    test_model = model_names[0]
    print(f"  Sending test prompt to '{test_model}'...")

    response = ollama.chat(
        model=test_model,
        messages=[{"role": "user", "content": "Reply with exactly: OLLAMA_OK"}],
    )
    reply = response.message.content.strip()
    print(f"  Response: {reply[:80]}")
    print(f"\n✓ Ollama is working! Model '{test_model}' is responding.\n")


if __name__ == "__main__":
    print("\n── Ollama Verification ────────────────────────")
    try:
        verify()
    except SystemExit:
        raise
    except Exception as e:
        print(f"\n✗ Ollama verification failed: {e}\n")
        sys.exit(1)
