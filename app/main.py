from fastapi import FastAPI
from app.api import paper_endpoints, translate_endpoints, ocr_endpoints, chatbot_endpoints, weaviate_endpoints, topic_endpoints
from app.core.config import settings
from app.api.keyword import endpoints as search_endpoints
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler  
import os


JH_IP = settings.JH_IP
YJ_IP = settings.YJ_IP
HJ_IP = settings.HJ_IP


# MainFastAPI = os.getenv("MainFastAPI")
# MainFrontend = os.getenv("MainFrontend")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","http://localhost:8500", f"http://{JH_IP}:8500", f"http://{YJ_IP}:8500", f"http://{HJ_IP}:8500"],  
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_scheduler()

# Include routers
app.include_router(paper_endpoints.router, prefix="/api/paper", tags=["paper"])
app.include_router(ocr_endpoints.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(search_endpoints.router, prefix="/api/search", tags=["search"])
app.include_router(chatbot_endpoints.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(topic_endpoints.router, prefix="/api/topic", tags=["topic"])
app.include_router(translate_endpoints.router, prefix="/api/translate", tags=["translate"])
app.include_router(weaviate_endpoints.router, prefix="/api/weaviate", tags=["weaviate"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
