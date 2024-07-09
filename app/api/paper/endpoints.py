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

@router.get('/searchDBpia')
async def trendKeywords():
    return await paper_service.trendKeywords()

@router.get('/searchPopularkeyord')
async def searchPopularKeyword():
    return await paper_service.searchPopularKeyword()

@router.get('/keywordExtract')
async def keyword_extraction(text: str):
    return keyword_extract_service.keyword_extraction(text)

