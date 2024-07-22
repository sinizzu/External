# 베이스 이미지 선택
FROM python:3.9-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
# 시스템 패키지 설치
RUN apt-get update \
    && apt-get install -y build-essential
RUN pip install --upgrade pip
RUN sudo apt-get install poppler-utils


# 애플리케이션 코드 복사
COPY app/ /app/app/
COPY ocr_key.json /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# uvicorn을 사용하여 FastAPI 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
