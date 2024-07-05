from typing import List, Dict, Any
from fastapi import HTTPException, Query
from app.schemas import paper as paper_schema
from app.db.connect_db import get_weaviate_client
import feedparser
import requests
from weaviate.classes.query import Filter, MetadataQuery

client = get_weaviate_client()
paperCollection = client.collections.get("Paper")


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
        with paperCollection.batch.fixed_size(5) as batch:
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