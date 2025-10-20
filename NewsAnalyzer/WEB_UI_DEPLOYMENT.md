# 🌐 Synology 웹 UI 배포 가이드 (SSH 없이)

## 📍 연결 정보
- **IP**: 192.168.219.2
- **웹 주소**: http://192.168.219.2:5000
- **계정**: btf_admin
- **비밀번호**: Ks12121212

---

## 🚀 **배포 단계 (15분)**

### ✅ Step 1: 웹 브라우저에서 DSM 접속

1. 브라우저 주소창에 입력:
   ```
   http://192.168.219.2:5000
   ```

2. 로그인:
   - 사용자: `btf_admin`
   - 비밀번호: `Ks12121212`

---

### ✅ Step 2: File Station에 파일 업로드

1. **File Station** 앱 클릭

2. 좌측 트리에서 경로 이동:
   - `docker` 폴더 (없으면 생성)

3. **업로드** 버튼 클릭

4. 파일 선택:
   ```
   /Users/hopidad/Desktop/workspace/NewsAnalyzer/newsanalyzer.tar.gz
   ```

5. 업로드 완료 대기 (2.2MB, 수 초 소요)

---

### ✅ Step 3: SSH 활성화

1. **제어판** 열기

2. **터미널 및 SNMP** 클릭

3. **터미널** 탭:
   - ☑️ **SSH 서비스 활성화** 체크
   - 포트: `22` (기본값)
   - **적용** 클릭

4. **고급 설정** 클릭:
   - `btf_admin` 계정에 SSH 권한 부여
   - **확인**

---

### ✅ Step 4: 터미널에서 설치

SSH 활성화 후, 로컬 터미널에서:

```bash
# SSH 접속
ssh btf_admin@192.168.219.2
# 비밀번호: Ks12121212

# Synology에서 실행
cd /volume1/docker
tar -xzf newsanalyzer.tar.gz
cd newsanalyzer

# 환경 설정
cat > .env << 'EOF'
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
COLLECTION_MODE=historical
EOF

# Docker 설치 확인
which docker
which docker-compose

# Docker Compose 버전에 따라 선택
# V2 (권장)
sudo docker compose build newsanalyzer-historical
sudo docker compose up -d newsanalyzer-historical

# 또는 V1
# sudo docker-compose build newsanalyzer-historical
# sudo docker-compose up -d newsanalyzer-historical

# 로그 확인
sudo docker compose logs -f newsanalyzer-historical
```

---

### ✅ Step 5: Container Manager에서 확인 (선택)

1. **Container Manager** 앱 열기

2. **컨테이너** 탭

3. `newsanalyzer-historical` 찾기

4. 상태 확인:
   - ✅ 실행 중 (초록색)
   - 📊 CPU/메모리 사용량
   - 📝 로그 보기

---

## 🔄 **Cron 스케줄 설정 (매일 자동 실행)**

### DSM 작업 스케줄러

1. **제어판** → **작업 스케줄러**

2. **생성** → **예약된 작업** → **사용자 정의 스크립트**

3. **일반** 탭:
   - 작업 이름: `NewsAnalyzer Historical Collection`
   - 사용자: `root`
   - ☑️ 활성화

4. **스케줄** 탭:
   - 실행 날짜: **매일**
   - 처음 실행 시간: `02:00` (새벽 2시)
   - 빈도: **매일**

5. **작업 설정** 탭 - 사용자 정의 스크립트:
   ```bash
   cd /volume1/docker/newsanalyzer
   docker compose restart newsanalyzer-historical
   ```

6. **확인** 클릭

---

## 📊 **모니터링**

### 진행 상황 확인 (SSH 접속 후)
```bash
# 수집 상태
cat /volume1/docker/newsanalyzer/data/collection_state.json

# 예시:
# {
#   "current_phase": 1,
#   "current_date": "2020-01-15",
#   "completed_dates": ["2020-01-01", ..., "2020-01-14"],
#   "total_api_calls_today": 15420
# }
```

### Container Manager에서
- 컨테이너 선택
- **세부 정보** → **로그** 탭
- 실시간 로그 확인

---

## 🎯 **지금 해야 할 일**

1. ✅ **DSM 접속**: http://192.168.219.2:5000
2. ✅ **제어판** → **터미널 및 SNMP** → SSH 활성화
3. ✅ **File Station**에 `newsanalyzer.tar.gz` 업로드
4. ✅ 터미널에서 설치 명령어 실행

---

**SSH 활성화만 해주시면 나머지는 5분 안에 자동으로 완료됩니다!** 🚀
