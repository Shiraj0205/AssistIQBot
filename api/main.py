import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


app = FastAPI(title="Assist IQ Bot API", version="1.0")

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"], 
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"])

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
async def build_document_index() -> Any :
    try:
        return {"message": "Document indexing started."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"Document indexing failed. ": str(e)})


@app.post("/chat/query")
async def chat_query() -> Any :
    try:
        return {"message": "Chat query processed."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"Chat query failed. ": str(e)})


# To execute fast API
# uvicorn api.main:app --reload
# uvicorn api.main:app --host 0.0.0.0 --port 8083 --reload
# uvicorn api.main:app --port 8083 --reload