from fastapi.responses import JSONResponse
import requests
from app.core.config import settings

API_KEY = settings.API_KEY
CX = settings.CX


async def search_query(query: str) -> list:
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query, 
        "num": 10
    }

    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
    data = response.json()
    results = []
    
    if 'items' in data:
        for item in data['items']:
            link = item.get('link', '')
            title = item.get('title', 'No title')
            snippet = item.get('snippet', 'No snippet available')
            image = ''
            
            pagemap = item.get('pagemap', {})
            cse_image_list = pagemap.get('cse_image', [])
            if cse_image_list:
                image = cse_image_list[0].get('src', '')

            results.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "image": image,
            })

    return results