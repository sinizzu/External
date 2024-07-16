from pydantic import BaseModel

class DivideChunkRequest(BaseModel):
    pdfId: str
    fullText: str

class UseChatbotRequest(BaseModel):
    pdfId: str
    query: str
