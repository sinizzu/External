from fastapi import APIRouter, Depends, HTTPException, Body
from app.services import paper_service
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
    return paper_service.searchKeyword(searchword)