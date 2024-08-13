from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str

class LanguageRequest(BaseModel):
    text: str
    lang: str