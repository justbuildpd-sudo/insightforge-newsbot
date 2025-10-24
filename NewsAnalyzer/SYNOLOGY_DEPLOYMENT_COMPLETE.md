# 🖥️ Synology NAS 배포 완전 가이드

## 📅 작성일: 2025년 10월 20일

---

## 🎯 **배포 목적**

### 2개의 독립적인 서비스
1. **Historical Collector** (과거 데이터 수집)
   - 2008-2025년 역사적 뉴스 수집
   - 매일 자동 실행
   - API 제한: 25,000건/일

2. **Daily Analyzer** (일일 분석)
   - 현재 뉴스 수집 + LDA 분석
   - GitHub 자동 업로드
   - Vercel 자동 배포

---

## 📦 **사전 준비**

### Synology NAS 요구사항
- **DSM 버전**: 7.0 이상
- **패키지**:
  - Docker
  - Container Manager
  - Git Server (선택)
- **스토리지**: 최소 50GB 여유 공간
- **메모리**: 최소 4GB RAM

### 로컬에서 준비할 파일
```
NewsAnalyzer/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.json
├── scripts/
│   ├── historical_collector.py
│   ├── collector.py
│   ├── lda_analyzer.py
│   ├── scheduler.py
│   └── uploader.py
└── data/
    ├── historical_politicians.json (4,135명)
    ├── phase1_politicians.json (1,409명)
    ├── phase2_politicians.json (1,120명)
    ├── phase3_politicians.json (1,128명)
    └── phase4_politicians.json (1,119명)
```

---

## 🚀 **배포 단계**

### Step 1: 파일 패키징
```bash
cd /Users/hopidad/Desktop/workspace/NewsAnalyzer

# tar.gz로 압축
tar -czf newsanalyzer.tar.gz \
    Dockerfile \
    docker-compose.yml \
    requirements.txt \
    config.json \
    scripts/ \
    data/

echo "✅ newsanalyzer.tar.gz 생성 완료"
ls -lh newsanalyzer.tar.gz
```

### Step 2: Synology NAS에 업로드

#### 방법 A: File Station (웹 UI)
1. DSM 로그인
2. File Station 열기
3. `/docker/newsanalyzer` 폴더 생성
4. `newsanalyzer.tar.gz` 업로드
5. 압축 해제

#### 방법 B: SSH/SCP (권장)
```bash
# Synology NAS IP 주소 확인 필요
SYNOLOGY_IP="192.168.x.x"
SYNOLOGY_USER="admin"

# SCP로 업로드
scp newsanalyzer.tar.gz ${SYNOLOGY_USER}@${SYNOLOGY_IP}:/volume1/docker/

# SSH 접속
ssh ${SYNOLOGY_USER}@${SYNOLOGY_IP}

# NAS에서 압축 해제
cd /volume1/docker
tar -xzf newsanalyzer.tar.gz
mv NewsAnalyzer newsanalyzer
cd newsanalyzer
```

### Step 3: 환경변수 설정
```bash
# NAS에서 실행
cd /volume1/docker/newsanalyzer

# .env 파일 생성
cat > .env << 'EOF'
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
GITHUB_TOKEN=your_github_token_here
VERCEL_TOKEN=your_vercel_token_here
EOF

chmod 600 .env
```

### Step 4: Docker 이미지 빌드
```bash
# NAS에서 실행
cd /volume1/docker/newsanalyzer

# 이미지 빌드
sudo docker-compose build

# 빌드 확인
sudo docker images | grep newsanalyzer
```

### Step 5: 컨테이너 시작
```bash
# 과거 데이터 수집만 시작
sudo docker-compose up -d newsanalyzer-historical

# 로그 확인
sudo docker-compose logs -f newsanalyzer-historical

# 상태 확인
sudo docker-compose ps
```

---

## ⏰ **Cron 스케줄 설정**

### DSM 작업 스케줄러
1. **제어판** → **작업 스케줄러**
2. **생성** → **예약된 작업** → **사용자 정의 스크립트**
3. **일반** 탭:
   - 작업: `NewsAnalyzer Historical Collection`
   - 사용자: `root`
   - 활성화: ✅
4. **스케줄** 탭:
   - 실행 날짜: **매일**
   - 시간: **새벽 2시**
5. **작업 설정** 탭:
   ```bash
   #!/bin/bash
   cd /volume1/docker/newsanalyzer
   docker-compose restart newsanalyzer-historical
   ```

---

## 📊 **모니터링**

### 로그 확인
```bash
# 실시간 로그
sudo docker-compose logs -f newsanalyzer-historical

# 최근 100줄
sudo docker-compose logs --tail=100 newsanalyzer-historical

# 진행 상황 파일
cat /volume1/docker/newsanalyzer/data/collection_state.json
```

### 수집 진행 상황
```json
{
  "current_phase": 1,
  "current_date": "2020-01-05",
  "total_api_calls_today": 15420,
  "completed_dates": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"],
  "last_run_date": "2025-10-20"
}
```

### 디스크 사용량
```bash
du -sh /volume1/docker/newsanalyzer/output/historical
```

---

## 🔧 **운영 명령어**

### 컨테이너 관리
```bash
# 시작
sudo docker-compose up -d newsanalyzer-historical

# 중지
sudo docker-compose stop newsanalyzer-historical

# 재시작
sudo docker-compose restart newsanalyzer-historical

# 제거
sudo docker-compose down newsanalyzer-historical

# 전체 재시작 (이미지 재빌드 후)
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d
```

### 데이터 백업
```bash
# 주기적 백업 (매주)
cd /volume1/docker/newsanalyzer
tar -czf backup_$(date +%Y%m%d).tar.gz output/ data/

# 백업 디렉토리로 이동
mv backup_*.tar.gz /volume1/backup/newsanalyzer/
```

---

## 📈 **수집 일정 (자동)**

### Phase 1: 2020-2025 (현직)
- **시작**: 2025-10-21
- **종료**: 2025-12-27 (67일 후)
- **대상**: 1,409명 (국회의원 + 현직 지방정치인)
- **일일 수집**: 약 1일치 데이터 (1,409명 x 1일)
- **API 호출**: 약 1,409건/일

### Phase 2: 2016-2019 (21대)
- **시작**: 2025-12-28 (자동 전환)
- **종료**: 2026-02-25 (59일)
- **대상**: 1,120명

### Phase 3: 2012-2015 (20대)
- **시작**: 2026-02-26 (자동 전환)
- **종료**: 2026-04-26 (59일)
- **대상**: 1,128명

### Phase 4: 2008-2011 (18-19대)
- **시작**: 2026-04-27 (자동 전환)
- **종료**: 2026-07-06 (70일)
- **대상**: 1,119명

### 전체 완료
- **예상 완료일**: **2026년 7월 6일**
- **총 소요 기간**: 255일 (약 8.5개월)

---

## 🔔 **알림 설정 (선택)**

### 이메일 알림
```bash
# 매 Phase 완료 시 이메일
# DSM 알림 센터 → 이메일 설정
```

### Telegram 봇 (선택)
```python
# scripts/send_notification.py
import requests

def send_telegram(message):
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    requests.post(url, json={
        'chat_id': chat_id,
        'text': message
    })
```

---

## 💾 **데이터 구조**

### 출력 폴더
```
output/
├── historical/
│   ├── phase1/
│   │   ├── 2020-01/
│   │   │   ├── news_2020-01-01.json
│   │   │   ├── news_2020-01-02.json
│   │   │   └── ...
│   │   ├── 2020-02/
│   │   └── ...
│   ├── phase2/
│   ├── phase3/
│   └── phase4/
│
├── lda_results/
│   └── (매주 LDA 분석 결과)
│
└── state/
    └── collection_progress.json
```

### 월별 압축 (자동)
```bash
# 매월 1일 자동 실행
# 이전 달 데이터 압축
gzip /volume1/docker/newsanalyzer/output/historical/phase1/2020-01/*.json
```

---

## 🐛 **트러블슈팅**

### 문제 1: 컨테이너 시작 실패
```bash
# 로그 확인
sudo docker-compose logs newsanalyzer-historical

# 이미지 재빌드
sudo docker-compose build --no-cache newsanalyzer-historical
```

### 문제 2: API 호출 제한 초과
```bash
# collection_state.json 확인
cat data/collection_state.json

# 수동으로 total_api_calls_today를 0으로 리셋 (다음 날에만)
```

### 문제 3: 디스크 공간 부족
```bash
# 오래된 데이터 압축
find output/historical -name "*.json" -mtime +30 -exec gzip {} \;

# 백업 후 삭제
tar -czf backup_old.tar.gz output/historical/phase1/2020-*
rm -rf output/historical/phase1/2020-01
```

---

## 📞 **Synology NAS 연결 정보**

### SSH 접속
```bash
# 기본 포트: 22
ssh admin@SYNOLOGY_IP

# 사용자 정의 포트인 경우
ssh -p PORT admin@SYNOLOGY_IP
```

### Docker 경로
```
/volume1/docker/newsanalyzer/
```

### Web UI 접속
```
http://SYNOLOGY_IP:5000
```

---

## ✅ **배포 체크리스트**

### 사전 준비
- [ ] Synology NAS에 Docker 설치
- [ ] SSH 접속 활성화
- [ ] 충분한 디스크 공간 (50GB+)

### 파일 준비
- [ ] newsanalyzer.tar.gz 생성
- [ ] Synology에 업로드
- [ ] 압축 해제

### 환경 설정
- [ ] .env 파일 생성
- [ ] Naver API 키 입력
- [ ] GitHub/Vercel 토큰 (선택)

### Docker 실행
- [ ] docker-compose build
- [ ] docker-compose up -d
- [ ] 로그 확인

### 스케줄러 설정
- [ ] DSM 작업 스케줄러 등록
- [ ] 매일 새벽 2시 실행
- [ ] 테스트 실행

### 모니터링
- [ ] 로그 파일 확인
- [ ] collection_state.json 추적
- [ ] 디스크 사용량 모니터링

---

## 🚀 **즉시 시작하기**

### 1️⃣ 로컬에서 패키징
```bash
cd /Users/hopidad/Desktop/workspace/NewsAnalyzer
tar -czf newsanalyzer.tar.gz .
```

### 2️⃣ Synology에 업로드
```bash
# Synology IP 주소 입력 필요
scp newsanalyzer.tar.gz admin@SYNOLOGY_IP:/volume1/docker/
```

### 3️⃣ Synology에서 설치
```bash
ssh admin@SYNOLOGY_IP
cd /volume1/docker
tar -xzf newsanalyzer.tar.gz
cd newsanalyzer

# 환경변수 설정
echo "NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm" > .env
echo "NAVER_CLIENT_SECRET=uO5mu7UQBg" >> .env

# Docker 시작
sudo docker-compose up -d newsanalyzer-historical

# 로그 확인
sudo docker-compose logs -f newsanalyzer-historical
```

---

## 📊 **예상 결과**

### 수집 속도
- **일일 수집**: 1일치 데이터 (약 1,400명)
- **API 호출**: 약 1,400-2,000건/일
- **소요 시간**: 약 5-10분/일
- **디스크 사용**: 약 50-100MB/일

### 8.5개월 후 (255일)
- **총 수집**: 약 6,500일치 데이터
- **정치인**: 4,135명
- **예상 파일**: 약 6,500개 JSON
- **예상 크기**: 약 30-50GB (압축 시 10GB)

---

## 💡 **최적화 팁**

### 1️⃣ API 효율성
- 이미 수집된 날짜는 건너뛰기
- 기사 없는 정치인은 제외
- 중복 체크

### 2️⃣ 스토리지 관리
- 월별 자동 압축 (gzip)
- 6개월 이상 데이터 아카이브
- S3/Glacier로 백업 (선택)

### 3️⃣ 성능 최적화
- SSD 캐시 활용
- Docker 볼륨 최적화
- 메모리 제한 설정

---

## 🎊 **완료 후 활용**

### 1️⃣ 시계열 분석
- 정치인별 언론 노출도 변화
- 주요 이슈 타임라인
- 정당별 트렌드 분석

### 2️⃣ LDA 토픽 변화
- 시기별 주요 토픽
- 정치인별 이슈 변천사
- 선거 전후 비교

### 3️⃣ 네트워크 분석
- 정치인 간 공동 출현
- 이슈 네트워크
- 정당 간 관계 변화

---

**준비 완료! Synology IP 주소만 알려주시면 즉시 배포하겠습니다!** 🚀

