"""
Built upon Python type hints, are primarily used for data validation, parsing, 
and serialization in Python applications
"""
from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class Metadata(BaseModel):
    """
        Document Metadata Model
    """
    Summary: List[str] = Field(default_factory=list, description="Summary of the document")
    Title: str
    Author: str
    DateCreated: str
    LastModifiedDate: str
    Publisher: str
    Language: str
    PageCount: Union[int, str]
    Sentimenttone: str

class ChangeFormat(BaseModel):
    """
        Document Comparison Response Model
    """
    page: str
    changes: str

class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass

class PromptType(str, Enum):
    """
    Prompt Type
    """
    CONTEXTUALIZE_QUESTION = "contextualize_question"
    CONTEXT_QA = "context_qa"