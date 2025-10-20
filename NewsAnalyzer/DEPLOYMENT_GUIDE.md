# NewsAnalyzer 시놀로지 배포 가이드

## 📋 사전 준비

### 1. 시놀로지 설정
- **Container Manager** 설치 (Package Center)
- **Git Server** 설치 (선택사항)
- **SSH 접속** 활성화

### 2. 필요한 파일
- `NewsAnalyzer/` 전체 폴더
- `.env` 파일 (API 키 설정)

## 🚀 배포 단계

### Step 1: 파일 업로드

시놀로지 File Station을 통해 `NewsAnalyzer` 폴더를 업로드:
```
/volume1/docker/NewsAnalyzer/
```

또는 SSH로 rsync:
```bash
rsync -avz NewsAnalyzer/ admin@synology-ip:/volume1/docker/NewsAnalyzer/
```

### Step 2: SSH 접속

```bash
ssh admin@synology-ip
cd /volume1/docker/NewsAnalyzer
```

### Step 3: 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env
nano .env
```

`.env` 파일 내용:
```
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
GITHUB_TOKEN=(GitHub Personal Access Token)
VERCEL_TOKEN=(Vercel Token, 선택사항)
```

### Step 4: Docker 빌드 및 실행

```bash
# 빌드 (최초 1회)
docker-compose build

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f newsanalyzer
```

### Step 5: 상태 확인

```bash
# 컨테이너 상태
docker-compose ps

# 로그 확인
tail -f logs/scheduler.log

# 수집된 데이터 확인
ls -lh data/collected/

# LDA 결과 확인
ls -lh output/lda_results/
```

## 🔧 관리 명령어

### 재시작
```bash
docker-compose restart
```

### 중지
```bash
docker-compose stop
```

### 완전 삭제 후 재시작
```bash
docker-compose down
docker-compose up -d
```

### 수동 실행 (테스트용)
```bash
# 뉴스 수집만
docker-compose exec newsanalyzer python3 scripts/collector.py

# LDA 분석만
docker-compose exec newsanalyzer python3 scripts/lda_analyzer.py

# 업로드만
docker-compose exec newsanalyzer python3 scripts/uploader.py
```

## 📊 데이터 흐름

1. **매일 06:00** - 뉴스 수집
   - 네이버 API 호출
   - `data/collected/news_collected_YYYYMMDD.json` 저장

2. **매일 07:00** - LDA 분석
   - 형태소 분석 (KoNLPy)
   - 토픽 모델링 (Gensim)
   - `output/lda_results/assembly_lda_YYYYMMDD.json` 저장

3. **매일 08:00** - InsightForge 업데이트
   - `../insightforge-web/data/` 복사
   - Git 커밋 및 푸시
   - Vercel 자동 배포

## 🎯 모니터링

### 웹 UI로 확인 (Synology Container Manager)
1. Container Manager 열기
2. `newsanalyzer` 컨테이너 클릭
3. 로그 탭에서 실시간 확인

### 로그 파일
- `logs/scheduler.log` - 스케줄러 로그
- `logs/collector.log` - 수집 로그 (자동 생성)
- `logs/analyzer.log` - 분석 로그 (자동 생성)

## ⚠️ 문제 해결

### 1. 컨테이너가 시작 안 됨
```bash
docker-compose logs newsanalyzer
```

### 2. 뉴스 수집 실패
- `.env` 파일의 API 키 확인
- 네이버 API 할당량 확인

### 3. LDA 분석 느림
- `config.json`에서 `passes`, `iterations` 줄이기
- 정치인 수 줄이기

### 4. Git 푸시 실패
- GitHub Token 권한 확인
- 수동 푸시 필요

## 🔄 업데이트

### 코드 업데이트
```bash
# 새 코드 업로드 후
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 설정 변경
```bash
# config.json 수정 후
docker-compose restart
```

## 📈 성능

- **수집 속도**: 약 795명 × 100개 = 79,500개 기사 (약 2-3시간)
- **분석 속도**: 약 795명 × 5개 토픽 (약 1-2시간)
- **디스크 사용**: 약 50MB/일 (압축 시 5MB)

## 🎯 권장 설정

### 시놀로지 사양
- **CPU**: 4코어 이상
- **메모리**: 8GB 이상
- **디스크**: 50GB 이상 여유공간

### Docker 리소스
- **메모리**: 4GB
- **CPU**: 2코어

---
생성일: 2025-10-20
버전: 1.0

