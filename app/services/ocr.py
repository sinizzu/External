from google.cloud import vision
from fastapi import HTTPException
from pdf2image import convert_from_path, convert_from_bytes 
import io, os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from app.db.connect_db import get_weaviate_client
from weaviate.classes.query import Filter
import re

# Google Cloud Vision API 인증을 위한 환경 변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./ocr_key.json"

client = get_weaviate_client()
documentCollection = client.collections.get("Document")

# Vision API 클라이언트 초기화
client = vision.ImageAnnotatorClient()
def pdf_to_text(pdf_file):
    # Google Cloud Vision API 클라이언트 생성
    client = vision.ImageAnnotatorClient()

    # PDF 파일을 이미지로 변환
    images = convert_from_path(pdf_file)
    
    extracted_text = ""

    for page_number, image in enumerate(images):
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            content = output.getvalue()
        
        # Vision API 요청을 위한 Image 객체 생성
        image = vision.Image(content=content)
        
        # 텍스트 인식 요청 및 결과 처리
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            extracted_text += f"Page {page_number + 1}:\n"
            extracted_text += texts[0].description
            extracted_text += "\n\n"
        else:
            extracted_text += f"Page {page_number + 1}:\nNo text found\n\n"

        if response.error.message:
            raise Exception(f"Error during text detection: {response.error.message}")

    return extracted_text
if __name__ == "__main__":
    pdf_file_path = "./data/test2.pdf"
    extracted_text = pdf_to_text(pdf_file_path)
    print("Extracted text:")
    print(extracted_text)


# 디렉토리가 없으면 생성하는 함수
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def pdf_stream_to_jpg(pdf_stream):
    try:
        # PDF 스트림 데이터를 이미지로 변환
        images = convert_from_bytes(pdf_stream)
        
        if not images:
            raise HTTPException(status_code=400, detail="No images found in PDF")

        image_datas = []
        for image in images:
            with io.BytesIO() as output:
                image.convert("RGB").save(output, format="JPEG")
                image_data = output.getvalue()
                image_datas.append(image_data)
                
        return image_datas
    except Exception as e:
        print(f"Error converting PDF to image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def image_to_text(image_data):
    try:
        client = vision.ImageAnnotatorClient()
        combined_text = ""

        for img_data in image_data:
            # Vision API 요청을 위한 Image 객체 생성
            vision_image = vision.Image(content=img_data)
            
            # 텍스트 인식 요청 및 결과 처리
            response = client.document_text_detection(image=vision_image)
            full_text = ""

            if response.full_text_annotation:
                for page in response.full_text_annotation.pages:
                    for block in page.blocks:
                        for paragraph in block.paragraphs:
                            paragraph_text = ''
                            for word in paragraph.words:
                                word_text = ''.join([symbol.text for symbol in word.symbols])
                                paragraph_text += word_text + ' '  # 단어 간 공백 추가
                            full_text += paragraph_text.strip() + "\\n\\n"  # 단락 구분을 위해 두 개의 개행 문자를 추가하고 앞뒤 공백 제거
            else:
                full_text = "No text found"
            
            # 텍스트를 바로 결합
            combined_text += full_text

        print(f"Combined text length: {len(combined_text)}")
        # 텍스트 분할 및 필터링
        document = Document(page_content=combined_text)
        text_splitter = CharacterTextSplitter(separator="\\n\\n", chunk_size=2000, chunk_overlap=100)
        split_docs = text_splitter.split_documents([document])
        
        filtered_docs = []
        for doc in split_docs:
            if "References" in doc.page_content:
                doc.page_content = doc.page_content.split("References")[0]
                filtered_docs.append(doc.page_content)
                break
            filtered_docs.append(doc.page_content)
        
        filtered_text = "\\n\\n".join(filtered_docs)
        
        # Create a dictionary in the required format
        output_data = {
            "result": 200,
            "texts": filtered_text
        }
        return output_data
    except Exception as e:
        print(f"Error processing image for OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# weaviate full text 검색
async def searchFulltext(title: str):
    try: 
        response = documentCollection.query.fetch_objects(
            filters=Filter.by_property("title").equal(title),
        )
        res = []
        # 오브젝트가 있으면
        if response.objects:
            for object in response.objects:
                res.append(object.properties) # 반환 데이터에 추가
            fullTexts = res[0].get("texts")
            res = process_text(fullTexts)
            # res = fullTexts
            return {"resultCode" : 200, "data" : res}
        else:
            return {"resultCode" : 400, "data" : response}
    except Exception as e:
        return {"resultCode": 500, "data": str(e)}

 # 전체 텍스트를 초록, 서론, 결론 추출
def process_text(text):
    try:
        # Define regex patterns for abstract, introduction, and conclusion
        abstract_pattern = re.compile(r'(?i)abstract\s*(.*?)(?=(introduction|1\sIntroduction))', re.DOTALL)
        introduction_pattern = re.compile(r'(?i)(introduction|1\sIntroduction)\s*(.*?)(?=\\n\\n2\s)', re.DOTALL)
        conclusion_pattern = re.compile(r'(?i)(conclusion|6\sConclusion)\s*(.*)', re.DOTALL)
        
        # Find matches
        abstract_match = abstract_pattern.search(text)
        introduction_match = introduction_pattern.search(text)
        conclusion_match = conclusion_pattern.search(text)
        
        # Extract matched sections
        abstract = abstract_match.group(1).strip() if abstract_match else "Abstract not found."
        introduction = introduction_match.group(2).strip() if introduction_match else "Introduction not found."
        conclusion = conclusion_match.group(2).strip() if conclusion_match else "Conclusion not found."
        
        response = {
            "abstract": abstract,
            "introduction": introduction,
            "conclusion": conclusion
        }

        return response
    except Exception as e:
        print(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

