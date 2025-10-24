# Vercel 배포 단계별 가이드

## 🔍 기존 프로젝트 확인

### 1. Vercel 대시보드에서 기존 프로젝트 확인
1. **Vercel 대시보드 접속**: https://vercel.com/dashboard
2. **프로젝트 목록 확인**: `justbuildpd-sudo/insightforge-newsbot` 프로젝트가 있는지 확인
3. **기존 프로젝트 상태**: 
   - 활성화된 프로젝트가 있다면 → **업데이트**
   - 없다면 → **새 프로젝트 생성**

## 🚀 단계별 배포 방법

### **Step 1: Vercel 대시보드 접속**
1. https://vercel.com/dashboard 접속
2. GitHub 계정으로 로그인
3. "New Project" 또는 기존 프로젝트 확인

### **Step 2: GitHub 저장소 연결**
1. **새 프로젝트인 경우**:
   - "Import Git Repository" 클릭
   - `justbuildpd-sudo/insightforge-newsbot` 선택
   - "Import" 클릭

2. **기존 프로젝트인 경우**:
   - 기존 프로젝트 클릭
   - "Settings" → "Git" 탭
   - "Redeploy" 또는 "Deploy" 클릭

### **Step 3: 프로젝트 설정**
1. **Framework Preset**: `Other` 선택
2. **Root Directory**: `./` (기본값)
3. **Build Command**: `npm install` (Node.js 의존성 설치)
4. **Output Directory**: `public` (정적 파일)
5. **Install Command**: `npm install` (자동으로 설정됨)

### **Step 4: 환경 변수 설정**
1. **Settings** → **Environment Variables** 탭
2. 다음 환경 변수 추가:
   ```
   NODE_ENV=production
   API_BASE=https://newsbot.kr
   PYTHON_VERSION=3.9
   ```

### **Step 5: 배포 실행**
1. **"Deploy"** 버튼 클릭
2. 배포 진행 상황 모니터링 (약 2-3분)
3. 배포 완료 후 URL 확인

## 🔧 기존 프로젝트 처리 방법

### **Case 1: 기존 프로젝트가 있는 경우**

#### A. 기존 프로젝트 업데이트
```bash
# 로컬에서 변경사항 확인
git status
git add .
git commit -m "Update newsbot.kr with new features"
git push origin main
```

**Vercel에서**:
1. 프로젝트 대시보드에서 "Redeploy" 클릭
2. 또는 자동 배포가 활성화되어 있다면 자동으로 배포됨

#### B. 기존 프로젝트 삭제 후 새로 생성
1. **기존 프로젝트 삭제**:
   - 프로젝트 설정 → "Delete Project" 클릭
   - 확인 후 삭제

2. **새 프로젝트 생성**:
   - "New Project" 클릭
   - GitHub 저장소 연결
   - 설정 후 배포

### **Case 2: 기존 프로젝트가 없는 경우**

#### 새 프로젝트 생성
1. **"New Project"** 클릭
2. **GitHub 저장소 선택**: `justbuildpd-sudo/insightforge-newsbot`
3. **프로젝트 설정**:
   - Name: `newsbot-kr`
   - Framework: `Other`
   - Root Directory: `./`
   - Build Command: `npm install`
   - Output Directory: `public`

## 🌐 도메인 연결

### **Step 1: 커스텀 도메인 추가**
1. **프로젝트 설정** → **Domains** 탭
2. **"Add Domain"** 클릭
3. **도메인 입력**: `newsbot.kr`
4. **"Add"** 클릭

### **Step 2: DNS 설정**
1. **도메인 제공업체에서 DNS 레코드 설정**:
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   
   Type: CNAME  
   Name: www
   Value: cname.vercel-dns.com
   ```

2. **Vercel에서 DNS 확인**:
   - 도메인 설정에서 "Verify" 클릭
   - DNS 전파 대기 (최대 24시간)

## 📊 배포 후 확인

### **Step 1: 기본 페이지 확인**
- **메인 페이지**: https://newsbot.kr/
- **랜딩 페이지**: https://newsbot.kr/landing.html
- **대시보드**: https://newsbot.kr/dashboard.html

### **Step 2: API 엔드포인트 확인**
- **API 상태**: https://newsbot.kr/api/health
- **시도 목록**: https://newsbot.kr/api/sido
- **정치인 목록**: https://newsbot.kr/api/politicians
- **LDA 분석**: https://newsbot.kr/api/lda

### **Step 3: 기능 테스트**
1. **랜딩 페이지**: 회사 소개, 로그인/회원가입
2. **대시보드**: ContextCHECKER 기능
3. **API**: 데이터 로딩 및 응답 확인

## 🔧 문제 해결

### **배포 실패 시**
1. **로그 확인**: Vercel 대시보드 → "Functions" 탭
2. **에러 메시지 확인**: 빌드 로그에서 오류 확인
3. **설정 재확인**: vercel.json, package.json 설정

### **도메인 연결 실패 시**
1. **DNS 설정 확인**: 도메인 제공업체에서 CNAME 설정
2. **전파 대기**: DNS 변경 후 최대 24시간 소요
3. **Vercel DNS 사용**: Vercel에서 제공하는 DNS 서버 사용

### **API 오류 시**
1. **환경 변수 확인**: Settings → Environment Variables
2. **함수 로그 확인**: Functions 탭에서 로그 확인
3. **로컬 테스트**: 로컬에서 API 동작 확인

## 📋 체크리스트

### **배포 전**
- [ ] GitHub 저장소 최신 상태 확인
- [ ] vercel.json 설정 확인
- [ ] package.json 의존성 확인
- [ ] 환경 변수 준비

### **배포 중**
- [ ] Vercel 대시보드에서 배포 진행 상황 모니터링
- [ ] 빌드 로그 확인
- [ ] 오류 발생 시 로그 분석

### **배포 후**
- [ ] 기본 페이지 접속 확인
- [ ] API 엔드포인트 테스트
- [ ] 도메인 연결 확인
- [ ] 기능 테스트 완료

## 🎯 예상 결과

**성공적인 배포 후**:
- **메인 URL**: https://newsbot.kr/
- **랜딩 페이지**: https://newsbot.kr/landing.html
- **대시보드**: https://newsbot.kr/dashboard.html
- **API 상태**: https://newsbot.kr/api/health

**주요 기능**:
- ✅ 회사 소개 (컨텍스트)
- ✅ ContextCHECKER 기능
- ✅ 정치인 분석 및 LDA 토픽 모델링
- ✅ 지역 데이터 분석
- ✅ 뉴스 수집 및 분석
- ✅ 트렌드 분석 및 통계

**🚀 이제 Vercel 대시보드에서 배포를 시작하세요!**
