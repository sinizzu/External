from fastapi import APIRouter, Depends, HTTPException, Body
from app.services import paper_service, keyword_extract_service
from app.schemas import paper as paper_schema


router = APIRouter()

@router.get("/getMeta", response_model=paper_schema.MetaResponse)
async def get_meta(searchword: str):
    return paper_service.getMeta(searchword)

@router.post("/saveWea", response_model=paper_schema.SaveWeaResponse)
async def save_wea(meta_response: paper_schema.MetaResponse):
    return await paper_service.saveWea(meta_response)

@router.get("/searchKeyword")
async def search_keyword(searchword: str):
    return await paper_service.searchKeyword(searchword)

@router.get('/getColl')
async def getColl(searchword: str):
    return await paper_service.getColl(searchword)    

@router.get('/dbpiasearch')
async def get_trend_keywords():
    return await paper_service.get_trend_keywords()

@router.get('/searchPopularkeyord')
async def search_popular_keyword():
    return await paper_service.search_popular_keyword()

@router.get('/keywordExtract')
async def keyword_extraction():
    return keyword_extract_service.keyword_extraction()