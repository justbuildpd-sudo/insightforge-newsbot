# 뉴스 수집 시스템 가이드

## 📊 개요

InsightForge는 두 가지 뉴스 수집 시스템을 운영합니다:

1. **구별 뉴스 수집** (기존) - `gu_news_articles.json`
2. **국회의원 뉴스 수집** (신규) - `assembly_member_news.json`

---

## 1️⃣ 국회의원 뉴스 수집

### 📁 파일
- `collect_assembly_member_news.py` - 수집 스크립트
- `analyze_assembly_news_lda.py` - LDA 분석
- `run_news_scheduler.sh` - 스케줄러 실행

### 🔑 API 정보
- **Client ID**: `kXwlSsFmb055ku9rWyx1`
- **Client Secret**: `JZqw_LTiq_`

### 📊 수집 내용
- **대상**: 48명의 국회의원
- **키워드**: `{의원명} 국정감사`
- **건수**: 의원당 50건
- **총계**: 2,400건

### ⏰ 자동 수집 스케줄
- **시간**: 매일 09:00, 15:00, 21:00 (3회)
- **실행**: `./run_news_scheduler.sh`

### 🛡️ 오프라인 대응

#### 인터넷 연결 확인
```python
if not check_internet_connection():
    print("오프라인 모드: 기존 데이터 유지")
    return  # 수집 건너뜀
```

#### 재시도 로직
- **타임아웃**: 10초, 3회 재시도
- **연결 오류**: 5초 대기 후 재시도
- **API 한도 초과**: 60초 대기

#### 오프라인 시 동작
1. 인터넷 연결 체크
2. 연결 없으면 기존 데이터 유지
3. 다음 스케줄 시간에 자동 재시도
4. 기존 데이터 통계 출력

### 💾 데이터 저장
- **원본**: `news_data/assembly_member_news.json` (1.5MB)
- **분석**: `InsightForge/Resources/assembly_member_lda_analysis.json` (215KB)

---

## 2️⃣ 구별 뉴스 수집

### 📊 수집 내용
- **대상**: 서울 25개 구
- **건수**: 구당 100건
- **총계**: 2,500건

### 📁 데이터
- `gu_news_articles.json` - 구별 뉴스 데이터

### 🔄 업데이트
- 수동 실행 (필요 시)
- 동일한 네이버 API 사용

---

## 🚨 오류 대응

### 1. 네트워크 오류
```
❌ 인터넷 연결이 없습니다.
💡 오프라인 모드: 기존 데이터를 유지합니다.
✅ 기존 데이터 유지: 48명, 2400건
```
- 기존 데이터 유지
- 다음 스케줄에 자동 재시도

### 2. API 호출 한도 초과
```
❌ HTTP 오류: 429
⏳ API 호출 한도 초과, 60초 대기...
```
- 60초 대기
- 자동 재개

### 3. 타임아웃
```
⚠️  타임아웃 (시도 1/3)
⚠️  타임아웃 (시도 2/3)
```
- 3회 재시도
- 실패 시 건너뜀

### 4. 데이터 손실 방지
- 10명마다 중간 저장
- 실패해도 기존 데이터 유지
- 덮어쓰기 안함

---

## 📝 사용 방법

### 즉시 1회 수집
```bash
python3 collect_assembly_member_news.py --once
python3 analyze_assembly_news_lda.py
```

### 스케줄러 실행 (매일 3회)
```bash
./run_news_scheduler.sh
```

### 스케줄러 중지
```bash
# Ctrl+C 또는
killall -9 python3
```

---

## 📈 데이터 흐름

```
네이버 API
    ↓
수집 (50건/의원)
    ↓
assembly_member_news.json (1.5MB)
    ↓
LDA 분석
    ↓
assembly_member_lda_analysis.json (215KB)
    ↓
Swift 앱 캐시 로드
    ↓
국회의원 팝업 표시
```

---

## 🔐 보안

- API 키는 코드에 하드코딩 (개인 프로젝트)
- 공개 저장소 사용 시 환경변수로 변경 권장

---

## 📌 참고사항

- **API 호출 한도**: 하루 25,000건 (네이버 기본)
- **실제 사용**: 하루 약 7,200건 (48명 × 50건 × 3회)
- **여유**: 충분함
- **오프라인**: 기존 데이터 유지, 자동 재시도

