# InsightForge 앱 개발 로그

## 📱 프로젝트 개요
- **프로젝트명**: InsightForge
- **플랫폼**: macOS (SwiftUI) + 웹 (FastAPI + HTML/JS)
- **목적**: 전국 지역 통계 및 정치인 분석 시스템

---

## 🗂️ 주요 컴포넌트

### 1. macOS 앱 (InsightForge/)
- **언어**: Swift (SwiftUI)
- **주요 파일**:
  - `ContentView.swift`: 메인 UI (3단 레이아웃)
  - `Views.swift`: 서브 뷰 컴포넌트
  - `DataService.swift`: 데이터 로딩 및 캐싱
  - `Models.swift`: 데이터 모델

### 2. 웹 서비스 (insightforge-web/)
- **백엔드**: Python FastAPI
- **프론트엔드**: HTML + JavaScript + Tailwind CSS + D3.js
- **배포 대상**: Synology NAS (로컬 서버)

---

## 📊 데이터 소스

### 정적 데이터
1. **행정구역**: SGIS API (통계지리정보서비스)
2. **인구 통계**: Census 데이터 (2000-2023)
3. **GDP**: 서울시 구별 GDP 데이터
4. **교통**: 서울시 대중교통 이용량
5. **안전**: 독거노인, 장애인, 범죄율
6. **부동산**: 매매/전세 가격지수

### 동적 데이터 (뉴스 수집)
1. **국회의원** (298명): 이름 + "국정감사" 키워드, 50건/일, 3회/일
2. **지방정치인**:
   - 서울시장: "국정감사" + "행정사무감사", 20건/일
   - 시의원/구청장/구의원: "행정사무감사", 10건/일

---

## 🎯 주요 기능

### macOS 앱
1. **지역 선택**
   - 17개 시도 + 비례대표 (접이식 트리)
   - 서울: 25개 구 → 426개 동
   - 전국: 252개 시군구 → 3,558개 읍면동

2. **상세 통계 보기**
   - 인구, 연령, 밀도, 고령화
   - GDP, 교통, 안전
   - 부동산 가격지수
   - 정치인 정보 (시장/구청장/의원)

3. **비교 및 순위**
   - 여러 구 선택하여 비교
   - 지표별 순위 표시
   - 트렌드 분석 (증감률, 예측)

4. **LDA 토픽 분석**
   - 뉴스 기사 수집 및 분류
   - 워드클라우드 (Spiral Layout)
   - 토픽별 키워드 순위 (TOP 10)

5. **국회의원-이슈 연결 지도**
   - 298명 의원 × 14개 이슈 네트워크
   - 의원-의원 연결 (공유 기사/위원회)
   - 클러스터링 및 필터링
   - 상세 추적 (이슈별/날짜별 기사)

### 웹 버전 (진행 중)
1. **기본 구조**: ✅ 완료
2. **서울 데이터**: ✅ 완료
3. **통계 표시**: ✅ GDP, 교통, 안전 추가
4. **전국 데이터**: 🔄 수집 중
5. **차트/그래프**: ⏳ 미구현
6. **LDA 분석**: ⏳ 미구현
7. **정치인 정보**: ⏳ 미구현

---

## 🔧 기술 스택

### macOS 앱
- SwiftUI (UI 프레임워크)
- Combine (반응형 프로그래밍)
- JSONDecoder (데이터 파싱)

### 웹 서비스
- **백엔드**: FastAPI, uvicorn
- **프론트엔드**: Vanilla JS, Tailwind CSS, D3.js
- **배포**: Docker + Nginx + Redis (예정)

### 데이터 수집
- Python requests (API 호출)
- pandas (데이터 처리)
- schedule (스케줄링)

---

## 🗝️ API 키 정보

### Naver News API
1. **국회의원용**
   - Client ID: `kXwlSsFmb055ku9rWyx1`
   - Client Secret: `JZqw_LTiq_`

2. **지방정치인용**
   - Client ID: `ULDLTGiPvrrPBgbuydSm`
   - Client Secret: `uO5mu7UQBg`

### SGIS API (통계지리정보서비스)
- Service ID: `8806b098778b4d6e84cd`
- Security Key: `5736845d40cf49ec8da5`

---

## 📝 데이터 파일 구조

### macOS 앱 리소스
```
InsightForge/Resources/
├── seoul_comprehensive_data.json         # 서울 종합 (426개 동)
├── seoul_gdp_data.json                   # 서울 GDP (25개 구)
├── seoul_traffic_data.json               # 서울 교통 (25개 구)
├── seoul_safety_data.json                # 서울 안전 (25개 구)
├── national_assembly_22nd_real.json      # 국회의원 (서울)
├── assembly_by_region.json               # 국회의원 (전국 298명)
├── assembly_member_lda_analysis.json     # 국회의원 LDA
├── local_politicians_lda_analysis.json   # 지방정치인 LDA
├── assembly_network_graph.json           # 의원-이슈 네트워크
├── issue_articles_tracking.json          # 이슈별 기사 추적
├── sido_sigungu_list.json                # 전국 시도-시군구 목록
├── seoul_mayor_8th_real.json             # 서울시장
├── seoul_si_uiwon_8th_real.json          # 서울시의원
├── seoul_gu_mayor_8th.json               # 구청장
└── seoul_gu_uiwon_8th_real.json          # 구의원
```

### 웹 서비스 데이터
```
insightforge-web/data/
├── seoul_comprehensive_data.json         # 서울 종합
├── seoul_gdp_data.json                   # 서울 GDP
├── seoul_traffic_data.json               # 서울 교통
├── seoul_safety_data.json                # 서울 안전
├── sgis_national_regions.json            # 전국 행정구역 (252개 시군구, 3,558개 읍면동)
└── sgis_comprehensive_stats.json         # 전국 통계 (수집 중)
```

---

## 🎨 UI/UX 특징

### macOS 앱
1. **3단 레이아웃**
   - 좌측: 지역 목록 (접이식 트리)
   - 중앙: 상세 통계 (4개 주요 카드 + 차트)
   - 우측: LDA 토픽 분석 + 워드클라우드

2. **색상 시스템**
   - 정당별 고유 색상 (더불어민주당: 파랑, 국민의힘: 빨강, 등)
   - 트렌드: 증가(녹색), 감소(빨강)
   - 강조: 선택된 항목(노랑)

3. **인터랙션**
   - 클릭: 지역/의원 선택
   - 체크박스: 비교 모드
   - 검색: 의원명 검색
   - 토글: 의원 연결 / 이슈 연결

### 웹 버전
1. **반응형 디자인**
   - Tailwind CSS 유틸리티 클래스
   - 모바일 대응 (예정)

2. **색상**
   - 헤더: 파랑 (bg-blue-600)
   - 카드: 그라데이션 (blue, green, purple, orange)

---

## 🐛 해결된 주요 이슈

### 1. UI 정렬 문제
- **문제**: 3단 레이아웃 헤더 높이 불일치
- **해결**: 
  - NavigationView 제거
  - `.windowStyle(.hiddenTitleBar)` 적용
  - HStack(alignment: .top) 사용
  - 일관된 padding 적용

### 2. 데이터 로딩 성능
- **문제**: 국회의원 팝업 로딩 느림 (700KB JSON)
- **해결**:
  - 앱 시작 시 데이터 캐싱
  - 백그라운드 스레드에서 로드
  - 기사 수 제한 (20건 → 5건)

### 3. HTML 엔티티 문제
- **문제**: 기사 제목에 `&quot;`, `&#39;` 등 표시
- **해결**: `decodeHTMLEntities` 함수 구현

### 4. Swift 컴파일러 타입 체크 실패
- **문제**: "compiler unable to type-check"
- **해결**: 복잡한 ViewBuilder를 helper 함수로 분리

### 5. 행정코드 불일치
- **문제**: Census 코드 ≠ 행정코드 (예: 11010 vs 11110)
- **해결**: 서울 데이터로 우선 진행, 이름 기반 매핑

### 6. 워드클라우드 겹침
- **문제**: 단어들이 중첩되어 표시
- **해결**: Spiral Layout 알고리즘 구현

---

## 📌 핵심 원칙 (메모리)

1. **절대 가짜 인물 생성 금지**
   - 실제 22대 국회의원 데이터만 사용
   - CSV 기반 298명 확정 데이터

2. **의원정보 수정 불가**
   - 현재 298명 데이터가 최종본
   - 임의 변경/추가 금지

3. **작업 방식**
   - 한 번에 하나씩 진행
   - 확인 없이 바로 실행
   - 실패 시 철저히 해결

---

## 🔄 다음 단계

### 웹 서비스 완성
1. ✅ 전국 행정구역 수집 (완료)
2. 🔄 전국 통계 수집 (진행 중)
3. ⏳ 백엔드 API 확장
4. ⏳ 프론트엔드 기능 구현
   - 차트/그래프 (D3.js)
   - LDA 분석 표시
   - 정치인 정보
   - 비교/순위 기능
5. ⏳ Synology 배포

### macOS 앱 개선
- 추가 통계 항목
- 성능 최적화
- 에러 핸들링

---

## 📅 타임라인

- **2025-10-02**: 프로젝트 시작, 기본 UI 구축
- **2025-10-03**: 서울 데이터 통합
- **2025-10-09**: LDA 분석 구현
- **2025-10-10**: 국회의원 뉴스 수집
- **2025-10-11**: 지방정치인 뉴스 수집
- **2025-10-12**: 비교/순위 기능
- **2025-10-13**: 전국 시도 확장, 연결 지도
- **2025-10-14**: 웹 서비스 개발 시작, SGIS API 통합

---

**마지막 업데이트**: 2025-10-14 10:30
**상태**: 전국 통계 데이터 수집 중 (백그라운드)

