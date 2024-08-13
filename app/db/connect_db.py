import weaviate
from fastapi import Depends
from app.core.config import settings

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

def get_weaviate_client():
    client = connect_to_weaviate()
    if not client.is_ready():
        raise ConnectionError("Weaviate Cloud에 연결할 수 없습니다.")
    return client
