# 저녁 배포 체크리스트 ✅

## 🎯 오늘 저녁 작업 목표
**NewsAnalyzer**를 시놀로지에 배포하여 매일 자동으로 정치인 뉴스를 수집하고 LDA 분석을 수행

## 📦 준비 완료 항목

### 1. 파일 준비 ✅
- ✅ `NewsAnalyzer_20251020_122709.tar.gz` (21KB)
- ✅ 496명 정치인 목록 (`data/politicians.json`)
- ✅ 설정 파일 (`config.json`)
- ✅ Docker 설정 (`docker-compose.yml`, `Dockerfile`)

### 2. 스크립트 준비 ✅
- ✅ `collector.py` - 뉴스 수집
- ✅ `lda_analyzer.py` - LDA 분석
- ✅ `uploader.py` - InsightForge 업데이트
- ✅ `scheduler.py` - 자동 스케줄러

### 3. 문서 준비 ✅
- ✅ `README.md` - 서비스 개요
- ✅ `DEPLOYMENT_GUIDE.md` - 배포 가이드
- ✅ `OPERATION_PLAN.md` - 운영 계획

## 🚀 저녁 배포 단계 (30분 소요)

### Step 1: 시놀로지 파일 업로드 (5분)
```bash
# 방법 A: File Station (추천)
1. 시놀로지 DSM 접속 (http://synology-ip:5000)
2. File Station 열기
3. docker 폴더로 이동
4. NewsAnalyzer_20251020_122709.tar.gz 업로드

# 방법 B: rsync (터미널)
cd /Users/hopidad/Desktop/workspace
rsync -avz --progress NewsAnalyzer_20251020_122709.tar.gz admin@SYNOLOGY_IP:/volume1/docker/
```

### Step 2: SSH 접속 및 압축 해제 (2분)
```bash
# SSH 접속
ssh admin@SYNOLOGY_IP

# 압축 해제
cd /volume1/docker
tar -xzf NewsAnalyzer_20251020_122709.tar.gz
cd NewsAnalyzer
ls -la  # 파일 확인
```

### Step 3: 환경변수 설정 (3분)
```bash
# .env 파일 생성
cp .env.example .env
nano .env

# 아래 내용 입력:
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
GITHUB_TOKEN=(GitHub 토큰 - 선택사항)

# 저장: Ctrl+O, Enter, Ctrl+X
```

### Step 4: Docker 빌드 (10분)
```bash
# 빌드 (처음에만 오래 걸림)
docker-compose build

# 예상 시간: 5-10분 (KoNLPy, Gensim 설치)
```

### Step 5: 실행 및 확인 (5분)
```bash
# 백그라운드 실행
docker-compose up -d

# 상태 확인
docker-compose ps

# 로그 확인 (Ctrl+C로 종료)
docker-compose logs -f newsanalyzer

# 정상 작동 확인:
# "NewsAnalyzer 스케줄러 시작" 메시지 확인
# "⏰ 스케줄 등록" 메시지 확인
```

### Step 6: 테스트 실행 (5분, 선택사항)
```bash
# 뉴스 수집 즉시 테스트 (소수 정치인)
docker-compose exec newsanalyzer python3 scripts/collector.py

# 결과 확인
docker-compose exec newsanalyzer ls -lh data/collected/
```

## 🎯 배포 후 확인사항

### 즉시 확인
- [ ] 컨테이너 Running 상태
- [ ] 로그에 에러 없음
- [ ] 스케줄 등록 메시지 확인

### 다음날 아침 확인 (자동 실행 후)
- [ ] `data/collected/news_collected_20251021.json` 생성
- [ ] `output/lda_results/assembly_lda_20251021.json` 생성
- [ ] InsightForge 데이터 업데이트 확인
- [ ] https://newsbot.kr 에서 LDA 데이터 표시 확인

## 📊 예상 동작

### 내일 (2025-10-21)
- **06:00** - 496명 뉴스 수집 시작 (2-3시간 소요)
- **07:00** - LDA 분석 시작 (1-2시간 소요)
- **08:00** - InsightForge 업데이트 및 Vercel 배포
- **08:10** - https://newsbot.kr 에 새로운 LDA 데이터 반영

## ⚠️ 주의사항

1. **네이버 API 할당량**: 25,000 calls/day 제한 (현재 ~500 사용)
2. **시놀로지 메모리**: 최소 8GB 권장
3. **첫 실행**: 초기 빌드 시 10-15분 소요
4. **GitHub Token**: 자동 푸시 원할 시 필요

## 🔧 문제 발생 시

### 컨테이너 시작 실패
```bash
docker-compose logs newsanalyzer  # 에러 확인
docker-compose down               # 중지
docker-compose up -d              # 재시작
```

### API 키 오류
```bash
nano .env                         # 키 재확인
docker-compose restart            # 재시작
```

### 메모리 부족
```bash
# config.json 수정 (passes, iterations 줄이기)
nano config.json
docker-compose restart
```

## 📞 지원

문제 발생 시:
1. `logs/scheduler.log` 확인
2. `docker-compose logs` 확인
3. 수동 실행으로 디버깅

---
준비 완료: 2025-10-20 12:27
배포 예정: 2025-10-20 저녁
첫 실행 예상: 2025-10-21 06:00
