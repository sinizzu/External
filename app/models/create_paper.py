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
    name="paper",
    vectorizer_config=Configure.Vectorizer.text2vec_huggingface(model="sentence-transformers/all-MiniLM-L6-v2"),
    properties=[
        wc.Property(name="title", data_type=wc.DataType.TEXT),
        wc.Property(name="authors", data_type=wc.DataType.TEXT_ARRAY),
        wc.Property(name="abstract", data_type=wc.DataType.TEXT),
        wc.Property(name="published", data_type=wc.DataType.DATE, skip_vectorization=True),
        wc.Property(name="direct_link", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="pdf_link", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="category", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="trans_summary", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="summary", data_type=wc.DataType.TEXT, skip_vectorization=True),
    ],
    # Define the generative module
    generative_config=wc.Configure.Generative.openai('gpt-3.5-turbo-16k'),
)

# 스키마 생성 확인
print("paper 컬렉션이 성공적으로 생성되었습니다.")
collection = client.collections.get("paper")
print(collection)

client.close()