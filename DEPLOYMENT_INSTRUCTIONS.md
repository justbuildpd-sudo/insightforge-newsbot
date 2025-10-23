# newsbot.kr 배포 가이드

## 🚀 GitHub 푸시 완료

✅ **GitHub에 성공적으로 푸시되었습니다!**
- Repository: `justbuildpd-sudo/insightforge-newsbot`
- Commit: `97668d4` - "newsbot.kr 배포 준비 완료 - Node.js API 서버 및 누락된 기능 추가"

## 🌐 Vercel 배포 방법

### 1. Vercel 웹 대시보드에서 배포

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard
   - GitHub 계정으로 로그인

2. **새 프로젝트 생성**
   - "New Project" 클릭
   - GitHub 저장소 선택: `justbuildpd-sudo/insightforge-newsbot`
   - "Import" 클릭

3. **프로젝트 설정**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (기본값)
   - **Build Command**: `npm install` (Node.js 의존성 설치)
   - **Output Directory**: `public` (정적 파일)

4. **환경 변수 설정**
   ```
   NODE_ENV=production
   API_BASE=https://newsbot.kr
   ```

5. **배포 실행**
   - "Deploy" 클릭
   - 배포 완료까지 대기 (약 2-3분)

### 2. 도메인 연결

1. **커스텀 도메인 추가**
   - 프로젝트 설정 → Domains
   - "Add Domain" 클릭
   - 도메인 입력: `newsbot.kr`

2. **DNS 설정**
   - 도메인 제공업체에서 DNS 레코드 설정
   - Vercel에서 제공하는 DNS 정보 사용

## 📊 배포 후 URL

- **메인 페이지**: https://newsbot.kr/
- **랜딩 페이지**: https://newsbot.kr/landing.html
- **대시보드**: https://newsbot.kr/dashboard.html
- **API 상태**: https://newsbot.kr/api/health

## 🎯 주요 기능

### 1. 랜딩 페이지
- 회사 소개 (컨텍스트)
- 모토: "정치에 대한 데이터의 편견"
- 로그인/회원가입 시스템
- 연락처: justbuild.pd@gmail.com

### 2. 대시보드 (ContextCHECKER)
- 정치인 인사이트 분석
- LDA 토픽 모델링 결과
- 지역 데이터 분석
- 관리자 전용 기능

### 3. API 엔드포인트
- `/api/health` - 서버 상태
- `/api/sido` - 시도 목록
- `/api/sido/:name` - 시도별 데이터
- `/api/politicians` - 정치인 목록
- `/api/lda` - LDA 분석 결과
- `/api/news` - 뉴스 데이터
- `/api/analysis` - 분석 결과
- `/api/trends` - 트렌드 데이터
- `/api/statistics` - 통계 데이터
- `/api/contextchecker` - ContextCHECKER

## 🔧 기술 스택

- **Backend**: Node.js (Express) + Python (Flask)
- **Frontend**: HTML/CSS/JavaScript (D3.js)
- **Deployment**: Vercel
- **Data**: JSON (gzip 압축)
- **Caching**: In-memory cache

## 📁 프로젝트 구조

```
/Users/hopidad/Desktop/workspace/
├── api/
│   └── index.js          # Node.js API 서버
├── public/
│   ├── index.html        # 메인 페이지
│   ├── landing.html      # 랜딩 페이지
│   ├── dashboard.html    # 대시보드
│   └── app.js           # 프론트엔드 JS
├── data/
│   ├── politicians_sample.json
│   ├── lda_results_sample.json
│   └── ...
├── app.py               # Python Flask 서버
├── vercel.json          # Vercel 설정
├── package.json         # Node.js 의존성
└── requirements.txt     # Python 의존성
```

## ✅ 배포 체크리스트

- [x] GitHub에 코드 푸시 완료
- [x] Node.js API 서버 구성
- [x] Python Flask 서버 구성
- [x] 누락된 기능 추가
- [x] Vercel 설정 파일 준비
- [ ] Vercel 웹 대시보드에서 배포
- [ ] 도메인 연결 (newsbot.kr)
- [ ] 기능 테스트

## 🎉 다음 단계

1. **Vercel 대시보드에서 배포**
2. **도메인 연결**
3. **기능 테스트**
4. **성능 최적화**

**🌐 최종 URL: https://newsbot.kr**
