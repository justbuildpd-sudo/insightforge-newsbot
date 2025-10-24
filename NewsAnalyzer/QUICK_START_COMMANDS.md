# ⚡ Synology 빠른 시작 명령어

## SSH로 바로 시작하기

### 1️⃣ SSH 접속
```bash
ssh btf_admin@192.168.219.2
# 비밀번호: D9BXMAZIaIbwtQW
```

### 2️⃣ 프로젝트 디렉토리 이동
```bash
cd /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer
```

### 3️⃣ 최신 코드 확인 (선택사항)
```bash
git pull origin main
```

### 4️⃣ Docker Compose 실행

#### Option A: Historical 수집만 시작
```bash
sudo docker compose up -d newsanalyzer-historical
# sudo 비밀번호: 1162916
```

#### Option B: Daily 수집만 시작
```bash
sudo docker compose up -d newsanalyzer-daily
```

#### Option C: 둘 다 시작
```bash
sudo docker compose up -d
```

### 5️⃣ 로그 확인
```bash
# Historical 로그
sudo docker compose logs -f newsanalyzer-historical

# Daily 로그
sudo docker compose logs -f newsanalyzer-daily

# 둘 다
sudo docker compose logs -f
```

---

## 📊 컨테이너 관리 명령어

### 상태 확인
```bash
sudo docker compose ps
```

### 중지
```bash
sudo docker compose stop
```

### 재시작
```bash
sudo docker compose restart
```

### 완전 종료 및 삭제
```bash
sudo docker compose down
```

### 재빌드 (코드 변경 시)
```bash
sudo docker compose build
sudo docker compose up -d
```

---

## 🔍 데이터 확인

### 수집된 파일 확인
```bash
ls -lh output/historical/phase1/
```

### 수집 상태 확인
```bash
cat data/collection_state.json
```

### 로그 파일 확인
```bash
tail -f logs/collector.log
```

---

## ⚠️ 문제 해결

### 컨테이너 재시작
```bash
sudo docker compose restart newsanalyzer-historical
```

### 로그 마지막 50줄 확인
```bash
sudo docker compose logs --tail=50 newsanalyzer-historical
```

### 컨테이너 진입 (디버깅)
```bash
sudo docker compose exec newsanalyzer-historical /bin/sh
```

---

## 🎯 한 줄 명령어 모음

```bash
# 빠른 시작
cd /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer && sudo docker compose up -d newsanalyzer-historical

# 빠른 로그 확인
sudo docker compose logs -f newsanalyzer-historical | tail -100

# 빠른 상태 확인
sudo docker compose ps && cat data/collection_state.json

# 빠른 재시작
sudo docker compose restart newsanalyzer-historical && sudo docker compose logs -f newsanalyzer-historical
```

---

**작성**: 2025-10-22  
**목적**: Synology NewsAnalyzer 빠른 배포

