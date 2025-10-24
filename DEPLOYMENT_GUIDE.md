# newsbot.kr 배포 가이드

## 🚀 Vercel 배포 방법

### 1. Vercel CLI 설치 (대안)
```bash
npm install -g vercel
# 또는
npx vercel
```

### 2. 프로젝트 설정
```bash
cd /Users/hopidad/Desktop/workspace
vercel login
vercel link
```

### 3. 도메인 설정
```bash
vercel domains add newsbot.kr
vercel domains ls
```

### 4. 배포
```bash
vercel --prod
```

## 📁 프로젝트 구조

```
/Users/hopidad/Desktop/workspace/
├── api/
│   └── index.js          # Vercel Serverless Function
├── public/
│   ├── index.html        # 메인 페이지
│   ├── landing.html      # 랜딩 페이지
│   ├── dashboard.html    # 대시보드
│   └── app.js           # 프론트엔드 JS
├── data/
│   ├── politicians_sample.json
│   ├── lda_results_sample.json
│   └── ...
├── vercel.json           # Vercel 설정
├── package.json          # Node.js 의존성
└── DEPLOYMENT_GUIDE.md   # 이 파일
```

## 🌐 배포된 URL

- **메인 페이지**: https://newsbot.kr/
- **랜딩 페이지**: https://newsbot.kr/landing.html
- **대시보드**: https://newsbot.kr/dashboard.html
- **API 상태**: https://newsbot.kr/api/health

## 🔧 환경 변수

Vercel 대시보드에서 다음 환경 변수 설정:

```
NODE_ENV=production
API_BASE=https://newsbot.kr
```

## 📊 API 엔드포인트

### 기본 API
- `GET /` - 메인 페이지
- `GET /landing.html` - 랜딩 페이지
- `GET /dashboard.html` - 대시보드
- `GET /api/health` - 서버 상태

### 데이터 API
- `GET /api/sido` - 시도 목록
- `GET /api/sido/:name` - 시도별 시군구 데이터
- `GET /api/politicians` - 정치인 목록
- `GET /api/politicians/:id` - 정치인 상세
- `GET /api/lda` - LDA 분석 결과
- `GET /api/lda/topics/:id` - 토픽 상세

## 🎯 주요 기능

### 1. 랜딩 페이지
- 회사 소개 (컨텍스트)
- 모토: "정치에 대한 데이터의 편견"
- 로그인/회원가입 시스템
- 연락처: justbuild.pd@gmail.com

### 2. 대시보드
- ContextCHECKER 기능
- 정치인 인사이트 분석
- LDA 토픽 모델링 결과
- 관리자 전용 기능

### 3. 지역 데이터 분석
- 시도/시군구/동 단계별 선택
- 인구 변화 차트
- D3.js 기반 시각화

## 🔄 배포 후 확인사항

1. **도메인 연결 확인**
   ```bash
   curl https://newsbot.kr/api/health
   ```

2. **페이지 로드 확인**
   - https://newsbot.kr/landing.html
   - https://newsbot.kr/dashboard.html

3. **API 동작 확인**
   - https://newsbot.kr/api/sido
   - https://newsbot.kr/api/politicians

## 🛠️ 문제 해결

### 1. 빌드 오류
```bash
vercel logs
vercel logs --follow
```

### 2. 도메인 연결 문제
```bash
vercel domains ls
vercel domains inspect newsbot.kr
```

### 3. 환경 변수 확인
```bash
vercel env ls
vercel env add NODE_ENV production
```

## 📈 성능 최적화

### 1. 데이터 압축
- gzip 압축 활성화
- JSON 데이터 최적화
- 캐싱 전략 적용

### 2. CDN 활용
- Vercel Edge Network
- 정적 파일 캐싱
- API 응답 캐싱

### 3. 모니터링
- Vercel Analytics
- 실시간 로그 모니터링
- 성능 메트릭 추적

## 🎉 배포 완료 체크리스트

- [ ] Vercel CLI 설치
- [ ] 프로젝트 연결
- [ ] 도메인 설정 (newsbot.kr)
- [ ] 환경 변수 설정
- [ ] 프로덕션 배포
- [ ] 도메인 연결 확인
- [ ] API 동작 확인
- [ ] 페이지 로드 확인
- [ ] 성능 테스트
- [ ] 모니터링 설정

**🌐 최종 URL: https://newsbot.kr**
