from fastapi import APIRouter
from app.services import chatbot_service
from app.schemas import chatbot as chatbot_schema

router = APIRouter()

@router.post("/divideChunk")
async def divideChunk(request: chatbot_schema.DivideChunkRequest):
    return await chatbot_service.divideChunk(request)


@router.post("/useChatbot")
async def useChatbot(request: chatbot_schema.UseChatbotRequest):
    return await chatbot_service.useChatbot(request)