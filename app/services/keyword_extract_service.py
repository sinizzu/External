from fastapi import FastAPI
from app.core.config import settings
import wikipedia
import wikipediaapi
import textrazor
import os
import app.services.ocr as ocr


textrazor.api_key = settings.TEXTRAZOR_API_KEY
tr_client = textrazor.TextRazor(extractors=["entities", "keywords"])
tr_client.set_classifiers(["textrazor_newscodes"])

def keyword_extraction():
    current_dir = os.path.dirname(__file__)
    pdf_file_path = os.path.join(current_dir, "data", "test.pdf")

    text = ocr.pdf_to_text(pdf_file_path)
    
    keyword = {}
    link = {}
    wikiLink = {}
    wiki_result = {}
    
    response = tr_client.analyze(text).json['response']
    entities = response['entities']

    for entity in entities:
        word = entity['entityId']
        score = entity['relevanceScore']
        wiki_Link = entity['wikiLink']
        keyword[word] = score
        link[word] = wiki_Link

    # 키워드를 점수 기준으로 정렬하여 상위 10개 선택
    keywords = dict(sorted(keyword.items(), key=lambda item: item[1], reverse=True)[:10])

    if keywords:
        return {
            "result_Code": 200,
            "data": keywords
        }
    else:
        return {
            "result_Code": 404,
            "data": None
        }
    
def wiki_search(keyword: str):
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='MyProjectName (merlin@example.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    page = wiki_wiki.page(keyword)

    link = f'https://en.wikipedia.org/wiki/{keyword.replace(" ", "_")}'
    
    if page.exists():
        # 첫 번째 문단 가져오기
        full_text = page.text
        return {
            "resultCode": 200,
            "data": {
                "pharse": full_text,
                "link": link
            }
        }
    else:
        return {
            "resultCode": 404,
            "data": {
                "message": "Page does not exist",
                "link": link
            }
        }