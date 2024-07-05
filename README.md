# 설명
메인 fast-api repo입니다.

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