import weaviate
import os

# 환경 변수 가져오기
URL = os.getenv("WCS_URL")
APIKEY = os.getenv("WCS_API_KEY")
HUGGING = os.getenv("HUGGINGFACE_API_KEY")

# Weaviate 클라이언트 초기화
client = weaviate.Client(
    url=URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=APIKEY),
    additional_headers={'X-HuggingFace-Api-Key': HUGGING}
)

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
def saveToWeaviate(title, texts):
    try:
        # pdf 클래스가 존재하는지 확인하고 없으면 생성
        createPdfClass()
        
        dataObject = {
            "title": title,
            "texts": texts
        }
        client.data_object.create(dataObject, "pdf")
        return "Data successfully saved to Weaviate"
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to save data to Weaviate: {str(e)}"
    
# Weaviate의 특정 클래스 데이터를 조회하는 함수
def getClassData(className, maxTextLength=50):
    try:
        result = client.query.get(className, ["title", "texts"]).with_additional('id').do()
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
    
# Weaviate의 pdf 클래스에서 특정 타이틀을 가진 객체의 texts를 조회하는 함수
def getTextsByTitle(className, title, maxTextLength=50):
    try:
        query = f"""
        {{
            Get {{
                {className} (
                    where: {{
                        path: ["title"],
                        operator: Equal,
                        valueText: "{title}"
                    }}
                ) {{
                    title
                    texts
                }}
            }}
        }}
        """
        result = client.query.raw(query)
        if 'data' in result and 'Get' in result['data'] and className in result['data']['Get']:
            data = result['data']['Get'][className]
            if data:
                item = data[0]
                return {
                    "title": item["title"],
                    "texts": item["texts"][:maxTextLength] + "..." if len(item["texts"]) > maxTextLength else item["texts"]
                }
            return f"Title '{title}' not found in class '{className}'."
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