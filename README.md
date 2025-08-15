
# AssistIQBot

A Retrieval‑Augmented Generation (RAG) chatbot for IT support teams. AssistIQBot indexes your internal support knowledge base (docs, wikis) into a local FAISS vector store and uses LLMs to answer user questions with accurate, source‑grounded responses.

---

## Key Features

* **RAG over your KB**: Ingest Markdown, PDF, HTML, Confluence/MediaWiki exports, and plain text.
* **Local FAISS**: Vectors stored locally (no managed vector DB required).
* **Citations**: Answers include source snippets/links for traceability.
* **Content filters**: File allow/deny lists, path scoping, metadata tagging.
* **Incremental re‑ingestion**: Only reindex changed files.
* **Embeddings choice**: OpenAI or local (Sentence‑Transformers) models.
* **Pluggable UI**: Minimal built‑in chat UI (optional) + simple REST API for any frontend.
* **Guardrails**: PII redaction, hallucination‑aware prompts, and “I don’t know” handling.

---

## 🧱 Architecture

1. **Ingestion Pipeline**

   * Load files → chunk → embed → upsert to **FAISS**.
2. **Retriever**

   * Hybrid lexical + vector (optional) → top‑k passages with metadata.
3. **Orchestrator (RAG)**

   * Compose a grounded prompt → call LLM → generate answer with citations.
4. **Serving Layer**

   * **FastAPI** endpoints (Python) for `/ask`, `/ingest`, `/health`.

5. **Frontend**

   * Simple web chat (Bootstrap) calling the REST API.



## Minimum Requirements for the Project

### LLM Models
- **Groq** (Free)
- **OpenAI** (Paid)
- **Gemini** (15 Days Free Access)
- **Claude** (Paid)
- **Hugging Face** (Free)
- **Ollama** (Local Setup)

### Embedding Models
- **OpenAI**
- **Hugging Face**
- **Gemini**

### Vector Databases
- **In-Memory**
- **On-Disk**
- **Cloud-Based**

## API Keys

### GROQ API Key
- [Get your API Key](https://console.groq.com/keys)  
- [Groq Documentation](https://console.groq.com/docs/overview)

### Gemini API Key
- [Get your API Key](https://aistudio.google.com/apikey)  
- [Gemini Documentation](https://ai.google.dev/gemini-api/docs/models)



## Python Commands

# Create Virtual Environment
- -m: This flag indicates that the next argument should be treated as a Python module name, and that module should be executed as a script.
- venv: This is the name of the built-in Python module that is used for creating virtual environments. 

python create -m venv .env

# Install dependencies from requirements.txt
pip install -r requirements.txt
