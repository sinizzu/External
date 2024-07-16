import weaviate
import os
from app.core.config import settings
from weaviate.classes.query import Filter
from app.services.paper_service import getObjectId

# 환경 변수 가져오기
URL = os.getenv("WCS_URL")
APIKEY = os.getenv("WCS_API_KEY")
HUGGING = os.getenv("HUGGINGFACE_API_KEY")

# Weaviate 클라이언트 초기화
def connect_to_weaviate():
    client = weaviate.connect_to_wcs(
        cluster_url=settings.WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(settings.WEAVIATE_API_KEY),
        headers={
            "X-HuggingFace-Api-Key": settings.HUGGINGFACE_API_KEY,
            "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
        },
        skip_init_checks=True
    )
    return client

client = connect_to_weaviate()
pdfCollection = client.collections.get("pdf")

# 연결 확인
if client.is_ready():
    print("Weaviate Cloud에 성공적으로 연결되었습니다.")
else:
    print("Weaviate Cloud에 연결할 수 없습니다.")

# 모든 스키마의 이름만 반환
def getAllSchema():
    schema = client.schema.get()
    classNames = [cls["class"] for cls in schema["classes"]]
    result = {
        "resultCode": 200,
        "data": classNames
    }
    return result

# 클래스 삭제 함수
def deleteClass(className):
    try:
        client.schema.delete_class(className)
        print(f"Class '{className}' has been successfully deleted.")
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        print(f"Failed to delete class '{className}': {str(e)}")
        
# pdf 클래스 생성 함수
def createPdfClass():
    try:
        # 기존 클래스 확인
        schema = client.schema.get()
        existingClasses = [cls["class"] for cls in schema["classes"]]
        
        if "pdf" not in existingClasses:
            client.schema.create_class(
                {
                    "class": "pdf",
                    "properties": [
                        {"name": "title", "dataType": ["string"]},
                        {"name": "texts", "dataType": ["text"]}
                    ]
                }
            )
            print("pdf 컬렉션 성공적으로 생성되었습니다.")
        else:
            print("pdf 컬렉션이 이미 존재합니다.")
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        print(f"pdf 컬렉션 생성 실패: {str(e)}")


# Weaviate의 pdf 클래스에 데이터 저장 함수
def saveToWeaviate(pdfId, title, texts):
    
    try:
        dataObject = {
            "pdf_id": pdfId,
            "pdf_link": title, 
            "full_text": texts
        }
        pdfCollection.data.insert(properties=dataObject)
        return "Data successfully saved to Weaviate"
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to save data to Weaviate: {str(e)}"
    
    
# object id와 pdf_link 가져오기
def getPdfId(uuid):
    try: 
        pdfCollection= client.collections.get("pdf")
        result = pdfCollection.query.fetch_objects(
            filters = Filter.by_property("pdf_id").equals(uuid),
            limit = 1)
        result_id = result.objects[0].properties.get["pdf_id"]
        return {"resultCode" : 200, "data" : result_id}
    except Exception as e:
        return {"resultCode": 400, "data": str(e)}

    
def compareId(pdfLink):
    try:
        # getObjectId 함수 호출하여 uuid 가져오기
        uuid_response = getObjectId(pdfLink) # paper collection에 있는 object ID
        paperId = uuid_response["data"]["uuid"]
        pdfId = getPdfId(paperId)
        if paperId == pdfId : # pdf collection에 있는 object ID
            return {"resultCode:" : 200, "data" : uuid_response}
        else:
            return {"resultCode:" : 400, "data" : uuid_response}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}


# Weaviate의 pdf 클래스에서 특정 타이틀을 가진 객체의 texts를 조회하는 함수
def getTextsById(className, pdfId):
    if not pdfId:
        return None
    
    client = connect_to_weaviate()
    pdfCollection = client.collections.get(className)
    try : 
        
        # Weaviate에서 객체를 조회
        result = pdfCollection.query.fetch_objects(
            filters=(
                Filter.by_property("pdf_id").equal(pdfId)),
            return_properties=["pdf_id", "full_text"]
        )
        if result and result.objects:
            return {"pdf_id": pdfId, "full_texts": result.objects[0].full_text}
        else:
            return None
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to retrieve data from Weaviate: {str(e)}"
    
    
# Weaviate의 특정 클래스 데이터를 조회하는 함수
def getClassData(className, maxTextLength=50):
    try:
        result = pdfCollection.query.get(className, ["title", "texts"]).with_additional('id').do()
        if 'data' in result and 'Get' in result['data'] and className in result['data']['Get']:
            data = result['data']['Get'][className]
            formatted_data = [
                {
                    "title": item["title"],
                    "texts": item["texts"][:maxTextLength] + "..." if len(item["texts"]) > maxTextLength else item["texts"]
                }
                for item in data
            ]
            return formatted_data
        return f"Class '{className}' not found or no data available."
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to retrieve data from Weaviate: {str(e)}"
    
def deleteDataByTitle(className, title):
    try:
# 쿼리 작성
        query = {
            "match": {
                "class": className,
                "where": {
                    "operator": "Equal",
                    "path": ["title"],
                    "valueText": title
                }
            }
        }

        # 삭제 요청
        result = client.data_object.delete(query)

        if result:
            return f"Data with title '{title}' deleted successfully."
        else:
            return f"Title '{title}' not found in class '{className}'."
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to delete data from Weaviate: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"