# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install git (required for some HF/Torch dependencies) and build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
# We use a constrained PyTorch install to save bandwidth and image size on CPU-only HF Spaces
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# We copy src, app, database, etc.
COPY src/ ./src/
COPY app/ ./app/
COPY .env.example ./.env

# Pre-download Emdedding and Reranking HF Models inside the build step 
# to ensure the Space starts instantly without delaying initialization.
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
               SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True); \
               CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# Set environment variables (Values MUST be passed via Hugging Face Space Secrets)
# SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, GROQ_API_KEY
ENV PORT=7860
EXPOSE 7860

# Command to run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
