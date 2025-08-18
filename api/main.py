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


# To execute fast API
# uvicorn api.main:app --reload
# uvicorn api.main:app --host 0.0.0.0 --port 8083 --reload
# uvicorn api.main:app --port 8083 --reload