from fastapi import FastAPI, Form, Query
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
# 첫번째줄에 fastapi의 Query를 선언해주어서 api에서 입력받을때 값 입력받을수 있음
# 예시로 localhost:3000/search/wikiSearch?keyword=BERT 이런식으로 던져짐
async def wiki_search(keyword: str, lang: str):
    return keyword_extract_service.wiki_search(keyword, lang)