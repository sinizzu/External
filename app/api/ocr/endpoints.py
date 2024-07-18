from fastapi import APIRouter, FastAPI, HTTPException, Form, Body, UploadFile, File
import os
from fastapi.responses import JSONResponse, HTMLResponse
from google.cloud import vision
from dotenv import load_dotenv
from app.services import ocr_service
from app.services.ocr_service import pdfStreamToJpg, imageToText, downloadPdfLink
from app.db.weaviate_utils import compareId, saveToWeaviate, getTextsById, getAllSchema, deleteClass, getClassData, deleteDataByTitle
from app.services.paper_service import getObjectId
from app.db.connect_db import get_weaviate_client 
from weaviate.classes.query import Filter

client = get_weaviate_client()
pdfCollection = client.collections.get("pdf")

router = APIRouter()

load_dotenv()

@router.get('/getSchemas')
async def get_schemas():
    return getAllSchema()
@router.post('/deleteSchema')
async def delete_schema(className):
    deleteClass(className)
@router.get("/getClassData/{className}")
async def get_class_data_endpoint(className: str, maxTextLength: int = 50):
    try:
        data = getClassData(className, maxTextLength)
        if isinstance(data, str):
            raise HTTPException(status_code=400, detail=data)
        return {"resultCode": 200, "className": className, "data": data}
    except Exception as e:
        print(f"Error in /getClassData: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/deleteData")
async def deleteData(title: str):
    try:
        deleteDataByTitle("pdf", title)
        return getClassData("pdf", 50)
    except Exception as e:
        print(f"Error in /deleteData: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ocrTest")
async def uploadData(pdfId: str = Form(None), pdfUrl: str = Form(None)):
    try:
        if not pdfUrl or not pdfId:
            raise HTTPException(status_code=400, detail="Invalid input: pdfUrl or pdfId is missing")

        print(f"Received pdfUrl: {pdfUrl}, pdfId: {pdfId}")
        pdfStreamData = None
        check = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdfId),
            limit=1)
        if check.objects : 
            fullTxt = check.objects[0].properties.get("full_text")
            pdfId = check.objects[0].properties.get("pdf_id")
            
            data = {
                "pdf_id": pdfId,
                "full_text" : fullTxt
            } 
            return {"resultCode": 200, "data": data}
        else : 
            pdfLink = pdfUrl
            pdfStreamData = downloadPdfLink(pdfUrl)
            # PDF 스트림 데이터를 JPEG 이미지로 변환
            jpgImgData = pdfStreamToJpg(pdfStreamData)
            # 이미지 데이터를 텍스트로 변환
            extractedData = imageToText(jpgImgData)
            # Weaviate 컬렉션 확인 및 저장
            
            data = {
                        "pdf_id": pdfId,
                        "full_text": extractedData.get("texts"),
                        "pdf_link": pdfLink
                    }
            with pdfCollection.batch.dynamic() as batch:
                batch.add_object(
                    properties=data
                )
            # JSON 응답 반환
            return {"resultCode": 200, "data": data}
    
    except Exception as e:
        print(f"Error in /ocrTest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/searchFulltext')
async def searchFulltext(title: str):
    return await ocr_service.searchFulltext(title)

