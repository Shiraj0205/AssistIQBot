import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils.document_helper import FastAPIFileAdapter
from src.ingestion.data_ingestor import ChatIngestor
from src.data_retrieval.retrieval import ConversationalRAG

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")

app = FastAPI(title="Assist IQ Bot API", version="1.0")

app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"], 
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"])


BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
def health() -> Dict[str, str]:
    """Api Health Endpoint

    Returns:
        Dict[str, str]: _description_
    """
    return { "status": "ok", "service": "AI Assist IQ Bot" }


@app.post("/admin/document/index")
async def build_document_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
    ) -> Any:
    try:
         # Wrap Uploaded Files
         wrapped = [FastAPIFileAdapter(f) for f in files]

         # Initialize ChatIngestor
         ci = ChatIngestor(
              temp_base=UPLOAD_BASE,
              faiss_base=FAISS_BASE,
              use_session_dirs=use_session_dirs,
              session_id=session_id or None
            )
         
         # Save Uploaded Files
         ci.built_retriver(
             wrapped,
             chunk_size=chunk_size,
             chunk_overlap=chunk_overlap, 
             k=k
             )
         
         return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"Document indexing failed. ": str(e)})


@app.post("/chat/query")
async def process_chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5)
    ) -> Any :
    """Process User Chat Query

    Args:
        question (str, optional): _description_. Defaults to Form(...).
        session_id (Optional[str], optional): _description_. Defaults to Form(None).
        use_session_dirs (bool, optional): _description_. Defaults to Form(True).
        k (int, optional): _description_. Defaults to Form(5).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        Any: _description_
    """
    try:
        # Validate Inputs
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400,
                                detail="session_id is required when use_session_dirs=True")

        # Prepare FAISS Index Path
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore

        # Check if FAISS Index Directory Exists
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, 
                                detail=f"FAISS index not found at: {index_dir}")

        # Initialize LCEL-style RAG pipeline
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=FAISS_INDEX_NAME)  # build retriever + chain
        response = rag.invoke(question, chat_history=[])

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}") from e


# To execute fast API
# uvicorn api.main:app --reload
# uvicorn api.main:app --host 0.0.0.0 --port 8083 --reload
# uvicorn api.main:app --port 8083 --reload