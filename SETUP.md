
## ⚡ Quick Start 

### 1. Clone & Setup Environment
```
python -m venv .venv
```
```
\.venv\Scripts\activate
```
```
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```env
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_ENV=
```


### 3. Initialize Knowledge Base
```
python app\data\ingest_laws.py

```

### 4. Start Server
```
uvicorn app.main:app --reload 
```

✅ **Server runs at: http://127.0.0.1:8000**
📖 **API Docs: http://127.0.0.1:8000/docs**

```

## Project Structure

```
Backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config/config.py     # Settings & AI system prompt
│   ├── services/ai_service.py  # Core AI logic
│   ├── api/ai_endpoint.py   # REST API routes
│   ├── models/model.py      # Database models
│   ├── schemas/schema.py    # Pydantic schemas
│   ├── utils/               # Document processing utilities
│   └── data/
│       ├── laws/            # Bangladesh tax law documents (.txt)
│       ├── Main_Data.pdf    # Main tax law PDF
│       ├── ingest_laws.py   # Knowledge base ingestion
│       └── simple_ingest.py # Local testing
├── requirements.txt         # Python dependencies
├── .env.template           # Environment variables template
└── README.md               # This file
```