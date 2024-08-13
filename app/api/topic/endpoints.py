from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from app.services import keyword_extract_service, weaviate_service

router = APIRouter()

@router.get('/keywordExtract')
async def keyword_extraction(pdf_id: str):
    try:
        getKeyword = weaviate_service.keywordSearch(pdf_id)
        res = getKeyword.get("resultCode")
        if res == 200:
            res = getKeyword.get("data", "")
            return JSONResponse(content={"result_Code": 200, "data": res})
        else:
            response = weaviate_service.searchFulltext(pdf_id)
            texts = response['data'][0].get('full_text', 'No content available')
            keywordsResult = keyword_extract_service.keyword_extraction(texts)

            # Extract the keys from the 'data' dictionary
            keywords = list(keywordsResult['data'].keys())
            res = weaviate_service.keywordSave(pdf_id, keywords)
            data = res['data']
            print("save Keywords: ", data)
            if res['resultCode'] == 200:
                return JSONResponse(content={"result_Code": 200, "data": keywords})
            else:
                return JSONResponse(content={"result_Code": 400, "data": keywords})
    except Exception as e:
        print(f"Error in /keywordExtraction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
