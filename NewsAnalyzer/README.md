# NewsAnalyzer - 정치인 뉴스 수집 및 LDA 분석 시스템

## 📋 개요

정치인 관련 뉴스를 자동 수집하고 LDA(Latent Dirichlet Allocation) 토픽 분석을 수행하여 InsightForge에 업데이트하는 독립 서비스입니다.

## 🏗️ 시스템 구조

```
NewsAnalyzer/
├── config.json              # 설정 파일 (API 키, 정치인 목록 등)
├── requirements.txt         # Python 패키지
├── docker-compose.yml       # 시놀로지 배포용
├── Dockerfile              # Docker 이미지
├── scripts/
│   ├── collector.py        # 뉴스 수집기
│   ├── lda_analyzer.py     # LDA 분석기
│   ├── scheduler.py        # 스케줄러 (매일 실행)
│   └── uploader.py         # InsightForge 업데이트
├── data/
│   ├── politicians.json    # 정치인 목록
│   └── collected/          # 수집된 뉴스
├── output/
│   ├── lda_results/        # LDA 분석 결과
│   └── insightforge/       # InsightForge 업데이트용
└── logs/
    └── analyzer.log        # 로그 파일
```

## 🎯 주요 기능

### 1. 뉴스 수집
- 네이버 뉴스 API 활용
- 국회의원 298명 + 지방정치인 497명
- 매일 자동 수집 (오전 6시)
- 중복 제거 및 정제

### 2. LDA 분석
- 한국어 형태소 분석 (KoNLPy)
- 토픽 모델링 (Gensim)
- 정치인별 주요 관심사 추출
- 키워드 가중치 계산

### 3. 자동 업데이트
- InsightForge 데이터 갱신
- Vercel 배포 자동화
- 변경사항 Git 커밋

## 📦 배포

### 시놀로지 배포
```bash
# Docker 빌드
docker-compose build

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 수동 실행
```bash
# 뉴스 수집
python scripts/collector.py

# LDA 분석
python scripts/lda_analyzer.py

# InsightForge 업데이트
python scripts/uploader.py
```

## ⏰ 스케줄

- **매일 06:00**: 뉴스 수집
- **매일 07:00**: LDA 분석
- **매일 08:00**: InsightForge 업데이트

## 🔧 환경 변수

- `NAVER_CLIENT_ID`: 네이버 API ID
- `NAVER_CLIENT_SECRET`: 네이버 API Secret
- `GITHUB_TOKEN`: GitHub 자동 커밋용
- `VERCEL_TOKEN`: Vercel 자동 배포용

## 📊 출력 데이터

### assembly_member_lda_analysis.json
```json
{
  "정치인이름": {
    "member_info": {
      "name": "이름",
      "party": "정당",
      "district": "지역구"
    },
    "total_count": 100,
    "issues": [
      {
        "category": "주요 토픽",
        "count": 50,
        "top_keywords": [["키워드", 빈도], ...]
      }
    ]
  }
}
```

## 🚀 시작하기

1. 설정 파일 작성: `config.json`
2. 정치인 목록 준비: `data/politicians.json`
3. Docker 빌드 및 실행
4. 로그 모니터링

---
생성일: 2025-10-20
시스템: NewsAnalyzer v1.0

