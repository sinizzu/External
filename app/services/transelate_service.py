import deepl
from app.core.config import settings
from app.services import weaviate_service
import re

DEEL_KEY = settings.DEEPL_AUTH_KEY
translator = deepl.Translator(DEEL_KEY)

def kotoenTranslate(text):
    transeText = translator.translate_text(text, source_lang="ko", target_lang="en-us")
    return transeText.text

def entokoTranslate(text):
    transeText = translator.translate_text(text, source_lang="en", target_lang="ko")
    return transeText.text

def summaryTranslate(pdf_id, lang):
    transResponde = weaviate_service.transelateSummarySearch(pdf_id)
    if transResponde.get("resultCode") == 200:
        return {"resultCode": 200, "data": transResponde.get("data")}
    else:
        summary = weaviate_service.summarySearch(pdf_id).get("data")
        if lang == "kr":
            response = kotoenTranslate(summary)
        else:
            response = entokoTranslate(summary)
        print("response: ", response)
        return {"resultCode": 200, "data": response}
    
def korCheck(text):
    p = re.compile('[ㄱ-힣]')
    r = p.search(text)
    if r is None:
        return {"resultCode": 200, "lang": "en"}
    else:
        return {"resultCode": 200, "lang": "kr"}
