# 📚 Hellobooks AI — Accounting Assistant

An AI-powered bookkeeping assistant built with **RAG (Retrieval-Augmented Generation)**, serving accurate, context-grounded answers to accounting questions.

## 🏗️ Architecture

```
User Question
     │
     ▼
Flask Backend (/api/ask)
     │
     ▼
HuggingFace Embeddings  ──►  FAISS Vector Store
     │                            │
     │                    Retrieve top-4 chunks
     │                            │
     ▼                            ▼
LangChain RetrievalQA  ◄── Context + Question
     │
     ▼
Ollama (llama3.2)  ──►  Generated Answer
     │
     ▼
Flask Response (JSON)  ──►  Frontend UI
```

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML + CSS + Vanilla JS (Flask-served) |
| Backend | Python + Flask |
| LLM Runtime | Ollama (llama3.2) |
| AI Framework | LangChain |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector DB | FAISS |
| Architecture | RAG |

## 📁 Project Structure

```
hellobooks/
├── knowledge_base/          # Accounting topic documents
│   ├── bookkeeping.md
│   ├── invoices.md
│   ├── profit_and_loss.md
│   ├── balance_sheet.md
│   ├── cash_flow.md
│   ├── accounts_payable.md
│   ├── accounts_receivable.md
│   └── tax_basics.md
├── backend/
│   ├── app.py              # Flask API
│   ├── rag_engine.py       # RAG pipeline (embeddings + FAISS + Ollama)
│   ├── requirements.txt
│   └── faiss_index/        # Auto-generated on first run
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- At least one Ollama model pulled

### Step 1: Install Ollama & pull a model
```bash
# Install Ollama from https://ollama.com
ollama pull llama3.2
# Or use: ollama pull mistral  (if llama3.2 unavailable)
```

### Step 2: Clone & install dependencies
```bash
git clone <your-repo-url>
cd hellobooks
pip install -r backend/requirements.txt
```

### Step 3: Run the server
```bash
python backend/app.py
```
Open your browser at **http://localhost:5000**

> The FAISS index is built automatically on first run from the knowledge base files.

### Step 4 (Optional): Change the model
Edit `backend/rag_engine.py`:
```python
OLLAMA_MODEL = "llama3.2"  # Change to your model, e.g. "mistral", "phi3"
```

---

## 🐳 Docker Setup

```bash
# Make sure Ollama is running on host machine first
ollama serve

# Build and run
docker-compose up --build
```

The app will be available at **http://localhost:5000**

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Web UI |
| POST | `/api/ask` | Ask a question |
| POST | `/api/rebuild` | Rebuild FAISS index |
| GET | `/api/health` | Health check |

### Example API call
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is double-entry bookkeeping?"}'
```

### Response
```json
{
  "answer": "Double-entry bookkeeping is a system where every transaction...",
  "sources": ["Bookkeeping", "Accounts Payable"]
}
```

---

## 📖 Knowledge Base Topics

| File | Topics Covered |
|---|---|
| `bookkeeping.md` | General ledger, chart of accounts, double-entry |
| `invoices.md` | Invoice types, components, AR |
| `profit_and_loss.md` | Revenue, COGS, gross/net profit |
| `balance_sheet.md` | Assets, liabilities, equity, ratios |
| `cash_flow.md` | Operating/investing/financing, FCF |
| `accounts_payable.md` | AP process, DPO, payment terms |
| `accounts_receivable.md` | AR aging, DSO, bad debt |
| `tax_basics.md` | Business taxes, deductions, depreciation |

To add topics: create a new `.md` file in `knowledge_base/`, then call `POST /api/rebuild`.

---

## 🔧 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `PORT` | `5000` | Flask server port |
| `FLASK_DEBUG` | `false` | Enable debug mode |
