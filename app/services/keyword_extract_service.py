from fastapi import FastAPI
from app.core.config import settings
import wikipedia
import wikipediaapi
import textrazor
import os
import app.services.ocr as ocr


textrazor.api_key = settings.TEXTRAZOR_API_KEY
tr_client = textrazor.TextRazor(extractors=["entities", "keywords"])

# 밑에는 textrazor에서 키워드 추출할때 설정해줄수 있는 타입임
# 종류는 actionList에 정리해놓겠슴
tr_client.set_classifiers(["textrazor_mediatopics_2023Q1"])
# 키워드 추출 함수 선언
def keyword_extraction():
    current_dir = os.path.dirname(__file__)
    pdf_file_path = os.path.join(current_dir, "data", "Articles.pdf") # ocr할 pdf 파일 경로 정의

    text = ocr.pdf_to_text(pdf_file_path) # pdf 파일을 ocr api로 보내서 text로 변환
    
    keyword = {} # 키워드, 점수를 저장할 keyword 딕셔너리 선언
    link = {} # 키워드, 링크를 저장할 link 딕셔너리 선언 근데 안씀
    wikiLink = {} # 키워드, 링크를 저장할 wikiLink 딕셔너리 선언
    wiki_result = {} # 키워드, 결과를 저장할 wikiResult 딕셔너리 선언
    
    response = tr_client.analyze(text).json['response'] # textrazor api를 호출
    entities = response['entities'] # textrazor의 entities에 키워드랑 점수가 포함되어 있어서 entities 불러옴

    for entity in entities: # entity변수에 entities를 각각 넣어줌
        word = entity['entityId'] # word에 textrazor로 추출한 키워드를 저장 
        score = entity['relevanceScore'] # score에 textrazor로 추출한 점수를 저장 (relevanceScore는 상대점수 0 ~ 1 까지)
        wiki_Link = entity['wikiLink'] # wikiLink에 textrazor로 추출한 링크를 저장
        keyword[word] = score # 키워드 딕셔너리로 keyword와 score를 저장
        link[word] = wiki_Link # link 딕셔너리로 keyword와 Link를 저장

    # 키워드를 점수 기준으로 정렬하여 상위 10개 선택
    keywords = dict(sorted(keyword.items(), key=lambda item: item[1], reverse=True)[:10])

    # 만약에 키워드가 있다면
    if keywords:
        # return 해줘
        return {
            # result_code는 200번
            "result_Code": 200,
            # return값의 data는 키워드로
            "data": keywords
        }
    else:
        return {
            # 키워드 없을때는 404에러
            "result_Code": 404,
            "data": None
        }
    
#위키검색 함수 선언
def wiki_search(keyword: str): # 위키검색할때 뭘검색해야할지 받을건데 변수는 keyword로 하고 string 타입으로 받겠다.
    wiki_wiki = wikipediaapi.Wikipedia( 
        user_agent='MyProjectName (merlin@example.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    ) # 이건 위키피디아 api호출시 넣어줘야함, language는 ko하면 한글로 설정할수 있는데 영어논문이라 한글 위키에서는 검색이 안됬었음
    page = wiki_wiki.page(keyword) # 위키 api 호출해서 얻은 키워드 검색에 대한 위키피디아 페이지
    print(page.text) # 디버그를 위해서 출력해봄
    link = f'https://en.wikipedia.org/wiki/{keyword}' # 위키피디아링크 형식
    
    # 만약에 페이지가 있으면 실행
    if page.exists(): 
        # page.text하면 페이지의 모든 text들을 가져오는것임 
        full_text = page.text #full_text로 선언후 return 해줌
        return {
            "resultCode": 200,
            "data": {
                "text": full_text,
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