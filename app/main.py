from fastapi import FastAPI
from app.api import paper_endpoints, trans_endpoints, ocr_endpoints, keyword_endpoints
from app.core.config import settings
from app.api.keyword import endpoints as search_endpoints
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler  



JH_IP = settings.JH_IP

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", f"http://{JH_IP}"],  # 모든 도메인에서 오는 요청을 허용합니다. 실제로는 필요한 도메인만 허용하도록 변경해야 합니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_scheduler()

# Include routers
app.include_router(paper_endpoints.router, prefix="/api/paper", tags=["paper"])
app.include_router(ocr_endpoints.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(search_endpoints.router, prefix="/search", tags=["search"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
