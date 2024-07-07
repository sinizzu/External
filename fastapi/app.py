from fastapi import FastAPI, HTTPException, Form, Body, UploadFile, File
from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from ocr.ocr import pdf_stream_to_jpg, image_to_text, pdf_to_text
from google.cloud import vision
from dotenv import load_dotenv
import json, os, requests
from search.search import search_query
from authlib.integrations.starlette_client import OAuth
from weaviatedb.weaviate_utils import client, get_all_schema_names, delete_class, save_to_weaviate, get_class_data, get_texts_by_title

app = FastAPI()
load_dotenv()

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://<your_ec2_domain>/auth/callback',
    client_kwargs={'scope': 'openid profile email'},
)
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
    
@app.get('/auth')
async def auth(request: Request):
    redirect_uri = 'http://<your_ec2_domain>/auth/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/callback')
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    # 여기에 세션 설정 또는 토큰 반환 로직을 추가할 수 있습니다.
    return {"user": user}


YJ_IP = os.getenv("YJ_IP")
CY_IP = os.getenv("CY_IP")
# 전역 변수로 파일 경로 저장
global uploaded_file_path



@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    return await search_query(query)

    
@app.post("/ocr/ocrPdf")
async def upload_stream(request: Request):
    try:
        # 요청 헤더에서 title 가져오기
        title = request.headers.get("titles")
        if not title:
            raise HTTPException(status_code=400, detail="Title header is missing.")

        # 팀원의 getFullText API 호출하여 full_text 존재 여부 확인
        response = requests.get(f"{YJ_IP}:3500/getFullText", params={"title": title})
        
        print(response.json())
        
        if response.json().get("resultCode") == 200 and response.json().get("data"):
            # title이 이미 존재하고, full_text 데이터를 가져옴
            print(f"Full text already exists for title: {title}")
            text_value = response.json().get("data")
            return JSONResponse(content={"resultCode": 200,  "data": {"titles": title, "texts": text_value}})
        else:
            # PDF 스트림 데이터 읽기
            pdf_stream_data = await request.body()
        
            print(f"Received title: {title}")
        
            # PDF 스트림 데이터를 JPEG 이미지로 변환
            jpg_image_data = pdf_stream_to_jpg(pdf_stream_data)
        
            # 이미지 데이터를 텍스트로 변환
            extracted_data = image_to_text(jpg_image_data)

            print(f"Extracted text and title saved")

            #존재하지 않으면 store_full_text API 호출하여 저장
            payload = {
                "title": title,
                "result": extracted_data.get("result"),
                "text": extracted_data.get("texts")
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{YJ_IP}:3500/store_full_text", data=json.dumps(payload), headers=headers)
            
            if response.json().get("resultCode") == 200: 
                # result = response.json()
                # text_value = result.get("text", "")
                print(f"Data stored successfully")
            else:
                print(f"Failed to store data: {response.status_code} - {response.text}")
                text_value = "Failed to store data"
                
            return JSONResponse(content={"resultCode": 200, "data": {"titles": payload.get("title"), "texts": payload.get("text")}}) 

    except Exception as e:
        print(f"Error in /upload: {str(e)}")

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

   

@app.post("/keyword")
async def getKeyword(data: dict = Body(...)):
    try:
        title = data.get("title")
        if not title:
            raise HTTPException(status_code=400, detail="Title is required.")

        # 팀원의 getFullText API 호출하여 full_text 존재 여부 확인
        response = requests.get(f"{YJ_IP}:3500/getFullText", params={"title": title})
        
        response_data = response.json()
        
        if response_data.get("resultCode") == 200 and response_data.get("data"):
            # title이 이미 존재하고, full_text 데이터를 가져옴
            print(f"Full text already exists for title: {title}")
            text_value = response_data.get("data")
            # Bert_Keyword API 호출하여 키워드 추출
            bert_keyword_response = requests.post(
                f"{CY_IP}:8000/Bert_Keyword",  # Bert_Keyword API의 실제 URL로 변경
                json={"text": text_value}
            )
            bert_keyword_data = bert_keyword_response.json()
            
            return JSONResponse(content={"titles": title, "keywords": bert_keyword_data})
        else:
            print("저장된 텍스트 파일이 없습니다.")
            return JSONResponse(content={"detail": "저장된 텍스트 파일이 없습니다."}, status_code=404)
        
    except Exception as e:
        print(f"Error in /keyword: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getSum1")
async def getsum(title: str):
    try:
        response = requests.get(f"{YJ_IP}:3500/getSummary1", params={"title": title})
        response.raise_for_status()  
        return response.json()
    except requests.RequestException as e:
        print(f"Error in /getSum: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/ocrtext")
async def get_ocrtext(uploaded_file_path):
    try:
        print(f"Uploaded file path: {uploaded_file_path}")


        if not uploaded_file_path:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Google Cloud Vision API 인증을 위한 환경 변수 설정
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./ocr_key.json"
        
        # PDF 파일에서 텍스트 추출
        extracted_text = pdf_to_text(uploaded_file_path)

        # JSON 파일로 저장
        json_file_location = os.path.splitext(uploaded_file_path)[0] + ".json"
        with open(json_file_location, 'w', encoding='utf-8') as json_file:
            json.dump({"extracted_text": extracted_text}, json_file, ensure_ascii=False, indent=4)
        
        return JSONResponse(content={"result": 200, "file_location": json_file_location})
    except Exception as e:
        print(f"Error in /ocrtext: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/getTime")
async def get_time(title:str):
    try :
        time1_response1 = requests.get(f"{YJ_IP}:3500/getTime1?title={title}")
        time1 = time1_response1.json()
        time2_response1 = requests.get(f"{YJ_IP}:3500/getTime2?title={title}")
        time2 = time2_response1.json()
        time3_response1 = requests.get(f"{YJ_IP}:3500/getTime3?title={title}")
        time3 = time3_response1.json()
    except Exception as e:
        print(f"Error in /getTime: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    return time1, time2, time3

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)