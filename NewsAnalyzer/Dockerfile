FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (KoNLPy 의존성)
RUN apt-get update && apt-get install -y \
    default-jdk \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# KoNLPy 데이터 다운로드
RUN python -c "from konlpy.tag import Okt; Okt()"

# 애플리케이션 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p logs data/collected output/lda_results

# 권한 설정
RUN chmod +x scripts/*.py

# 환경변수
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1

# 기본 명령어 (스케줄러 실행)
CMD ["python3", "scripts/scheduler.py"]

