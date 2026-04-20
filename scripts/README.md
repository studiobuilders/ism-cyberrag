# Scripts helpers

## Ollama setup

First we would need to create a uv environment by installing uv from [here](https://github.com/astral-sh/uv)
Also modify the model required in the `DEFAULT_MODEL` variable provided

```bash
uv venv # For activating the environment to run pip installations
source .venv/bin/activate
./scripts/setup_ollama.sh
```

This should open up an interactive chat based environment. Close it if you do not want to access the chat-interface.

For uninstalling ollama modules, run
```bash
./scripts/ollama_uninstall.sh
```
