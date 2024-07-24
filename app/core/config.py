import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "MainFastAPI"
    PROJECT_VERSION: str = "1.0.0"

    # 데이터베이스 설정
    #DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Weaviate 설정
    WEAVIATE_URL: str = os.getenv("WCS_URL")
    WEAVIATE_API_KEY: str = os.getenv("WCS_API_KEY")

    # 외부 API 키 설정
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    TEXTRAZOR_API_KEY: str = os.getenv("TEXTRAZOR_API_KEY")
    DEEPL_AUTH_KEY: str = os.getenv("DEEPL_AUTH_KEY")
    
    # google search 설정
    API_KEY = os.getenv("CUSTOM_SEARCH_API")
    CX = os.getenv("GOOGLE_CX")
    
    # IP
    JH_IP = os.getenv("JH_IP")
    YJ_IP = os.getenv("YJ_IP")
    HJ_IP = os.getenv("HJ_IP")
    CY_IP = os.getenv("CY_IP")
    MY_IP = os.getenv("MY_IP")
    

    # SUBFASTAPI
    SUBFASTAPI_URL: str = os.getenv("SUBFASTAPI_URL")
    # MAINFASTAPI
    MAINFASTAPI: str = os.getenv("MAINFASTAPI")

    # 애플리케이션 모드
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
