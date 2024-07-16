import weaviate
import os
import weaviate.classes.config as wc
from weaviate.classes.config import Configure, Property, DataType



# 환경 변수 가져오기
URL = os.getenv("WCS_URL")
APIKEY = os.getenv("WCS_API_KEY")
HUGGING = os.getenv("HUGGINGFACE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

headers = {
    "X-HuggingFace-Api-Key": HUGGING,
    "X-OpenAI-Api-Key" : OPENAI_API_KEY

}

client = weaviate.connect_to_wcs(
    cluster_url=URL,
    auth_credentials=weaviate.auth.AuthApiKey(APIKEY),
    headers=headers
    )


# 연결 확인
if client.is_ready():
    print("Weaviate Cloud에 성공적으로 연결되었습니다.")
else:
    print("Weaviate Cloud에 연결할 수 없습니다.")


# Paper 클래스의 속성 및 벡터화 설정 정의
client.collections.create(
    name="pdf",
    vectorizer_config=None,
    properties=[
        wc.Property(name="pdf_id", data_type=wc.DataType.TEXT),  # S3 ID or Paper collection object ID
        wc.Property(name="pdf_link", data_type=wc.DataType.TEXT),  # Direct link to the PDF
        wc.Property(name="pre_image", data_type=wc.DataType.BLOB),  # Thumbnail image as blob
        wc.Property(name="keywords", data_type=wc.DataType.TEXT_ARRAY),  # Extracted keywords
        wc.Property(name="full_text", data_type=wc.DataType.TEXT)  # Full text from OCR
    ]
 )


# 스키마 생성 확인
print("Pdf 컬렉션이 성공적으로 생성되었습니다.")
collection = client.collections.get("pdf")
print(collection)

client.close()