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


chunkCollection = client.collections.get("chunk_pdf")
pdfCollection = client.collections.get("pdf")

# 텍스트 청크 생성
chunk_size = 1000
chunk_overlap = 200

def create_chunks(text, chunk_size, chunk_overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - chunk_overlap)
    return chunks

pdf_id = "ea1cc84c-fd0d-4c5e-9e14-bf5fad2fd042"

response = pdfCollection.query.fetch_objects(
    filters=(
        Filter.by_property("pdf_id").equal(pdf_id)
    ),
    limit=1,
    return_properties=["full_text"]
)

full_text = response.objects[0].properties['full_text']

chunked_text = create_chunks(full_text, chunk_size, chunk_overlap)

# pdf_id로 중복 체크
check = chunkCollection.query.fetch_objects(
        filters=Filter.by_property("pdf_id").equal(pdf_id),
        limit=1)

# return chunk data 해주기
if check.objects:
    print("pdf_id로 중복 체크")
else:
    chunks_list = list()

    try:
        with chunkCollection.batch.dynamic() as batch:
            for i, chunk in enumerate(chunked_text):

                data_properties = {
                    "pdf_id": pdf_id, 
                    "chunk_text": chunk,
                    "chunk_id": i
                }

                # 체크 용도
                chunks_list.append(chunk)

                batch.add_object(
                    properties=data_properties,
                )
    except Exception as e:
        print(e)


# list 확인
for i in chunks_list:
    print(i)

print(len(chunks_list))

client.close()