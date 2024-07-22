from pydantic import BaseModel

class DivideChunkRequest(BaseModel):
    pdfId: str
    language: str
    fullText: str

class UseChatbotRequest(BaseModel):
    pdfId: str
    language: str
    query: str
