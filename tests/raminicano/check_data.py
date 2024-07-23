import weaviate
import os
import weaviate.classes.config as wc
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter




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


chunkCollection = client.collections.get("chunk_en_pdf")


# response = chunkCollection.query.fetch_objects(filters=Filter.by_property("pdf_id").equal("a0f1e14a-34dc-4b38-abe9-1d063beeea32.pdf"), limit=200)
response = chunkCollection.query.fetch_objects(filters=Filter.by_property("chunk_id").equal(1), limit=200)

for o in response.objects:
    print(o.properties)