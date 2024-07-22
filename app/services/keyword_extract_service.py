from fastapi import FastAPI
from app.core.config import settings
import wikipediaapi
import app.services.ocr_service as ocr
    
#위키검색 함수 선언
def wiki_search(keyword: str, lang: str):
    if lang == 'kr':
        wiki_wiki = wikipediaapi.Wikipedia( 
        user_agent='MyProjectName (merlin@example.com)',
        language='ko',
        extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        page = wiki_wiki.page(keyword) # 위키 api 호출해서 얻은 키워드 검색에 대한 위키피디아 페이지
        link = f'https://ko.wikipedia.org/wiki/{keyword}' # 위키피디아링크 형식
    else:
        wiki_wiki = wikipediaapi.Wikipedia( 
            user_agent='MyProjectName (merlin@example.com)',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        ) # 이건 위키피디아 api호출시 넣어줘야함, language는 ko하면 한글로 설정할수 있는데 영어논문이라 한글 위키에서는 검색이 안됬었음
        page = wiki_wiki.page(keyword) # 위키 api 호출해서 얻은 키워드 검색에 대한 위키피디아 페이지
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