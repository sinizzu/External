from app.db.connect_db import get_weaviate_client
from fastapi import Query
from weaviate.classes.query import Filter
from app.schemas import chatbot as chatbot_schema


client = get_weaviate_client()
pdfCollection = client.collections.get("pdf")
chunkCollection = client.collections.get("chunk_pdf")



def create_chunks(text, chunk_size, chunk_overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - chunk_overlap)
    return chunks


async def divideChunk(request: chatbot_schema.DivideChunkRequest):
    check = chunkCollection.query.fetch_objects(
        filters=Filter.by_property("pdf_id").equal(request.pdfId),
        limit=1)
    
    if check.objects:
        return {"resultCode": 201, "data": "chunk data already exists"}
    
    else:
        chunked_text = create_chunks(request.fullText, 1000, 200)
        try:
            with chunkCollection.batch.dynamic() as batch:
                for i, chunk in enumerate(chunked_text):

                    data_properties = {
                        "pdf_id": request.pdfId, 
                        "chunk_text": chunk,
                        "chunk_id": i
                    }


                    batch.add_object(
                        properties=data_properties,
                    )
                

            return {"resultCode": 200, "data": "chunk data create success"}
        except Exception as e:
            return {"resultCode": 500, "data": str(e)}



async def useChatbot(request: chatbot_schema.UseChatbotRequest):

    task =  "Answer the following questions in Korean based on the text provided:\n\n"
    # return chunk data 해주기
    try:
        res = chunkCollection.generate.near_text(
            filters=(
                Filter.by_property("pdf_id").equal(request.pdfId)
            ),
            query=request.query,
            limit=5,
            grouped_task=task
        )

        return {"resultCode": 200, "data": res.generated}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}