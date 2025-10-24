# ⏸️ Synology 배포 작업 홀드

## 📅 날짜: 2025년 10월 21일 00:30

---

## ✅ **완료된 작업**

### 로컬 준비 (100%)
- ✅ 4,135명 정치인 목록 생성
- ✅ Phase별 분할 (4개 Phase)
- ✅ `historical_collector.py` 스크립트 작성
- ✅ Docker 설정 (Dockerfile, docker-compose.yml)
- ✅ `.env` 파일 템플릿
- ✅ 배포 스크립트 (`deploy_to_synology.sh`)
- ✅ GitHub push 완료 (commit 040530b)

### Synology 준비 (95%)
- ✅ Synology 정보 확인: `192.168.219.2:5000`
- ✅ SSH 포트 열림 확인 (port 22)
- ✅ 계정: `btf_admin` / 비밀번호: `D9BXMAZIaIbwtQW`
- ✅ Git clone 완료: `/volume1/BTF-Tech/newsanalyzer-temp`
- ✅ 최신 코드 pull 완료 (commit 040530b)
- ✅ `.env` 파일 생성 완료
- ⏸️ Docker 빌드: 홀드 (sudo 권한 이슈)

---

## 🔧 **남은 작업**

### Container Manager GUI로 완료 (권장)
1. Synology DSM 접속: http://192.168.219.2:5000
2. Container Manager 앱 열기
3. 프로젝트 생성:
   - 이름: `newsanalyzer`
   - 경로: `/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
   - 소스: `docker-compose.yml`
4. 환경변수 설정:
   ```
   COLLECTION_MODE=historical
   NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
   NAVER_CLIENT_SECRET=uO5mu7UQBg
   ```
5. 빌드 및 시작

### 또는 SSH로 완료
```bash
ssh btf_admin@192.168.219.2
# 비밀번호: D9BXMAZIaIbwtQW

cd /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer
sudo docker compose build newsanalyzer-historical
# sudo 비밀번호: 1162916

sudo docker compose up -d newsanalyzer-historical
sudo docker compose logs -f newsanalyzer-historical
```

---

## 📊 **수집 계획**

### Phase 1: 2020-2025 (우선)
- **대상**: 1,409명
- **기간**: 2,120일
- **예상 소요**: 67일
- **완료 예정**: 2025-12-27

### Phase 2-4: 2008-2019
- **대상**: 3,368명
- **기간**: 4,382일
- **예상 소요**: 188일
- **완료 예정**: 2026-07-06

### 전체
- **총 정치인**: 4,135명
- **총 기간**: 6,502일 (2008-2025)
- **총 소요**: 255일 (약 8.5개월)
- **API 호출**: 일일 25,000건 제한 준수

---

## 📁 **파일 위치**

### Synology
```
/volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/
├── .env (생성 완료)
├── docker-compose.yml
├── Dockerfile
├── scripts/
│   └── historical_collector.py
└── data/
    ├── historical_politicians.json (4,135명)
    ├── phase1_politicians.json (1,409명)
    ├── phase2_politicians.json (1,120명)
    ├── phase3_politicians.json (1,128명)
    └── phase4_politicians.json (1,119명)
```

### 로컬
```
/Users/hopidad/Desktop/workspace/NewsAnalyzer/
├── newsanalyzer.tar.gz (2.2MB, 백업용)
└── (모든 소스 파일)
```

---

## 🔐 **인증 정보**

### SSH
- IP: `192.168.219.2`
- Port: `22`
- 사용자: `btf_admin`
- 비밀번호: `D9BXMAZIaIbwtQW`

### sudo
- 비밀번호: `1162916` (expect 스크립트에서 인식 안 됨 - 수동 입력 필요)

### Naver API
- Client ID: `ULDLTGiPvrrPBgbuydSm`
- Client Secret: `uO5mu7UQBg`

---

## 🎯 **재개 시 진행 방법**

### 즉시 재개 (Container Manager GUI)
1. http://192.168.219.2:5000 접속
2. Container Manager → 프로젝트 생성
3. 경로: `/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
4. 환경변수 설정 → 빌드 → 시작

### 즉시 재개 (SSH)
```bash
ssh btf_admin@192.168.219.2
cd /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer
sudo docker compose build newsanalyzer-historical
# sudo 비밀번호 입력: 1162916
sudo docker compose up -d newsanalyzer-historical
```

---

## 📝 **작업 홀드 사유**
- sudo 비밀번호 자동 입력 이슈
- Container Manager GUI 작업 대기 중

---

**작성일**: 2025-10-21 00:30 KST  
**상태**: ⏸️ 홀드 (95% 완료, Docker 빌드만 남음)

