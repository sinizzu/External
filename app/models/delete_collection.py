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

client.collections.delete("Pdf")  

client.close()

