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
def get_all_schema_names():
    schema = client.schema.get()
    class_names = [cls["class"] for cls in schema["classes"]]
    result = {
        "resultCode": 200,
        "data": class_names
    }
    return result

# 클래스 삭제 함수
def delete_class(class_name):
    try:
        client.schema.delete_class(class_name)
        print(f"Class '{class_name}' has been successfully deleted.")
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        print(f"Failed to delete class '{class_name}': {str(e)}")
        
# Document 클래스 생성 함수
def create_document_class():
    try:
        # 기존 클래스 확인
        schema = client.schema.get()
        existing_classes = [cls["class"] for cls in schema["classes"]]
        
        if "Document" not in existing_classes:
            client.schema.create_class(
                {
                    "class": "Document",
                    "properties": [
                        {"name": "title", "dataType": ["string"]},
                        {"name": "texts", "dataType": ["text"]}
                    ]
                }
            )
            print("Document 클래스가 성공적으로 생성되었습니다.")
        else:
            print("Document 클래스가 이미 존재합니다.")
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        print(f"Document 클래스 생성 실패: {str(e)}")

# Weaviate의 Document 클래스에 데이터 저장 함수
def save_to_weaviate(title, texts):
    try:
        # Document 클래스가 존재하는지 확인하고 없으면 생성
        create_document_class()
        
        data_object = {
            "title": title,
            "texts": texts
        }
        client.data_object.create(data_object, "Document")
        return "Data successfully saved to Weaviate"
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to save data to Weaviate: {str(e)}"
    
# Weaviate의 특정 클래스 데이터를 조회하는 함수
def get_class_data(class_name, max_text_length=50):
    try:
        result = client.query.get(class_name, ["title", "texts"]).with_additional('id').do()
        if 'data' in result and 'Get' in result['data'] and class_name in result['data']['Get']:
            data = result['data']['Get'][class_name]
            formatted_data = [
                {
                    "title": item["title"],
                    "texts": item["texts"][:max_text_length] + "..." if len(item["texts"]) > max_text_length else item["texts"]
                }
                for item in data
            ]
            return formatted_data
        return f"Class '{class_name}' not found or no data available."
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to retrieve data from Weaviate: {str(e)}"
    
# Weaviate의 Document 클래스에서 특정 타이틀을 가진 객체의 texts를 조회하는 함수
def get_texts_by_title(class_name, title, max_text_length=50):
    try:
        query = f"""
        {{
            Get {{
                {class_name} (
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
        if 'data' in result and 'Get' in result['data'] and class_name in result['data']['Get']:
            data = result['data']['Get'][class_name]
            if data:
                item = data[0]
                return {
                    "title": item["title"],
                    "texts": item["texts"][:max_text_length] + "..." if len(item["texts"]) > max_text_length else item["texts"]
                }
            return f"Title '{title}' not found in class '{class_name}'."
        return f"Class '{class_name}' not found or no data available."
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        return f"Failed to retrieve data from Weaviate: {str(e)}"