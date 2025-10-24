# 🚀 Synology 빠른 배포 가이드

## 📍 Synology 정보
- **IP**: 192.168.219.2
- **웹 주소**: http://192.168.219.2:5000
- **SSH 포트**: 22 (열림 확인됨)

---

## 🎯 **2가지 배포 방법**

---

## 방법 1: SSH 터미널 배포 (5분) ⭐ 권장

### Step 1: SSH 접속 테스트
터미널에서 실행:
```bash
ssh admin@192.168.219.2
```

비밀번호 입력 → 접속 성공하면:

### Step 2: 자동 배포 스크립트 실행
```bash
cd /Users/hopidad/Desktop/workspace/NewsAnalyzer
./deploy_to_synology.sh 192.168.219.2
```

**끝!** 스크립트가 자동으로:
- ✅ 파일 패키징
- ✅ 업로드
- ✅ Docker 설치
- ✅ 컨테이너 시작

---

## 방법 2: File Station 수동 배포 (15분)

### Step 1: 파일 준비 완료 ✅
```
📦 newsanalyzer.tar.gz (2.2MB)
   위치: /Users/hopidad/Desktop/workspace/NewsAnalyzer/
```

### Step 2: Synology 웹 접속
1. 브라우저에서 열기: **http://192.168.219.2:5000**
2. 로그인 (admin 계정)

### Step 3: File Station에 업로드
1. **File Station** 앱 열기
2. 좌측에서 **docker** 폴더 클릭 (없으면 생성)
3. **newsanalyzer.tar.gz** 파일을 드래그 앤 드롭 또는 업로드 버튼

### Step 4: SSH로 압축 해제 (터미널)
```bash
# SSH 접속
ssh admin@192.168.219.2

# 비밀번호 입력 후
cd /volume1/docker
tar -xzf newsanalyzer.tar.gz
rm newsanalyzer.tar.gz

# 환경 설정
cd newsanalyzer
cat > .env << 'EOF'
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
EOF

# Docker 시작
sudo docker-compose up -d newsanalyzer-historical

# 로그 확인
sudo docker-compose logs -f newsanalyzer-historical
```

---

## 방법 3: Container Manager GUI (20분)

### Step 1: File Station 업로드 (위와 동일)

### Step 2: 압축 해제
1. File Station에서 **newsanalyzer.tar.gz** 우클릭
2. **압축 풀기** 선택

### Step 3: Container Manager
1. **Container Manager** 앱 열기
2. **프로젝트** 탭
3. **생성** 클릭
4. 다음 정보 입력:
   - 프로젝트 이름: `newsanalyzer`
   - 경로: `/docker/newsanalyzer`
   - 소스: `docker-compose.yml` 업로드
5. **환경** 탭에서 변수 추가:
   ```
   COLLECTION_MODE=historical
   NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
   NAVER_CLIENT_SECRET=uO5mu7UQBg
   ```
6. **적용** → **빌드** → **시작**

---

## ⚡ **가장 빠른 방법: SSH 한 줄**

터미널에서 이것만 실행:
```bash
ssh admin@192.168.219.2
```

비밀번호 입력 후 접속되면:
```bash
# Synology에서 실행
mkdir -p /volume1/docker
exit
```

그 다음 로컬에서:
```bash
cd /Users/hopidad/Desktop/workspace/NewsAnalyzer
scp newsanalyzer.tar.gz admin@192.168.219.2:/volume1/docker/
ssh admin@192.168.219.2 "cd /volume1/docker && tar -xzf newsanalyzer.tar.gz && cd newsanalyzer && echo 'NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm' > .env && echo 'NAVER_CLIENT_SECRET=uO5mu7UQBg' >> .env && sudo docker-compose up -d newsanalyzer-historical"
```

**한 번에 모든 설치 완료!** 🚀

---

## 📊 **배포 후 확인**

### 로그 확인
```bash
ssh admin@192.168.219.2
cd /volume1/docker/newsanalyzer
sudo docker-compose logs -f newsanalyzer-historical
```

### 진행 상황
```bash
cat /volume1/docker/newsanalyzer/data/collection_state.json
```

---

**먼저 SSH 접속 테스트를 해주세요:**
```bash
ssh admin@192.168.219.2
```

접속 성공하시면 나머지는 자동으로 진행하겠습니다! 🎯

