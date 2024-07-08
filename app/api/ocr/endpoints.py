from fastapi import FastAPI, HTTPException, Form, Body, UploadFile, File
from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse
from google.cloud import vision
from dotenv import load_dotenv
from ocr import pdf_stream_to_jpg, image_to_text, pdf_to_text
from db.weaviate_utils import save_to_weaviate, get_texts_by_title, get_all_schema_names, delete_class, get_class_data

app = FastAPI()
load_dotenv()

@app.get('/getSchemas')
async def get_schemas():
    return get_all_schema_names()
@app.post('/deleteSchema')
async def delete_schema(class_name):
    delete_class(class_name)
@app.get("/getClassData/{class_name}")
async def get_class_data_endpoint(class_name: str, max_text_length: int = 50):
    try:
        data = get_class_data(class_name, max_text_length)
        if isinstance(data, str):
            raise HTTPException(status_code=400, detail=data)
        return {"class_name": class_name, "data": data}
    except Exception as e:
        print(f"Error in /getClassData: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ocr/ocrTest")
async def upload_stream(file: UploadFile = File(...), title: str = Form(...)):
    try:
        # Weaviate에서 title이 존재하는지 확인
        existing_data = get_texts_by_title("Document", title)
        
        # title이 존재하면 해당 데이터를 반환
        if isinstance(existing_data, dict):
            return JSONResponse(content={"resultCode": 200, 
                                         "data": existing_data})
        # PDF 파일 읽기
        pdf_stream_data = await file.read()
    
        # PDF 스트림 데이터를 JPEG 이미지로 변환
        jpg_image_data = pdf_stream_to_jpg(pdf_stream_data)
    
        # 이미지 데이터를 텍스트로 변환
        extracted_data = image_to_text(jpg_image_data)
        
        # weaviate 컬렉션 확인 및 저장
        save_result = save_to_weaviate(title, extracted_data.get("texts"))
        # JSON 응답 반환
        return JSONResponse(content={"resultCode": 200, 
                                     "data": {"title": title, 
                                              "texts": extracted_data.get("texts")}, 
                                     "save_result": save_result})
    except Exception as e:
        print(f"Error in /ocrTest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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