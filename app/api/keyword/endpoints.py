from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from app.services.web_search import search_query
from fastapi import APIRouter

router = APIRouter()

@router.post("/searchWeb", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    return await search_query(query)

