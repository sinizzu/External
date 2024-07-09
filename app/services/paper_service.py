from typing import List, Dict, Any
from fastapi import HTTPException, Query, Request
from app.schemas import paper as paper_schema
from app.db.connect_db import get_weaviate_client
import feedparser
import requests
from weaviate.classes.query import Filter, MetadataQuery
import re
from bs4 import BeautifulSoup

import warnings

client = get_weaviate_client()
paperCollection = client.collections.get("Paper")
documentCollection = client.collections.get("Document")

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')



def getMeta(searchword: str = Query(..., description="Search term for arXiv API")) -> Dict[str, Any]:
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



async def saveWea(meta_response: paper_schema.MetaResponse) -> paper_schema.SaveWeaResponse:
    papers = meta_response.data
    try:
        with paperCollection.batch.dynamic() as batch:
            for paper in papers:
                response = paperCollection.query.fetch_objects(
                    filters=Filter.by_property("title").equal(paper.title),
                    limit=1
                )

                # object가 있으면 건너뛰기
                if response.objects:
                    continue
                
                properties = {
                    "title": paper.title,
                    "authors": paper.authors,
                    "abstract": paper.abstract,
                    "published": paper.published,
                    "direct_link": paper.direct_link,
                    "pdf_link": paper.pdf_link,
                    "category": paper.category,
                }

                batch.add_object(
                    properties=properties,
                )

        return paper_schema.SaveWeaResponse(resultCode=200, data={"message": "데이터 저장이 완료되었습니다."})
    except Exception as e:
        raise paper_schema.SaveWeaResponse(resultCode=500, data={"message": str(e)})
    

def searchKeyword(searchword: str = Query(..., description="Search term for Weaviate db")) -> Dict[str, Any]:
    try:
        response = paperCollection.query.bm25(
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
            return {"resultCode" : 400, "data" : response}
    
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}

# 구어체 기반 weaviate 검색 
async def getColl(searchword: str):
    try: 
        response = paperCollection.query.near_text(
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
            return {"resultCode" : 400, "data" : response}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}

# dbpia 인기키워드 검색
async def trendKeywords():
    try:
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
            keywords = extractKeywords(url)
            filtered_keywords = filterKeywords(keywords)
            all_keywords.extend(filtered_keywords)

        if all_keywords:
                return {"resultCode" : 200, "keywords" : all_keywords}
        else:
            return {"resultCode" : 400, "keywords" : all_keywords}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}

def extractKeywords(url):
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

def filterKeywords(keywords):
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


# 인기 검색어를 arXiv에서 검색
async def searchPopularKeyword():
    # dbpia API에서 인기있는 검색어 가져오기
    response = await trendKeywords()
    keywords = response.get("keywords", [])
    
    results = []
    for keyword in keywords:
        try:
            keyword_response = getMeta(keyword)
            results.append(keyword_response)
        except Exception as e:
            print(f'Error fetching data for keyword: {keyword}', e)
            results.append(keyword)
    
    if results:
        return {"resultCode" : 200, "data" : results}
    else:
        return {"resultCode" : 400, "data" : results}
    