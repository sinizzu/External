from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    text: str

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: Optional[str] = "No snippet available"
    image: Optional[str] = ""

class SearchResponse(BaseModel):
    result: List[SearchResult]
