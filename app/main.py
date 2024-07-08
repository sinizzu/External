from fastapi import FastAPI
from app.api import paper_endpoints, trans_endpoints, ocr_endpoints, keyword_endpoints
from app.core.config import settings
from app.api.keyword import endpoints as search_endpoints

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Include routers
app.include_router(paper_endpoints.router, prefix="/api/paper", tags=["paper"])
app.include_router(ocr_endpoints.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(search_endpoints.router, prefix="/search", tags=["search"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
