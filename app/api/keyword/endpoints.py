from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from web_search import search_query

app = FastAPI()

@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    return await search_query(query)

