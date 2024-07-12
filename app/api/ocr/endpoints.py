from fastapi import APIRouter, FastAPI, HTTPException, Form, Body, UploadFile, File
import os
from fastapi.responses import JSONResponse, HTMLResponse
from google.cloud import vision
from dotenv import load_dotenv
from app.services import paper_service, keyword_extract_service, ocr
from app.services.ocr import pdfStreamToJpg, imageToText, downloadPdfLink
from app.db.weaviate_utils import saveToWeaviate, getTextsByTitle, getAllSchema, deleteClass, getClassData, deleteDataByTitle

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
        deleteDataByTitle("Document", title)
        return getClassData("Document", 50)
    except Exception as e:
        print(f"Error in /deleteData: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/ocrTest")
async def uploadData(file: UploadFile = File(None), pdfUrl: str = Form(None)):
    try:
        pdfStreamData = None
        title = None

        if pdfUrl:
            pdfStreamData = downloadPdfLink(pdfUrl)
            # PDF URL을 제목으로 사용
            title = pdfUrl
        else:
            pdfStreamData = await file.read()
            # 파일 이름에서 .pdf를 뺀 부분을 제목으로 사용
            title = os.path.splitext(file.filename)[0]

        # Weaviate에서 title이 존재하는지 확인
        existingData = getTextsByTitle("Document", title)

        # title이 존재하면 해당 데이터를 반환
        if isinstance(existingData, dict):
            return JSONResponse(content={"resultCode": 200, 
                                         "data": existingData})

        # PDF 스트림 데이터를 JPEG 이미지로 변환
        jpgImgData = pdfStreamToJpg(pdfStreamData)

        # 이미지 데이터를 텍스트로 변환
        extractedData = imageToText(jpgImgData)

        # Weaviate 컬렉션 확인 및 저장
        saveResult = saveToWeaviate(title, extractedData.get("texts"))

        # JSON 응답 반환
        return JSONResponse(content={"resultCode": 200, 
                                     "data": {"title": title, 
                                              "texts": extractedData.get("texts")}, 
                                     "save_result": saveResult})
    except Exception as e:
        print(f"Error in /ocrTest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/searchFulltext')
async def searchFulltext(title: str):
    return await ocr.searchFulltext(title)

# @app.post("/ocr/ocrPdf")
# async def upload_stream(request: Request):
#     try:
#         # 요청 헤더에서 title 가져오기
#         title = request.headers.get("titles")
#         if not title:
#             raise HTTPException(status_code=400, detail="Title header is missing.")

#         # 팀원의 getFullText API 호출하여 full_text 존재 여부 확인
#         response = requests.get(f"{YJ_IP}:3500/getFullText", params={"title": title})
        
#         print(response.json())
        
#         if response.json().get("resultCode") == 200 and response.json().get("data"):
#             # title이 이미 존재하고, full_text 데이터를 가져옴
#             print(f"Full text already exists for title: {title}")
#             text_value = response.json().get("data")
#             return JSONResponse(content={"resultCode": 200,  "data": {"titles": title, "texts": text_value}})
#         else:
#             # PDF 스트림 데이터 읽기
#             pdf_stream_data = await request.body()
        
#             print(f"Received title: {title}")
        
#             # PDF 스트림 데이터를 JPEG 이미지로 변환
#             jpg_image_data = pdf_stream_to_jpg(pdf_stream_data)
        
#             # 이미지 데이터를 텍스트로 변환
#             extracted_data = image_to_text(jpg_image_data)

#             print(f"Extracted text and title saved")

#             #존재하지 않으면 store_full_text API 호출하여 저장
#             payload = {
#                 "title": title,
#                 "result": extracted_data.get("result"),
#                 "text": extracted_data.get("texts")
#             }
#             headers = {"Content-Type": "application/json"}
#             response = requests.post(f"{YJ_IP}:3500/store_full_text", data=json.dumps(payload), headers=headers)
            
#             if response.json().get("resultCode") == 200: 
#                 # result = response.json()
#                 # text_value = result.get("text", "")
#                 print(f"Data stored successfully")
#             else:
#                 print(f"Failed to store data: {response.status_code} - {response.text}")
#                 text_value = "Failed to store data"
                
#             return JSONResponse(content={"resultCode": 200, "data": {"titles": payload.get("title"), "texts": payload.get("text")}}) 

#     except Exception as e:
#         print(f"Error in /upload: {str(e)}")