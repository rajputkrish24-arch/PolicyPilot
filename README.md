# PolicyPilot - AI-Powered Government Scheme Discovery Platform

An AI-powered web platform that helps citizens discover government welfare schemes they are eligible for. Built with **100% free and open-source tools**.

## Architecture Flow

```
Citizen Profile (React Frontend)
        │
        ▼
FastAPI Backend (/analyze endpoint)
        │
        ├──────────────────────┐
        ▼                      ▼
FAISS Vector Store      Eligibility Engine
(Retrieves relevant     (Rule-based + LLM
 scheme chunks)          matching)
        │                      │
        └──────────┬───────────┘
                   ▼
          Conflict Detector
                   │
                   ▼
          Results → Frontend Dashboard
```

## Data Pipeline

```
Government Websites / PDFs
        │
        ▼
Scraper Module (requests + BeautifulSoup)
        │
        ▼
PDF Parser Module (PyMuPDF)
        │
        ▼
Storage Module (JSON files)
        │
        ▼
Chunker Module (200-word chunks)
        │
        ▼
Embedder Module (all-MiniLM-L6-v2)
        │
        ▼
FAISS Vector Store
        │
        ▼
Retriever Module (similarity search)
```

## Tech Stack (All Free & Open-Source)

| Layer | Tool | Why |
|-------|------|-----|
| Frontend | React.js + Tailwind CSS | Popular, free, component-based |
| HTTP Client | Axios | Simple API calls from React |
| Backend | FastAPI (Python) | Fast, async, auto-docs |
| Scraping | requests + BeautifulSoup | Free, easy HTML parsing |
| PDF Parsing | PyMuPDF (fitz) | Free, fast PDF text extraction |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free local embeddings |
| Vector Store | FAISS | Free, local similarity search |
| Local LLM | Ollama + Mistral | Free local inference |
| Storage | JSON + FAISS index | No database needed |
| Frontend Deploy | Vercel | Free tier |
| Backend Deploy | Render | Free tier |

## Project Structure

```
/PolicyPilot
├── /backend                 # FastAPI server
│   ├── main.py             # App entry point
│   ├── requirements.txt    # Python dependencies
│   ├── /routes
│   │   └── analyze.py      # API route handlers
│   └── /services
│       ├── eligibility.py  # Eligibility logic
│       └── conflict.py     # Conflict detection
├── /scraper                 # Data collection
│   ├── scraper.py          # Web scraper
│   ├── pdf_parser.py       # PDF text extractor
│   └── storage.py          # JSON storage
├── /rag                     # RAG pipeline
│   ├── chunker.py          # Text chunking
│   ├── embedder.py         # Embedding generation
│   ├── vector_store.py     # FAISS operations
│   └── retriever.py        # Similarity search
├── /data                    # Stored data
│   ├── /schemes            # Scheme JSON files
│   ├── /pdfs               # Downloaded PDFs
│   └── /faiss              # FAISS index files
├── /frontend                # React app
│   ├── package.json
│   ├── tailwind.config.js
│   ├── /src
│   │   ├── App.jsx
│   │   ├── /components
│   │   │   ├── Navbar.jsx
│   │   │   ├── EligibilityForm.jsx
│   │   │   ├── SchemeCard.jsx
│   │   │   └── ConflictAlert.jsx
│   │   ├── /pages
│   │   │   ├── Home.jsx
│   │   │   ├── Analyze.jsx
│   │   │   └── Results.jsx
│   │   └── /services
│   │       └── api.js
│   └── /public
│       └── index.html
└── README.md
```

## Setup Instructions

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Ollama (Local LLM)
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
ollama serve
```

### Build the RAG Index
```bash
cd scraper
python scraper.py      # Scrape scheme data
python pdf_parser.py   # Parse PDFs
cd ../rag
python chunker.py      # Chunk text
python embedder.py     # Generate embeddings
python vector_store.py # Build FAISS index
```
