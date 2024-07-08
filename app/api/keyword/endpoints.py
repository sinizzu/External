from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from app.services.web_search import search_query
from app.services import keyword_extract_service
from fastapi import APIRouter
from app.schemas.web_search import SearchRequest, SearchResponse
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

@router.post("/searchWeb", response_model=SearchResponse)
async def search(request: SearchRequest):
    logger.info(f"Request: {request}")
    results = await search_query(request.text)
    logger.info(f"Results: {results}")
    return SearchResponse(result=results)

@router.get('/wikiSearch')
async def wiki_search(keyword: str):
    return keyword_extract_service.wiki_search(keyword)