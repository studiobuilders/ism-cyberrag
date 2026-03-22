# LLM Configuration Guide

All LLM settings are controlled via the **`.env`** file in the project root.
There are **two independent LLM configurations**:

| Purpose | Provider Variable | Model Variable |
|---|---|---|
| **Main LLM** (answering questions) | `LLM_PROVIDER` | `LLM_MODEL_NAME` |
| **Evaluation LLM** (RAGAS scoring) | `EVAL_LLM_PROVIDER` | `EVAL_LLM_MODEL` |

---

## Provider Options

| Provider | Value | Description |
|---|---|---|
| **Groq** (cloud) | `groq` | Uses Groq cloud API. Requires `GROQ_API_KEY` in `.env`. |
| **Ollama Local** | `ollama` | Uses local Ollama at `http://localhost:11434`. Requires Ollama running locally. |
| **Ollama Cloud** | `ollama` | Uses remote Ollama. Set `OLLAMA_BASE_URL` to the remote server URL. |

---

## Example Scenarios

### Main LLM: Groq Llama (default)
```env
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.1-8b-instant
```

### Main LLM: Ollama Local Llama
```env
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama3.1:8b
```

### Eval: Ollama Local Devstral
```env
EVAL_LLM_PROVIDER=ollama
EVAL_LLM_MODEL=devstral:latest
```

### Eval: Ollama Local Qwen
```env
EVAL_LLM_PROVIDER=ollama
EVAL_LLM_MODEL=qwen2.5:7b
```

### Eval: Ollama Cloud GPT-OSS
```env
EVAL_LLM_PROVIDER=ollama
EVAL_LLM_MODEL=gpt4all
OLLAMA_BASE_URL=https://your-remote-ollama-server.com
```

### Eval: Groq Cloud Llama
```env
EVAL_LLM_PROVIDER=groq
EVAL_LLM_MODEL=llama-3.1-8b-instant
```

---

## How It Works

1. **`.env`** is the **single source of truth** — change values there.
2. `src/config.py` reads from `.env` using `os.getenv()`. The second argument is only a fallback default if the variable is missing.
3. `src/llm.py` uses `LLM_PROVIDER` + `LLM_MODEL_NAME` for answer generation.
4. `src/evaluation.py` uses `EVAL_LLM_PROVIDER` + `EVAL_LLM_MODEL` for RAGAS scoring.

---

## Quick Setup for Ollama Local Models

```bash
# Pull models you want to use
ollama pull llama3.1:8b
ollama pull mistral:latest
ollama pull qwen2.5:7b
ollama pull devstral:latest

# Verify they're available
ollama list
```

Then update `.env` with the model name exactly as shown by `ollama list`.
