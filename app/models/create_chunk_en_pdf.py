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


# 컬렉션 생성
chunks = client.collections.create(
    name="chunk_en_pdf",
    vectorizer_config=Configure.Vectorizer.text2vec_huggingface(model="sentence-transformers/all-MiniLM-L6-v2"),
    properties=[
        wc.Property(name="pdf_id", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="chunk_text", data_type=wc.DataType.TEXT),
        wc.Property(name="chunk_id", data_type=wc.DataType.INT, skip_vectorization=True),

    ],
    generative_config=wc.Configure.Generative.openai('gpt-3.5-turbo-16k')
)

# 스키마 생성 확인
print("chunk_en_pdf 컬렉션이 성공적으로 생성되었습니다.")
collection = client.collections.get("chunk_en_pdf")
print(collection)

client.close()