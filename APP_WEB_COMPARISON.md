# iOS 앱 vs 웹 앱 기능 비교

## 📊 현재 상태

### 데이터 파일
- **iOS 앱**: 51개 JSON 파일 (로컬)
- **웹 앱**: 44개 JSON + 23개 gzip 압축 파일

### 주요 기능 수
- **iOS 앱**: 30개 데이터 로드 함수
- **웹 앱**: 18개 비동기 로드 함수

## 🔍 iOS 앱에만 있는 기능

### 1. 정치인 분석
- ✅ **LDA 토픽 분석**: assembly_member_lda_analysis.json
- ✅ **지방정치인 LDA**: local_politicians_lda_analysis.json
- 🎯 정치인별 주요 관심사/활동 토픽 분석

### 2. 네트워크 분석
- ✅ **국회의원 네트워크**: assembly_network_graph.json
- 🎯 정치인 간 연결 관계, 협력 패턴 시각화

### 3. 이슈 추적
- ✅ **이슈 아티클**: issue_articles_tracking.json
- 🎯 지역 주요 이슈 추적 및 시계열 분석

### 4. 뉴스/키워드 분석
- ✅ **구별 뉴스**: gu_news_articles.json
- ✅ **구별 키워드**: gu_news_keywords.json
- ✅ **감사 키워드**: gu_audit_keywords.json
- ✅ **감사 뉴스**: gu_audit_news.json

### 5. 상세 지역 데이터
- ✅ **상세 GDP**: seoul_detailed_gdp_data.json
- ✅ **교육 데이터**: seoul_education_data.json
- ✅ **상업지역**: seoul_commercial_area_data.json
- ✅ **안전 데이터**: seoul_safety_data.json
- ✅ **교통 데이터**: seoul_traffic_data.json

### 6. 선거 데이터
- ✅ **역사적 선거**: previous_election_data_complete.json
- ✅ **구청장**: seoul_gu_mayor_8th.json
- ✅ **지역구/비례대표**: assembly_by_region.json

## ✅ 웹 앱에만 있는 기능

### 1. 전국 데이터
- ✅ **Census 데이터**: national_census_data.json.gz (3,827개 지역)
- ✅ **17개 시도** 전체 커버
- ✅ **시계열 데이터**: 2000-2020년

### 2. 정치인 타임라인
- ✅ **그래프 위 정치인 임기** 표시
- ✅ **드래그 선택** 기간별 정치인 목록

### 3. 월별 인구 데이터
- ✅ **jumin_monthly_full**: 2018-2025년 월별 데이터
- ✅ **상세 타임라인** 차트

## 🎯 TODO: 웹 앱 개선 사항

### 우선순위 1 (핵심 기능)
1. ⬜ 정치인 LDA 분석 통합
2. ⬜ 국회의원 네트워크 그래프
3. ⬜ 이슈 추적 대시보드
4. ⬜ 상세 GDP 데이터 차트

### 우선순위 2 (부가 기능)
5. ⬜ 교육/상업/안전/교통 데이터
6. ⬜ 역사적 선거 데이터 비교
7. ⬜ 구청장 정보 표시
8. ⬜ 지역구/비례대표 구분

### 우선순위 3 (분석 기능)
9. ⬜ 뉴스/키워드 분석
10. ⬜ 감사 키워드 시각화

## 📡 필요한 API 엔드포인트

1. `/api/politician/<name>` - 정치인 상세정보 + LDA
2. `/api/network/assembly` - 국회의원 네트워크
3. `/api/issues/<region>` - 지역별 이슈
4. `/api/news/<region>` - 지역 뉴스
5. `/api/keywords/<region>` - 키워드 분석
6. `/api/timeseries/<region>` - 다년도 시계열

## 📈 데이터 규모

| 항목 | iOS 앱 | 웹 앱 |
|------|--------|-------|
| 커버 지역 | 서울 452개 동 | 전국 3,827개 지역 |
| 시도 | 서울만 | 17개 전체 |
| 시계열 | 제한적 | 2000-2025년 |
| 정치인 | 상세 분석 | 기본 정보 |
| 뉴스/이슈 | 분석 포함 | 미구현 |

