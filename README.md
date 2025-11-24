
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

**Server : http://127.0.0.1:8000**  
**API    : http://127.0.0.1:8000/docs**
