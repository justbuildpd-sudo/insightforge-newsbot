# 시놀로지 NAS 기반 웹서비스 마이그레이션 계획

## 📋 시놀로지 정보

- **주소**: http://192.168.219.2:5000
- **계정**: btf_admin / Ks&js140405
- **상태**: ✅ 연결 성공
- **서비스**: DSM, SSH(포트 22), Docker API

---

## 🎯 마이그레이션 목표

현재 **macOS 전용 SwiftUI 앱 (InsightForge)**을:
- ✅ 웹 기반 서비스로 전환
- ✅ 시놀로지 NAS에서 호스팅
- ✅ 서버 비용 0원 (로컬 NAS 활용)
- ✅ 크로스 플랫폼 지원 (Windows, Mac, Mobile)

---

## 🏗️ 아키텍처

### **시놀로지 Docker 기반**

```
┌─────────────────────────────────────────┐
│         사용자 (브라우저)               │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│   Nginx (포트 80/443)                   │
│   리버스 프록시                         │
└──────┬──────────────────┬───────────────┘
       │                  │
       ↓                  ↓
┌──────────────┐   ┌──────────────────┐
│  React       │   │  FastAPI         │
│  (포트 3000) │   │  (포트 8000)     │
│  프론트엔드  │   │  백엔드 API      │
└──────────────┘   └────┬─────────────┘
                        │
                ┌───────┴────────┬──────────┐
                ↓                ↓          ↓
         ┌──────────┐    ┌──────────┐  ┌──────────┐
         │PostgreSQL│    │  Redis   │  │   Data   │
         │ (DB)     │    │ (Cache)  │  │  (JSON)  │
         └──────────┘    └──────────┘  └──────────┘
```

---

## 📂 시놀로지 디렉토리 구조

```
/volume1/
├── docker/
│   └── insightforge/
│       ├── docker-compose.yml
│       ├── nginx/
│       │   ├── Dockerfile
│       │   └── nginx.conf
│       ├── backend/
│       │   ├── Dockerfile
│       │   ├── requirements.txt
│       │   ├── main.py
│       │   ├── api/
│       │   │   ├── regions.py
│       │   │   ├── politicians.py
│       │   │   ├── lda.py
│       │   │   └── network.py
│       │   ├── services/
│       │   │   ├── news_collector.py
│       │   │   ├── lda_analyzer.py
│       │   │   └── data_service.py
│       │   └── models/
│       │       ├── region.py
│       │       ├── politician.py
│       │       └── network.py
│       ├── frontend/
│       │   ├── Dockerfile
│       │   ├── package.json
│       │   ├── public/
│       │   └── src/
│       │       ├── components/
│       │       │   ├── RegionList/
│       │       │   ├── RegionDetail/
│       │       │   ├── LDAAnalysis/
│       │       │   ├── NetworkGraph/
│       │       │   └── WordCloud/
│       │       ├── pages/
│       │       │   ├── Home.tsx
│       │       │   ├── RegionView.tsx
│       │       │   └── NetworkView.tsx
│       │       └── services/
│       │           └── api.ts
│       └── data/
│           ├── seoul_comprehensive_data.json
│           ├── assembly_member_lda_analysis.json
│           ├── local_politicians_lda_analysis.json
│           ├── assembly_network_graph.json
│           └── issue_articles_tracking.json
└── web/
    └── insightforge/  # 빌드된 정적 파일 (백업용)
```

---

## 🔧 기술 스택

### **백엔드 (Python)**
```python
FastAPI 0.104+        # API 프레임워크
Uvicorn              # ASGI 서버
SQLAlchemy           # ORM (필요 시)
Pydantic             # 데이터 검증
APScheduler          # 뉴스 수집 스케줄러
Redis                # 캐싱
```

### **프론트엔드 (TypeScript + React)**
```javascript
Next.js 14           # React 프레임워크
TypeScript           # 타입 안정성
D3.js                # 네트워크 그래프
Recharts             # 통계 차트
Tailwind CSS         # 스타일링
React Query          # 데이터 캐싱
Zustand              # 상태 관리
```

### **인프라 (Docker)**
```yaml
Nginx               # 리버스 프록시, SSL
PostgreSQL 15       # 데이터베이스 (선택)
Redis 7            # 캐싱
```

---

## 📅 마이그레이션 일정

### **Week 1: 환경 구축**

#### Day 1-2: 시놀로지 설정
- [x] SSH 연결 확인
- [ ] Docker 설치 확인
- [ ] 공유 폴더 생성
- [ ] Git 저장소 설정 (선택)

#### Day 3-4: 백엔드 기본 구조
- [ ] FastAPI 프로젝트 생성
- [ ] 기존 Python 코드 통합
- [ ] API 엔드포인트 설계
- [ ] Docker 이미지 빌드

#### Day 5-7: 데이터 API화
- [ ] JSON 데이터 로딩 엔드포인트
- [ ] LDA 분석 결과 API
- [ ] 네트워크 그래프 API
- [ ] CORS 설정

### **Week 2: 프론트엔드 개발**

#### Day 1-3: 기본 레이아웃
- [ ] Next.js 프로젝트 생성
- [ ] 레이아웃 컴포넌트
- [ ] 지역 선택 사이드바
- [ ] 상세 정보 패널

#### Day 4-5: LDA 분석 뷰
- [ ] 토픽 분석 컴포넌트
- [ ] 워드 클라우드 (D3.js)
- [ ] 기사 목록

#### Day 6-7: 네트워크 그래프
- [ ] D3.js 네트워크 시각화
- [ ] 의원-이슈 연결
- [ ] 의원-의원 연결
- [ ] 클러스터 표시

### **Week 3: 통합 및 최적화**

#### Day 1-3: 통합 테스트
- [ ] API 연동 테스트
- [ ] 반응형 디자인
- [ ] 성능 최적화

#### Day 4-5: 배포
- [ ] Docker Compose 설정
- [ ] Nginx 설정
- [ ] SSL 인증서 (Let's Encrypt)
- [ ] 자동화 스크립트

#### Day 6-7: 모니터링
- [ ] 로그 설정
- [ ] 백업 스크립트
- [ ] 문서화

---

## 🚀 즉시 실행 가능한 작업

### **Step 1: SSH 연결 확인**

터미널에서 실행:
```bash
ssh btf_admin@192.168.219.2
# 비밀번호: Ks&js140405
```

연결 후 실행:
```bash
# 시스템 정보
uname -a
cat /etc/synoinfo.conf | grep model

# Docker 확인
docker --version
docker ps

# 디스크 공간
df -h

# 볼륨 확인
ls -la /volume1/
```

---

## 💻 백엔드 API 설계

### **주요 엔드포인트**

```python
# 지역 데이터
GET  /api/regions                    # 전체 지역 목록
GET  /api/regions/{gu}               # 구 상세 정보
GET  /api/regions/{gu}/statistics    # 통계 데이터
GET  /api/regions/{gu}/rankings      # 순위 정보
GET  /api/regions/compare            # 지역 비교

# LDA 분석
GET  /api/lda/district/{gu}          # 구 단위 LDA
GET  /api/lda/assembly/{name}        # 국회의원 LDA
GET  /api/lda/local/{name}           # 지방정치인 LDA

# 정치인
GET  /api/politicians/assembly       # 국회의원 목록
GET  /api/politicians/local/{gu}     # 지역 정치인
GET  /api/politicians/{name}         # 개별 정치인

# 네트워크
GET  /api/network/assembly           # 국회의원-이슈 네트워크
GET  /api/network/members            # 의원-의원 네트워크
GET  /api/network/clusters           # 클러스터 정보
GET  /api/network/issues/{issue}     # 이슈별 추적

# 검색
GET  /api/search?q={query}           # 통합 검색
```

---

## 🎨 프론트엔드 페이지 구조

### **메인 페이지**
```
┌────────────────────────────────────────────┐
│  Header (로고, 검색, 메뉴)                 │
├──────────┬────────────────┬────────────────┤
│          │                │                │
│  지역    │  상세 정보     │  LDA 분석      │
│  목록    │                │  워드 클라우드 │
│          │  - 인구        │                │
│  (접기   │  - GDP         │  토픽 분석     │
│   가능)  │  - 교육        │                │
│          │  - 부동산      │  기사 목록     │
│          │  - 정치인      │                │
│          │                │                │
└──────────┴────────────────┴────────────────┘
```

### **네트워크 페이지**
```
┌────────────────────────────────────────────┐
│  의원-이슈 연결 지도                       │
│  [이슈 연결] [의원 연결] [검색]            │
├────────────────────────────────────────────┤
│                                            │
│        D3.js 네트워크 그래프               │
│                                            │
│  - 노드 클릭: 상세 정보                   │
│  - 연결선 클릭: 관련 기사                 │
│  - 검색: 의원 찾기                        │
│  - 필터: 클러스터별                       │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🔐 보안 설정

### **시놀로지 방화벽**
```
제어판 → 보안 → 방화벽
허용 규칙:
  - 포트 80 (HTTP)
  - 포트 443 (HTTPS)
  - 포트 22 (SSH - 제한적)
```

### **HTTPS 설정**
```
제어판 → 보안 → 인증서
Let's Encrypt 무료 SSL
```

---

## 📊 예상 리소스 사용량

### **디스크**
- 백엔드 이미지: ~500MB
- 프론트엔드 이미지: ~200MB
- 데이터: ~100MB
- 총: **~1GB**

### **메모리**
- Nginx: ~50MB
- FastAPI: ~200MB
- Redis: ~50MB
- 총: **~300MB**

### **CPU**
- 평상시: 5-10%
- 뉴스 수집/분석 시: 30-50%

---

## ✅ 다음 단계

### **지금 바로 실행:**

1. **SSH 연결 테스트**
   ```bash
   ssh btf_admin@192.168.219.2
   # 비밀번호: Ks&js140405
   ```

2. **연결 후 확인**
   ```bash
   docker --version
   ls -la /volume1/
   df -h
   ```

3. **결과를 알려주시면:**
   - Docker 설치 여부
   - 사용 가능한 공유 폴더
   - 여유 공간

   → **즉시 마이그레이션 시작!**

---

## 🚀 빠른 시작 (준비되면)

```bash
# 1. 프로젝트 업로드
scp -r /Users/hopidad/Desktop/workspace/InsightForge btf_admin@192.168.219.2:/volume1/docker/

# 2. Docker Compose 실행
ssh btf_admin@192.168.219.2
cd /volume1/docker/insightforge
docker-compose up -d

# 3. 접속
# http://192.168.219.2
```

---

## 📞 문의사항

- Docker 설치 여부?
- 공유 폴더 생성 필요?
- 도메인 설정 필요?

**SSH 연결 테스트를 먼저 진행해주세요!** 🔐

