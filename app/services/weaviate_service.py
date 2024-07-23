
from app.db.connect_db import get_weaviate_client
from weaviate.classes.query import Filter

client = get_weaviate_client()
pdfCollection = client.collections.get("pdf")
paperCollection = client.collections.get("paper")

# weaviate full text 검색
def searchFulltext(pdf_id: str):
    try: 
        response = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id),
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

def searchAll(collection_name: str):
    try:
        collection = client.collections.get(collection_name)
        response = collection.query.fetch_objects()
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
    
def searchPaperId(pdf_url: str):
    try: 
        response = paperCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_link").equal(pdf_url),
        )
        res = []
        # 오브젝트가 있으면
        if response.objects:
            for object in response.objects:
                res.append(object.uuid) # 반환 데이터에 추가
            return {"resultCode" : 200, "data" : res[0]}
        else:
            return {"resultCode" : 400, "data" : response}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}
    
def summarySearch(pdf_id: str):
    try: 
        response = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id),
        )
        # 오브젝트가 있으면
        if response.objects:
            for object in response.objects:
                res = object.properties.get("summary")
        if res == None:
            res = "No summary available"
            return {"resultCode" : 404, "data" : res}
        else:
            return {"resultCode": 200,"data" : res}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}
    
def summarySave(pdf_id: str, summary: str):
    try: 
        res = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id)
        )
        for o in res.objects:
            pdf_uuid = o.uuid
        response = pdfCollection.data.update(
            uuid=pdf_uuid,
            properties={"summary": summary}
        )
        return {"resultCode" : 200, "data" : response}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}

def keywordSearch(pdf_id: str):
    try: 
        response = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id),
        )
        # 오브젝트가 있으면
        if response.objects:
            for object in response.objects:
                res = object.properties.get("keywords")
        if res == None:
            res = "No keywords available"
            return {"resultCode" : 404, "data" : res}
        else:
            return {"resultCode": 200,"data" : res}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}
        
def keywordSave(pdf_id: str, keywords: list):
    try: 
        res = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id)
        )
        for o in res.objects:
            pdf_uuid = o.uuid
        response = pdfCollection.data.update(
            uuid=pdf_uuid,
            properties={"keywords": keywords}
        )
        return {"resultCode" : 200, "data" : "success"}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}
    
def transelateSummarySearch(pdf_id: str):
    try: 
        response = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id),
        )
        # 오브젝트가 있으면
        if response.objects:
            for object in response.objects:
                res = object.properties.get("trans_summary")
        if res == None:
            res = "No translated summary available"
            return {"resultCode" : 404, "data" : res}
        else:
            return {"resultCode": 200,"data" : res}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}
    
def transSave(pdf_id: str, trans_summary: str):
    try:
        res = pdfCollection.query.fetch_objects(
            filters=Filter.by_property("pdf_id").equal(pdf_id)
        )
        for o in res.objects:
            pdf_uuid = o.uuid
        response = pdfCollection.data.update(
            uuid=pdf_uuid,
            properties={"trans_summary": trans_summary}
        )
        return {"resultCode" : 200, "data" : "success"}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}