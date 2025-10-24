# 🚀 NewsAnalyzer 다중 API 시스템 배포 가이드

## 📋 개요

3개의 네이버 API 계정을 사용하여 하루 종일 뉴스 수집이 가능한 시스템입니다.

### 주요 기능
- ✅ **3개 API 계정 로테이션**: 총 75,000건/일 수집 가능
- ✅ **실시간 API 관리**: 웹 인터페이스로 중간에 API 추가/제거/수정
- ✅ **자동 부하 분산**: API 사용량에 따른 자동 전환
- ✅ **연속 수집**: 하루 종일 중단 없는 수집
- ✅ **모니터링**: 실시간 사용량 및 상태 확인

## 🛠️ 시스템 구조

```
NewsAnalyzer/
├── scripts/
│   ├── multi_api_manager.py          # 다중 API 관리자
│   ├── enhanced_historical_collector.py  # 향상된 수집기
│   └── api_management_server.py      # API 관리 웹 서버
├── templates/
│   └── api_management.html           # 웹 인터페이스
├── multi_api_config.json            # API 설정 파일
└── docker-compose.yml               # Docker Compose 설정
```

## 📦 배포 단계

### 1단계: API 계정 설정

`multi_api_config.json` 파일을 수정하여 3개의 네이버 API 계정을 설정합니다:

```json
{
  "api_accounts": [
    {
      "id": "api_1",
      "client_id": "YOUR_FIRST_CLIENT_ID",
      "client_secret": "YOUR_FIRST_CLIENT_SECRET",
      "daily_limit": 25000,
      "enabled": true,
      "priority": 1,
      "description": "Primary API Account"
    },
    {
      "id": "api_2", 
      "client_id": "YOUR_SECOND_CLIENT_ID",
      "client_secret": "YOUR_SECOND_CLIENT_SECRET",
      "daily_limit": 25000,
      "enabled": true,
      "priority": 2,
      "description": "Secondary API Account"
    },
    {
      "id": "api_3",
      "client_id": "YOUR_THIRD_CLIENT_ID", 
      "client_secret": "YOUR_THIRD_CLIENT_SECRET",
      "daily_limit": 25000,
      "enabled": true,
      "priority": 3,
      "description": "Tertiary API Account"
    }
  ]
}
```

### 2단계: Synology에 배포

```bash
# 1. 기존 컨테이너 중지
sudo docker compose down

# 2. 새 이미지 빌드
sudo docker compose build --no-cache

# 3. 서비스 시작
sudo docker compose up -d

# 4. 로그 확인
sudo docker compose logs -f newsanalyzer-historical
```

### 3단계: 웹 관리 인터페이스 접속

브라우저에서 `http://192.168.219.2:5000` 접속하여 API 관리 인터페이스를 사용할 수 있습니다.

## 🔧 API 관리 기능

### 웹 인터페이스 기능
- 📊 **실시간 사용량 모니터링**: 각 API 계정의 사용량 확인
- ➕ **새 API 계정 추가**: 중간에 API 계정 추가 가능
- ✏️ **API 계정 수정**: 기존 계정 정보 수정
- 🗑️ **API 계정 삭제**: 불필요한 계정 제거
- 🧪 **API 테스트**: 각 계정의 연결 상태 테스트
- 🔄 **사용량 리셋**: 일일 사용량 수동 리셋

### API 계정 추가 방법

1. 웹 인터페이스에서 "새 계정 추가" 버튼 클릭
2. 다음 정보 입력:
   - **계정 ID**: 고유 식별자 (예: api_4)
   - **Client ID**: 네이버 API Client ID
   - **Client Secret**: 네이버 API Client Secret
   - **일일 한도**: 기본값 25,000
   - **우선순위**: 1-3 (낮을수록 우선)
   - **설명**: 계정 설명

3. "추가" 버튼 클릭

## 📊 모니터링

### 실시간 상태 확인
```bash
# 컨테이너 상태 확인
sudo docker compose ps

# 수집기 로그 확인
sudo docker compose logs -f newsanalyzer-historical

# API 관리 서버 로그 확인
sudo docker compose logs -f api-management
```

### 사용량 확인
- 웹 인터페이스: `http://192.168.219.2:5000`
- API 엔드포인트: `http://192.168.219.2:5000/api/status`

## 🔄 운영 가이드

### 일일 운영
1. **오전 00:00**: API 사용량 자동 리셋
2. **연속 수집**: 하루 종일 자동 수집 진행
3. **모니터링**: 웹 인터페이스로 상태 확인

### 문제 해결

#### API 한도 도달시
- 자동으로 다음 API 계정으로 전환
- 모든 계정 한도 도달시 1시간 대기 후 재시도

#### API 계정 오류시
- 웹 인터페이스에서 해당 계정 비활성화
- 새 계정 추가 또는 기존 계정 수정

#### 수집 중단시
```bash
# 컨테이너 재시작
sudo docker compose restart newsanalyzer-historical

# 로그 확인
sudo docker compose logs -f newsanalyzer-historical
```

## 📈 성능 최적화

### 권장 설정
- **API 계정**: 3개 이상
- **일일 한도**: 계정당 25,000건
- **요청 간격**: 0.1초
- **배치 크기**: 100건

### 예상 수집량
- **3개 계정**: 75,000건/일
- **수집 기간**: 2008-2025 (17년)
- **예상 완료**: 약 2-3개월

## 🚨 주의사항

1. **API 키 보안**: Client Secret은 절대 공개하지 마세요
2. **사용량 모니터링**: 일일 한도 초과 방지
3. **백업**: 정기적으로 데이터 백업
4. **로그 관리**: 로그 파일 크기 주기적 확인

## 📞 지원

문제 발생시 다음을 확인하세요:
1. 컨테이너 상태: `sudo docker compose ps`
2. 로그 확인: `sudo docker compose logs`
3. 웹 인터페이스: `http://192.168.219.2:5000`
4. API 설정: `multi_api_config.json`

---

**🎯 목표**: 3개 API 계정으로 하루 75,000건 수집하여 2008-2025년 전체 기간의 정치인 뉴스 데이터 완성!
