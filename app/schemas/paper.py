from pydantic import BaseModel
from typing import List

class Paper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    published: str
    direct_link: str
    pdf_link: str
    category: str

class MetaResponse(BaseModel):
    resultCode: int
    data: List[Paper]

class SaveWeaResponse(BaseModel):
    resultCode: int
    data: dict
