from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from app.services import paper_service, keyword_extract_service
from app.schemas import paper as paper_schema
from app.db import connect_s3

router = APIRouter()

@router.get("/searchMeta", response_model=paper_schema.MetaResponse)
async def get_meta(searchword: str):
    return paper_service.getMeta(searchword)

@router.post("/saveWea", response_model=paper_schema.SaveWeaResponse)
async def save_wea(meta_response: paper_schema.MetaResponse):
    return await paper_service.saveWea(meta_response)

@router.get("/searchKeyword")
async def search_keyword(searchword: str):
    response = paper_service.searchKeyword(searchword)
    if response.get("resultCode") == 200:
        return response
    else:
        res = paper_service.getMeta(searchword)
        res = paper_schema.MetaResponse(**res)
        response = await paper_service.saveWea(res)
        response = paper_service.searchKeyword(searchword)
        return response 

@router.get('/searchColl')
async def getColl(searchword: str):
    response = await paper_service.getColl(searchword)
    if response.get("resultCode") == 200:
        return response
    else:
        keywords = paper_service.extract_keywords(searchword)
        for keyword in keywords:
            res= paper_service.getMeta(keyword)
            res = paper_schema.MetaResponse(**res)
            response = await paper_service.saveWea(res)
        response = await paper_service.getColl(searchword)
        return response    

@router.get('/searchDBpia')
async def trendKeywords():
    return await paper_service.trendKeywords()

@router.get('/searchPopularkeyord')
async def searchPopularKeyword():
    return await paper_service.searchPopularKeyword()

@router.get('/keywordExtract')
async def keyword_extraction():
    return keyword_extract_service.keyword_extraction()

@router.post("/saveToS3")
async def save_to_s3(file: UploadFile = File(...)):
    return await connect_s3.uploadFileToS3(file)
@router.get("/listPdfs")
async def list_pdfs():
    return await connect_s3.listPdfs()

@router.get("/searchObjectId")
async def search_keyword(searchLink: str):
    return paper_service.getObjectId(searchLink)