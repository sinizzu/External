from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    text: str

class SearchResult(BaseModel):
    title: str
    link: str

class SearchResponse(BaseModel):
    result: List[SearchResult]