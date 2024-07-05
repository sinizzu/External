import requests
import os
import re
from typing import List, Dict, Any
import feedparser
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, HTTPException, Query, Body
import weaviate
from weaviate.classes.query import Filter, MetadataQuery
import model
from model import collection

import warnings
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from datetime import datetime
from langchain.text_splitter import CharacterTextSplitter
import concurrent.futures

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')


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

FASTAPI_URL1 = os.getenv('FASTAPI_URL1')
FASTAPI_URL2 = os.getenv('FASTAPI_URL2')

app = FastAPI()


@app.get('/')
async def health_check():
    return "OK"

# ArXiv API를 사용해 arXiv papers를 가져오기
@app.get("/getMeta")
async def get_meta(searchword: str = Query(..., description="Search term for arXiv API")) -> Dict[str, Any]:
    try:
        text = searchword.replace(" ", "+")
        base_url = f"http://export.arxiv.org/api/query?search_query=ti:{text}+OR+abs:{text}&sortBy=relevance&sortOrder=descending&start=0&max_results=15"

        response = requests.get(base_url)
        if response.status_code != 200:
            return {"resultCode": 500, "data": "Failed to fetch data from arXiv API"}
        
        feed = feedparser.parse(response.content)
        papers: List[Dict[str, Any]] = []

        for entry in feed.entries:
            link = entry.links[0]['href'] if entry.links else None
            pdf_link = entry.links[1]['href'] if len(entry.links) > 1 else None
            category = entry.arxiv_primary_category['term'] if 'arxiv_primary_category' in entry else None

            paper = {
                "title": entry.title,
                "authors": [author.name for author in entry.authors],
                "abstract": entry.summary,
                "published": entry.published,
                "direct_link": link,
                "pdf_link": pdf_link,
                "category": category
            }
            papers.append(paper)

        return {
            "resultCode": 200,
            "data": papers
        }
    except requests.exceptions.RequestException as e:
        return {"resultCode": 400, "data": str(e)}

    except Exception as e:
        return {"resultCode": 500, "data": str(e)}


# 키워드 기반 weaviate 검색
@app.get("/searchKeyword")
async def search_keyword(searchword: str = Query(..., description="Search term for Weaviate db")) -> Dict[str, Any]:
    try:
        response = collection.query.bm25(
            query=searchword,
            return_metadata=MetadataQuery(score=True),
            query_properties=["title", "authors", "abstract"],
            limit=10
        )
        res = []
        # 오브젝트가 있으면
        if response.objects:
            for object in response.objects:
                res.append(object.properties) # 반환 데이터에 추가
            return {"resultCode" : 200, "data" : res}
        else:
            return {"resultCode" : 404, "data" : response}
    
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}

# 구어체 기반 weaviate 검색 
# searchword = 'Why Deepfake Videos Are Really Visible'
@app.get('/getColl')
async def getColl(searchword: str):
    result = []
    # print(searchword)
    result = []
    questions  = client.collections.get("Paper")
    response = questions.query.near_text(
        query=searchword,
        limit=10
    )
    res = []
    # 오브젝트가 있으면
    if response.objects:
        for object in response.objects:
            res.append(object.properties) # 반환 데이터에 추가
        return {"resultCode" : 200, "data" : res}
    else:
        return {"resultCode" : 404, "data" : response}


@app.get('/dbpiasearch')
async def get_trend_keywords():
    # 요청할 URL
    url = 'https://www.dbpia.co.kr/curation/best-node/top/20?bestCode=ND'

    # requests를 사용하여 JSON 데이터 가져오기
    response = requests.get(url)
    response.raise_for_status()  # 오류 체크

    # JSON 데이터 파싱
    data = response.json()

    # node_id 값을 추출하고 전체 URL 생성
    base_url = 'https://www.dbpia.co.kr/journal/articleDetail?nodeId='
    urls = [base_url + item['node_id'] for item in data]
    
    # 각 URL에서 해시태그 추출
    all_keywords = []
    for url in urls:
        keywords = extract_keywords(url)
        filtered_keywords = filter_keywords(keywords)
        all_keywords.extend(filtered_keywords)
        # print(f"Extracted keywords from {url}: {filtered_keywords}")

    if all_keywords:
            return {"resultCode" : 200, "keywords" : all_keywords}
    else:
        return {"resultCode" : 404, "keywords" : all_keywords}

def extract_keywords(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 오류 체크
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 클래스 이름이 'keywordWrap__keyword'인 요소 찾기
        keywords = [tag.text.strip() for tag in soup.find_all(class_='keywordWrap__keyword')]
        # 불필요한 첫 글자(#) 제거
        keywords = [keyword[1:] if keyword.startswith("#") else keyword for keyword in keywords]
        return keywords
    except Exception as e:
        print(f"Error extracting keywords from {url}: {e}")
        return []

def filter_keywords(keywords):
    filtered_keywords = []
    for keyword in keywords:
        # 한글이 포함된 키워드 제거
        if re.search('[가-힣]', keyword):
            continue
        # 괄호 안에 한글 설명이 포함된 키워드 제거
        if re.search(r'\([가-힣]+\)', keyword):
            continue
        filtered_keywords.append(keyword)
    return filtered_keywords

@app.get('/searchPopularkeyord')
async def search_popular_keyword():
    # dbpia API에서 인기있는 검색어 가져오기
    response = await get_trend_keywords()
    keywords = response.get("keywords", [])
    
    results = []
    for keyword in keywords:
        try:
            keyword_response = requests.get(f'{FASTAPI_URL2}/getMeta?searchword={keyword}')
            keyword_data = keyword_response.json()
            results.append({'keyword': keyword, 'length': len(keyword_data)})
        except Exception as e:
            print(f'Error fetching data for keyword: {keyword}', e)
            results.append({'keyword': keyword, 'length': 0})
    
    if results:
        return {"resultCode" : 200, "data" : results}
    else:
        return {"resultCode" : 404, "data" : results}

