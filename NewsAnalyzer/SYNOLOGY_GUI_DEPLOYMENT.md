# 🚀 Synology Container Manager GUI 배포 가이드

## 📅 배포 재개: 2025년 10월 22일

---

## ✅ **사전 준비 완료**

### Synology 상태:
- ✅ IP: `192.168.219.2:5000`
- ✅ 계정: `btf_admin` / 비밀번호: `D9BXMAZIaIbwtQW`
- ✅ 경로: `/volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
- ✅ 파일: docker-compose.yml, Dockerfile, .env 모두 존재
- ✅ 데이터: 4,135명 정치인 목록 (Phase 1-4)

---

## 📋 **Container Manager GUI 배포 단계**

### Step 1: Synology DSM 접속
1. 브라우저에서 **http://192.168.219.2:5000** 접속
2. 계정: `btf_admin`
3. 비밀번호: `D9BXMAZIaIbwtQW`
4. 로그인

### Step 2: Container Manager 앱 열기
1. 메인 메뉴에서 **"Container Manager"** 클릭
2. 또는 검색: "Container" 또는 "Docker"

### Step 3: 프로젝트 생성
1. 왼쪽 메뉴에서 **"프로젝트"** 클릭
2. 상단 **"생성"** 버튼 클릭
3. **프로젝트 설정**:
   ```
   프로젝트 이름: newsanalyzer
   경로: /BTF-Tech/newsanalyzer-temp/NewsAnalyzer
   소스: docker-compose.yml 선택
   ```

### Step 4: 환경 변수 설정
**docker-compose.yml 파일 내용 확인 후**, 필요시 환경 변수 추가:

#### 과거 데이터 수집 서비스 (historical)
```env
COLLECTION_MODE=historical
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
```

#### 일일 수집 서비스 (daily)
```env
COLLECTION_MODE=daily
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
```

### Step 5: 서비스 선택
docker-compose.yml에 2개 서비스가 정의되어 있습니다:
- **newsanalyzer-historical**: 과거 데이터 수집 (2008-2025)
- **newsanalyzer-daily**: 일일 뉴스 수집 및 LDA 분석

**권장**: 먼저 `newsanalyzer-historical`만 시작

### Step 6: 빌드 및 시작
1. **"빌드"** 버튼 클릭 (이미지 생성)
   - 예상 소요: 3-5분
   - Python 패키지 설치 중...
2. 빌드 완료 후 **"시작"** 버튼 클릭
3. 상태가 **"실행 중"**으로 변경되는지 확인

### Step 7: 로그 확인
1. 프로젝트에서 **"newsanalyzer-historical"** 컨테이너 클릭
2. **"로그"** 탭 선택
3. 다음과 같은 로그가 보이면 정상:
   ```
   === 역사적 뉴스 수집 시작 ===
   ⏰ 시작: 2025-10-22 ...
   📍 현재 Phase: 1
   📅 수집 날짜: 2020-01-01
   📊 남은 API 호출: 25,000건
   ```

---

## 🔍 **배포 확인 방법**

### 1. 컨테이너 상태 확인
```
Container Manager → 프로젝트 → newsanalyzer
상태: ✅ 실행 중 (녹색)
```

### 2. 로그 확인
```
실시간 로그에서 다음 메시지 확인:
✅ "역사적 뉴스 수집 시작"
✅ "Phase 1 | 날짜: 2020-01-01"
✅ "대상: 1,409명"
```

### 3. 데이터 수집 확인
```
File Station → /BTF-Tech/newsanalyzer-temp/NewsAnalyzer/output/historical/
phase1/ 폴더 아래에 날짜별 폴더 생성 확인
```

### 4. 수집 상태 파일 확인
```
/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/data/collection_state.json
{
  "current_phase": 1,
  "current_date": "2020-01-XX",
  "total_api_calls_today": XXXX,
  ...
}
```

---

## ⚠️ **문제 해결**

### 빌드 실패 시:
```
로그에서 에러 메시지 확인:
- Python 패키지 설치 오류 → requirements.txt 확인
- 권한 오류 → 폴더 권한 777 확인
```

### 컨테이너 시작 안 될 때:
```
1. 포트 충돌 확인 (docker-compose.yml에 포트 노출 없음 → 문제 없음)
2. .env 파일 확인
3. 로그에서 구체적 에러 확인
```

### API 호출 오류 시:
```
로그 확인:
❌ "Naver API 호출 오류" → API 키 확인
❌ "일일 API 호출 제한" → 다음날 자동 재시작
```

---

## 📊 **예상 진행 상황**

### 첫 날 (오늘):
- Phase 1 시작: 2020-01-01부터
- 일일 API 제한: 25,000건
- 예상 수집: ~1,409명 × 1일 = 1일치 데이터

### 1주일 후:
- Phase 1 진행 중
- 수집 날짜: 2020-01-07 근처
- 축적 데이터: ~7일 × 1,409명

### 2개월 후 (Phase 1 완료):
- Phase 1 완료: 2020-2025 전체
- Phase 2 시작: 2016-2019
- 전체 진행률: ~25%

---

## 🎯 **다음 단계**

### 1. Historical 수집 모니터링 (지금~2개월)
- 매일 로그 확인
- 에러 발생 시 재시작
- API 제한 준수 확인

### 2. Daily 수집 시작 (선택사항)
- Historical 안정화 후
- newsanalyzer-daily 컨테이너 시작
- LDA 분석 결과 웹 업로드

### 3. 웹 연동 (추후)
- InsightForge 웹에 LDA 결과 표시
- 정치인별 이슈 키워드 시각화

---

## 📞 **문제 발생 시**

### 즉시 확인:
1. Container Manager → 로그
2. `/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/logs/` 폴더
3. `collection_state.json` 파일

### 재시작 방법:
```
Container Manager → 프로젝트 → newsanalyzer
1. "중지" 버튼
2. 잠시 대기
3. "시작" 버튼
→ 마지막 중단 지점부터 자동 재개
```

---

## ✅ **배포 체크리스트**

- [ ] Synology DSM 로그인 (192.168.219.2:5000)
- [ ] Container Manager 앱 열기
- [ ] 프로젝트 "newsanalyzer" 생성
- [ ] 경로: `/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
- [ ] docker-compose.yml 선택
- [ ] 환경변수 확인 (.env 자동 로드)
- [ ] newsanalyzer-historical 빌드
- [ ] newsanalyzer-historical 시작
- [ ] 로그에서 "수집 시작" 확인
- [ ] output/historical/ 폴더에 파일 생성 확인

---

## 🎊 **예상 결과**

### 8.5개월 후 (2026년 7월):
```
✅ 4,135명 정치인
✅ 6,502일 뉴스 데이터 (2008-2025)
✅ LDA 토픽 분석 완료
✅ 정치인별 이슈 키워드 매핑
✅ InsightForge 웹에 통합
```

---

**작성**: Claude Sonnet 4.5  
**날짜**: 2025-10-22  
**상태**: 🚀 배포 준비 완료

