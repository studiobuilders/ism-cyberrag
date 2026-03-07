# Inference Setup Guide

This folder contains setup scripts and instructions for configuring the following services:

| Service | Description |
|---|---|
| [Groq API](#1-groq-api) | Cloud inference for fast LLM access |
| [Ollama](#2-ollama) | Local LLM environment |
| [ClearML](#3-clearml) | Experiment tracking workspace |

---

## Prerequisites
- Unix-based OS (Linux/macOS) or WSL on Windows

We need to use uv here since uv is really good at speed of installation of packages.
## UV installation (For more info, refer [here](https://github.com/astral-sh/uv))

Setup

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv venv --python 3.12.0
source .venv/bin/activate
```
Your local environment is now activated!

Install shared Python dependencies:

```bash
pip install -r requirements.txt
```
---

## 1. Groq API

Groq API is used to access cloud deployed models. It has a free tier of certain limitations. You can check the Groq Free tier limits [here](https://console.groq.com/docs/rate-limits)

**Script:** `scripts/setup_groq.sh`

### Steps

1. Sign up at [https://console.groq.com](https://console.groq.com)
2. Generate an API key from the Console → API Keys section
3. Paste it somewhere secure on your local machine as you cannot be able to retrieve it later
4. Run the setup script:

```bash
chmod +x scripts/setup_groq.sh
./scripts/setup_groq.sh
```

5. When prompted, paste your Groq API key. It will be saved to `.env`.

### Verify

```bash
python helpers/verify_groq.py
```

---

## 2. Ollama

Local inference engine to run inference on locally hosted models which consumes a bit of compute resources locally.

**Script:** `scripts/setup_ollama.sh`

### Steps

Choose which model you wish to run with ollama. (by default its `llama3.1:8b`)
Run the setup script (installs Ollama and pulls the selected default model):

```bash
chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh
```

This will:
- Install the Ollama CLI
- Start the Ollama service
- Pull the default model (`llama3.2`)

### Verify

```bash
python helpers/verify_ollama.py
```

or

Test it directly on the CLI

```bash
ollama run llama3.1 "Hello, world!"
```

### Other Available Models

| Model | Command |
|---|---|
| Llama 3.2 (3B) | `ollama pull llama3.2` |
| Mistral 7B | `ollama pull mistral` |
| Phi-3 Mini | `ollama pull phi3` |
| Gemma 2 (2B) | `ollama pull gemma2:2b` |


---

## 3. ClearML

Cloud based experiment tracking platform used to log and version your metrics, experiments and datasets.

**Script:** `scripts/setup_clearml.sh`

### Steps

1. Sign up at [https://app.clear.ml](https://app.clear.ml) (or use a self-hosted server)
2. Go to **Settings → Workspace → Create new credentials**
3. Copy your credentials (access key, secret key)
4. Paste it somewhere secure on your local machine as you cannot be able to retrieve it later
5. Run the setup script:

```bash
chmod +x scripts/setup_clearml.sh
./scripts/setup_clearml.sh
```

6. Paste your credentials when prompted — they will be saved to `~/clearml.conf`

### Verify

```bash
python helpers/verify_clearml.py
```

---

## Environment Variables

All API keys are stored in a `.env` file (gitignored). 

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `CLEARML_API_ACCESS_KEY` | ClearML access key |
| `CLEARML_API_SECRET_KEY` | ClearML secret key |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `GROQ_API_KEY not set` | Re-run `setup_groq.sh` or manually add key to `.env` |
| `Ollama: connection refused` | Run `ollama serve` in a separate terminal |
| `ClearML auth failed` | Re-run `clearml-init` or check `~/clearml.conf` |
| Permission denied on scripts | Run `chmod +x scripts/*.sh` |
