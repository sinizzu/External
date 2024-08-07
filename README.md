# 📂 PDFast 서비스 소개

![파이널-프로젝트-001](https://github.com/user-attachments/assets/b6ceb105-2b41-4101-b510-ac062fe5c130)

![파이널-프로젝트-004](https://github.com/user-attachments/assets/4ec19ea5-4540-4606-8ef0-fc35691e852e)


<br/>
<br/>

## 🎥 시연 영상

|<img width="1000" src="https://github.com/user-attachments/assets/6d27a6c6-caf8-4071-974c-54c735fe1d0f">|
| :---: |
|PDF 문서를 통한 학습 보조 웹 플랫폼|

<br/>
<br/>

## ✅ 추진 배경


![파이널-프로젝트-005](https://github.com/user-attachments/assets/4c7d0043-7651-4d3c-b1f0-294b8818998d)


# 👥 팀원 소개

| <img width="250" alt="hj" src="https://github.com/user-attachments/assets/c0af7daa-f81b-4527-b62b-f9ee8d23e311"> | <img width="250" alt="yj" src="https://github.com/user-attachments/assets/bee1516f-d25d-46af-8cee-2771a4d9c917"> | <img width="250" alt="jh" src="https://github.com/user-attachments/assets/0c08e694-5ca3-446a-8af9-e7441b83553f"> |
| --- | --- | --- |
| 🐼[정현주](https://github.com/wjdguswn1203)🐼 | 🐱[송윤주](https://github.com/raminicano)🐱 | 🐶[신지현](https://github.com/sinzng)🐶 |


<br/>
<br/>
<br/>


# ⚒ 전체 아키텍처

![파이널-프로젝트-008](https://github.com/user-attachments/assets/da29e426-b752-4f92-98ef-833580c38298)

<br/>
<br/>

# 📝 기능 소개

| <img width="180" alt="search" src="https://github.com/user-attachments/assets/15222799-5fbf-414c-a28a-dfc08e8c5fcb"> | <img width="180" alt="chat" src="https://github.com/user-attachments/assets/8e43aa56-1b01-47e7-a1df-5cfd6ada664e"> | <img width="180" alt="keyword" src="https://github.com/user-attachments/assets/c0e05de1-3884-46c2-a94e-d6835e13622e"> | <img width="180" alt="googlesearch" src="https://github.com/user-attachments/assets/62b99c0d-97a3-49a3-a7fd-b500efb0b138"> | <img width="180" alt="translate" src="https://github.com/user-attachments/assets/27517df2-49f8-495c-beea-a8bf51353d28"> |
| --- | --- | --- | --- | --- |
| ArxivAPI 논문 검색 | GoogleCloudVision, OpenAI 챗봇 | TextRazor, WikipediaAPI 키워드 추출 | GoogleCustomSearch 구글 검색 | DeepL 번역 |


<br/>
<br/>


# 🏆 기술 스택
## Programming language

<img width="45" alt="python" src="https://github.com/user-attachments/assets/2ef3dc8e-0cec-4f54-afc6-6ca237f3ccbc"> 
<br/>


## Library & Framework

<img width="60" alt="fastapi" src="https://github.com/user-attachments/assets/d2216e87-0dd1-438e-95d8-46aad12ae240"> 
<br/>


## Database

<img width="45" alt="s3" src="https://github.com/user-attachments/assets/53249fab-04e0-41e8-845b-ae75ce3b33d8"> <img width="50" alt="mongodb" src="https://github.com/user-attachments/assets/bb0d8cf9-01db-4f61-befa-53f1f384f835"> <img width="50" alt="weaviate" src="https://github.com/user-attachments/assets/3c8bd45b-74d8-420a-aa8b-8726f9ed0e9e"> 
<br/>


## Version Control System

<img width="50" alt="github" src="https://github.com/user-attachments/assets/2e05133c-088b-4494-ae2c-2947e7b96c9f"> 
<br/>


## Communication Tool

<img width="50" alt="kakao" src="https://github.com/user-attachments/assets/4dbeeaba-c7ca-4316-8569-b58ebb18a4fc"> <img width="50" alt="notion" src="https://github.com/user-attachments/assets/3b7dda7e-909a-41a5-90f9-7058c35b41dd"> 


<br/>
<br/>
<br/>


# Repo
메인 fast-api repo입니다.
<br/>
<br/>

# 디렉토리 설명

```
MainFastAPI/
├── .github/
├── .venv/
├── app/
│   ├── api/
│   │   ├── chatbot/
│   │   ├── ocr/
│   │   ├── paper/
│   │   ├── keyword/
│   │   ├── sentence/
│   │   ├── trans/
│   │   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connect_db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── create_paper.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── paper.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── paper_service.py
│   ├── main.py
│   ├── __init__.py
├── tests/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
```

## app/api
- `chatbot` : 챗봇 관련 API 엔드포인트 정의
- `ocr` : ocr 관련 API 엔드포인트 정의
- `paper` : 논문 검색 등 API 엔드포인트 정의
- `keyword` : 키워드 기능 관련 API 엔드 포인트 정의
- `sentence` : 문장 기능 관련 API 엔드 포인트 정의
- `trans` : 번역 관련 API 엔드포인트 정의
- `__init__.py`: API 디렉토리 패키지 초기화 파일

## api/core
- `config.py`: 애플리케이션 설정 및 환경 변수를 관리합니다.
- `__init__.py`: Core 디렉토리 패키지 초기화 파일입니다.

## app/db
- `connect_db.py`: Weaviate 데이터베이스와의 연결을 설정하고 관리하는 파일입니다.
- `__init__.py`: DB 디렉토리 패키지 초기화 파일입니다.

## app/models
- `create_paper.py`: 논문 모델을 정의하는 파일입니다.
- `__init__.py`: Models 디렉토리 패키지 초기화 파일입니다.

## app/schemas
- `paper.py`: Pydantic 스키마를 정의하여 데이터 유효성 검사를 수행합니다.
- `__init__.py`: Schemas 디렉토리 패키지 초기화 파일입니다.

## app/services
- `paper_service.py`: 논문 관련 비즈니스 로직을 처리하는 서비스 레이어입니다.
- `__init__.py`: Services 디렉토리 패키지 초기화 파일입니다.


## app/main.py
FastAPI 애플리케이션을 초기화하고 라우터를 포함하는 메인 파일입니다.

## tests
테스트 코드를 포함하는 디렉토리입니다.
