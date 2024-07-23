from fastapi import APIRouter, HTTPException, Request
from app.services import transelate_service, weaviate_service
from app.schemas.sentence import TextRequest, LanguageRequest

router = APIRouter()

@router.post("/transelateToEnglish")
async def transelateText(request: TextRequest):
    try:
        json_body = request.text
        data = transelate_service.kotoenTranslate(json_body)
        return {"resultCode": 200, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transelate")
async def transelateText(request: LanguageRequest):
    try:
        text = request.text
        lang = request.lang
        if lang == "kr":
            data = transelate_service.kotoenTranslate(text)
        else:
            data = transelate_service.entokoTranslate(text)
        return {"resultCode": 200, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transelateSummary")
async def transelateSummary(pdf_id: str):
    try:
        lang = weaviate_service.searchFulltext(pdf_id)
        lang = lang['data'][0].get('language', 'No content available')
        res = transelate_service.summaryTranslate(pdf_id, lang)
        text = res.get("data")
        if res.get("resultCode") == 200:
            save = weaviate_service.transSave(pdf_id, text)
            print(save)
            return {"resultCode": 200, "data": text}
        else:
            print("summaryTranslate error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkLanguage")
async def checkLanguage(request: TextRequest):
    return transelate_service.korCheck(request.text)
    


