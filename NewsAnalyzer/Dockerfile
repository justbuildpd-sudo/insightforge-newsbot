FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (Java 제거 - Kiwipiepy 사용)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kiwipiepy 모델 다운로드 (첫 실행 시 자동)
RUN python -c "from kiwipiepy import Kiwi; kiwi = Kiwi()"

# 애플리케이션 복사
COPY . .

# 디렉토리 생성
RUN mkdir -p logs data/collected output/lda_results output/historical

# 권한 설정
RUN chmod +x scripts/*.py

# 환경변수
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV COLLECTION_MODE=daily

# 실행 모드에 따라 스크립트 선택
# COLLECTION_MODE: daily (일일 수집) | historical (과거 데이터)
CMD if [ "$COLLECTION_MODE" = "historical" ]; then \
        python3 scripts/historical_collector.py; \
    else \
        python3 scripts/scheduler.py; \
    fi

