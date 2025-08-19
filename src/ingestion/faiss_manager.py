from __future__ import annotations
import sys
import json
import uuid
import hashlib
from pathlib import Path
from typing import Iterable, List, Optional, Dict, Any

import fitz  # PyMuPDF
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import AssistIQAppException

from utils.file_io import _session_id, save_uploaded_files
from utils.document_helper import load_documents, concat_for_analysis, concat_for_comparison


# FAISS Manager (load-or-create)
class FaissManager:
    """FAISS Manager Class
    """
    def __init__(self, index_dir: Path, model_loader: Optional[ModelLoader] = None):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta: Dict[str, Any] = {"rows": {}}
        
        if self.meta_path.exists():
            try:
                self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {"rows": {}}
            except Exception:
                self._meta = {"rows": {}}
        

        self.model_loader = model_loader or ModelLoader()
        self.emb = self.model_loader.load_embeddings()
        self.vs: Optional[FAISS] = None
        
    def _exists(self)-> bool:
        return (self.index_dir / "index.faiss").exists() and (self.index_dir / "index.pkl").exists()
    
    @staticmethod
    def _fingerprint(text: str, md: Dict[str, Any]) -> str:
        src = md.get("source") or md.get("file_path")
        rid = md.get("row_id")
        if src is not None:
            return f"{src}::{'' if rid is None else rid}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def _save_meta(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")
        
        
    def add_documents(self,docs: List[Document]):
        """Add Documents to existing index if not duplicate.

        Args:
            docs (List[Document]): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        if self.vs is None:
            raise RuntimeError("Call load_or_create() before add_documents_idempotent().")
        
        new_docs: List[Document] = []
        
        # Create unique key for each document (pdf, txt, docs etc.) and add to metadata. 
        # If key exists continue else add new document
        # This will avoid ingesting duplicate data.
        # Iterate through chunks / documents and create unique key
        for d in docs:
            key = self._fingerprint(d.page_content, d.metadata or {})
            if key in self._meta["rows"]:
                continue
            self._meta["rows"][key] = True
            new_docs.append(d)
        
        # Add new documents to index and save
        if new_docs:
            self.vs.add_documents(new_docs)
            self.vs.save_local(str(self.index_dir))
            self._save_meta()
        return len(new_docs)
    
    def load_or_create(self, texts:Optional[List[str]]=None, metadatas: Optional[List[dict]] = None):
        """Load existing index or create new one if not exists.

        Args:
            texts (Optional[List[str]], optional): _description_. Defaults to None.
            metadatas (Optional[List[dict]], optional): _description_. Defaults to None.

        Raises:
            DocumentPortalException: _description_

        Returns:
            _type_: _description_
        """
        # Index exists, load and return
        if self._exists():
            self.vs = FAISS.load_local(
                str(self.index_dir),
                embeddings=self.emb,
                allow_dangerous_deserialization=True,
            )
            return self.vs
        if not texts:
            raise AssistIQAppException("No existing FAISS index and no data to create one", sys)
        
        # First time execution. Create new index
        self.vs = FAISS.from_texts(texts=texts, embedding=self.emb, metadatas=metadatas or [])
        self.vs.save_local(str(self.index_dir))
        return self.vs