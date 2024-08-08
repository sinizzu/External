# 베이스 이미지로 Python 사용
FROM python:3.9.7

# step 2 : Package Install
RUN apt-get update && apt-get -y upgrade && apt-get -y install git net-tools vim

# 작업 디렉토리 설정
WORKDIR /root

# 의존성 설치
RUN mkdir /root/External
WORKDIR /root/External

# 환경 변수로부터 ocr_key.json 파일 생성
ARG OCR_KEY_JSON
RUN echo "$OCR_KEY_JSON" > /root/External/ocr_key.json

# 애플리케이션 코드 복사
COPY app/ ./app/
COPY requirements.txt .

# 가상 환경 생성 및 패키지 설치
RUN python3.9 -m venv .venv
RUN . .venv/bin/activate
RUN pip install -r requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# uvicorn을 사용하여 FastAPI 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
