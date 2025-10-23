# 브라우저 캐시 문제 해결 가이드

## 🎯 문제 상황

**브라우저가 여전히 `localhost:3002`로 API 호출을 시도하는 문제**

### ✅ 해결된 부분
- **API 엔드포인트**: 모든 API가 정상 작동
- **서버 배포**: Vercel 배포 완료
- **API_BASE URL**: 올바르게 설정됨

### ❌ 문제가 있는 부분
- **브라우저 캐시**: 이전 버전의 `app.js` 캐시됨
- **JavaScript 캐시**: `localhost:3002` URL이 캐시됨
- **강제 새로고침**: 일반 새로고침으로 해결되지 않음

## 🔧 적용된 해결 방법

### 1. 캐시 버스팅
- **버전 정보 추가**: `v2.0.0` 버전 표시
- **파일 수정**: `app.js` 내용 변경으로 캐시 무효화
- **디버그 로깅**: API URL 로깅 추가

### 2. 디버그 기능 추가
```javascript
// Version: 2.0.0 - Cache busting update
const API_BASE = 'https://insightforge-newsbot.vercel.app';

console.log('📊 시도 데이터 로드 중... (v2.0.0)');
console.log('🔗 API URL:', `${API_BASE}/api/sido`);
```

## 🚀 사용자 해결 방법

### 방법 1: 강제 새로고침
- **Windows**: `Ctrl + F5`
- **Mac**: `Cmd + Shift + R`
- **모든 브라우저**: `Ctrl + Shift + R`

### 방법 2: 개발자 도구 사용
1. **F12** 키로 개발자 도구 열기
2. **Network** 탭 클릭
3. **Disable cache** 체크박스 선택
4. **새로고침** 버튼 클릭

### 방법 3: 시크릿 모드
- **Chrome**: `Ctrl + Shift + N`
- **Firefox**: `Ctrl + Shift + P`
- **Edge**: `Ctrl + Shift + N`

### 방법 4: 브라우저 캐시 완전 삭제
1. **설정** → **개인정보 보호 및 보안**
2. **인터넷 사용 기록 삭제**
3. **캐시된 이미지 및 파일** 선택
4. **삭제** 버튼 클릭

## 🌐 테스트 URL

**웹사이트:**
- https://insightforge-newsbot.vercel.app/
- https://insightforge-newsbot.vercel.app/landing.html
- https://insightforge-newsbot.vercel.app/dashboard.html

**API 엔드포인트:**
- https://insightforge-newsbot.vercel.app/api/health
- https://insightforge-newsbot.vercel.app/api/sido
- https://insightforge-newsbot.vercel.app/api/politicians
- https://insightforge-newsbot.vercel.app/api/lda

## 📊 확인 방법

### 개발자 도구 콘솔에서 확인
1. **F12** 키로 개발자 도구 열기
2. **Console** 탭 클릭
3. 다음 메시지 확인:
   - `📊 시도 데이터 로드 중... (v2.0.0)`
   - `🔗 API URL: https://insightforge-newsbot.vercel.app/api/sido`
   - `✅ 시도 데이터 로드 완료: 17개`

### Network 탭에서 확인
1. **Network** 탭 클릭
2. **새로고침** 버튼 클릭
3. API 호출이 `https://insightforge-newsbot.vercel.app/api/sido`로 가는지 확인

## 🎯 최종 확인

**정상 작동 시 나타나는 현상:**
- ✅ 콘솔에 `v2.0.0` 버전 표시
- ✅ API URL이 `https://insightforge-newsbot.vercel.app`로 표시
- ✅ 시도 데이터 로드 성공 메시지
- ✅ 웹사이트에 시도 목록 표시

**🎉 이제 모든 기능이 정상적으로 작동할 것입니다!**
