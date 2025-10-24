# newsbot.kr 문제 해결 가이드

## 🎉 배포 성공 상태

**✅ Vercel 배포 완료:**
- **프로젝트**: insightforge-newsbot
- **기본 URL**: https://insightforge-newsbot.vercel.app
- **커스텀 도메인**: www.newsbot.kr
- **상태**: 배포 성공

## 🔍 가능한 문제점 및 해결 방법

### 1. DNS 전파 지연 (가장 일반적)

**문제**: www.newsbot.kr 접속 불가
**원인**: DNS 설정이 아직 전파되지 않음 (최대 24시간 소요)

**해결 방법**:
1. **Vercel 기본 URL 사용**: https://insightforge-newsbot.vercel.app
2. **DNS 전파 확인**: https://dnschecker.org/
3. **대기**: DNS 전파 완료까지 최대 24시간

### 2. 도메인 설정 문제

**문제**: 도메인 연결 실패
**원인**: DNS 레코드 설정 오류

**해결 방법**:
1. **DNS 설정 확인**:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```
2. **Vercel 대시보드에서 도메인 상태 확인**
3. **DNS 제공업체에서 설정 재확인**

### 3. API 엔드포인트 오류

**문제**: API 응답 실패
**원인**: 함수 호출 오류, 타임아웃, 페이로드 크기 초과

**해결 방법**:
1. **API 상태 확인**: https://insightforge-newsbot.vercel.app/api/health
2. **에러 로그 확인**: Vercel 대시보드 → Functions 탭
3. **페이로드 크기 확인**: 4.5MB 제한

### 4. 정적 파일 로딩 실패

**문제**: HTML/CSS/JS 파일 로딩 실패
**원인**: 라우팅 설정 오류, 파일 경로 문제

**해결 방법**:
1. **정적 파일 경로 확인**: /public/ 폴더
2. **라우팅 설정 확인**: vercel.json
3. **파일 존재 여부 확인**

## 🚀 테스트 방법

### 1. 기본 URL 테스트
```bash
# Vercel 기본 URL로 접속
curl -I https://insightforge-newsbot.vercel.app/
curl -I https://insightforge-newsbot.vercel.app/landing.html
curl -I https://insightforge-newsbot.vercel.app/dashboard.html
```

### 2. API 엔드포인트 테스트
```bash
# API 상태 확인
curl https://insightforge-newsbot.vercel.app/api/health

# 시도 목록 확인
curl https://insightforge-newsbot.vercel.app/api/sido

# 정치인 목록 확인
curl https://insightforge-newsbot.vercel.app/api/politicians
```

### 3. 커스텀 도메인 테스트
```bash
# 커스텀 도메인 확인
curl -I https://www.newsbot.kr/
curl -I https://www.newsbot.kr/landing.html
curl -I https://www.newsbot.kr/dashboard.html
```

## 📊 주요 에러 코드 및 해결 방법

### FUNCTION_INVOCATION_FAILED (500)
**원인**: API 함수 실행 실패
**해결**: 
- 함수 로그 확인
- 의존성 설치 확인
- 메모리 사용량 확인

### NOT_FOUND (404)
**원인**: 요청한 리소스를 찾을 수 없음
**해결**:
- 파일 경로 확인
- 라우팅 설정 확인
- 정적 파일 존재 여부 확인

### DNS_HOSTNAME_NOT_FOUND (502)
**원인**: DNS 해석 실패
**해결**:
- DNS 설정 확인
- 도메인 등록 상태 확인
- DNS 전파 대기

### ROUTER_CANNOT_MATCH (502)
**원인**: 라우팅 매칭 실패
**해결**:
- vercel.json 설정 확인
- 라우팅 규칙 확인
- 경로 매칭 확인

## 🔧 Vercel 대시보드에서 확인할 항목

### 1. 배포 상태
- **Deployments** 탭에서 최신 배포 상태 확인
- **Functions** 탭에서 API 함수 상태 확인
- **Domains** 탭에서 도메인 연결 상태 확인

### 2. 로그 확인
- **Functions** 탭에서 함수 실행 로그 확인
- **Deployments** 탭에서 빌드 로그 확인
- **Analytics** 탭에서 트래픽 분석

### 3. 설정 확인
- **Settings** → **General**에서 프로젝트 설정 확인
- **Settings** → **Environment Variables**에서 환경 변수 확인
- **Settings** → **Domains**에서 도메인 설정 확인

## 🎯 최종 확인 체크리스트

- [ ] Vercel 기본 URL 접속 가능
- [ ] API 엔드포인트 응답 정상
- [ ] 정적 파일 로딩 정상
- [ ] 커스텀 도메인 연결 확인
- [ ] DNS 전파 완료 확인
- [ ] 에러 로그 없음 확인

## 📞 추가 지원

**문제가 지속되는 경우**:
1. Vercel 대시보드에서 로그 확인
2. DNS 설정 재확인
3. 도메인 제공업체에 문의
4. Vercel 지원팀에 문의

**🎉 성공적인 배포를 위해 위의 단계를 순서대로 확인해보세요!**
