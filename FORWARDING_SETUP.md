# 포워딩 설정 가이드

## 🔗 이전 포워딩 설정

### 1. Synology NewsAnalyzer 배포
- **파일**: `NewsAnalyzer/deploy_to_synology.sh`
- **목적**: NewsAnalyzer를 Synology NAS에 배포
- **포트**: Docker 컨테이너 (5000번 포트)
- **기능**: 뉴스 수집, LDA 분석, API 관리

### 2. 현재 웹사이트 배포
- **Vercel**: newsbot.kr
- **로컬 테스트**: localhost:3002
- **기능**: 웹 인터페이스, API 엔드포인트

## 🌐 포워딩 설정이 필요한 부분

### 1. Synology NewsAnalyzer → Vercel newsbot.kr

**목적**: Synology에서 수집한 데이터를 newsbot.kr로 전송

**설정 방법**:
```bash
# Synology에서 Vercel API로 데이터 전송
curl -X POST https://newsbot.kr/api/lda \
  -H "Content-Type: application/json" \
  -d @lda_results.json
```

**자동화 스크립트**:
```bash
#!/bin/bash
# Synology에서 실행할 스크립트
cd /volume1/docker/newsanalyzer

# LDA 결과를 newsbot.kr로 전송
if [ -f "output/lda_results/latest.json" ]; then
    curl -X POST https://newsbot.kr/api/lda/update \
      -H "Content-Type: application/json" \
      -d @output/lda_results/latest.json
fi
```

### 2. 로컬 개발 서버 → Vercel 배포

**목적**: 로컬 개발 중인 기능을 Vercel에 자동 배포

**GitHub Actions 설정**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

### 3. API 엔드포인트 연결

**목적**: newsbot.kr의 API가 Synology 데이터를 사용하도록 연결

**Vercel 환경 변수 설정**:
```
SYNOLOGY_API_URL=https://your-synology-ip:5000
SYNOLOGY_API_KEY=your-api-key
```

**API 연결 코드**:
```javascript
// api/index.js에서 Synology API 호출
async function getSynologyData() {
    const response = await fetch(`${process.env.SYNOLOGY_API_URL}/api/lda`);
    return response.json();
}
```

## 🚀 자동화 설정

### 1. Synology → Vercel 자동 전송

**Cron 작업 설정** (Synology DSM):
```bash
# 매일 새벽 3시에 데이터 전송
0 3 * * * cd /volume1/docker/newsanalyzer && ./forward_to_vercel.sh
```

**전송 스크립트** (`forward_to_vercel.sh`):
```bash
#!/bin/bash
VERCEL_URL="https://newsbot.kr"
SYNOLOGY_PATH="/volume1/docker/newsanalyzer"

# LDA 결과 전송
if [ -f "$SYNOLOGY_PATH/output/lda_results/latest.json" ]; then
    curl -X POST "$VERCEL_URL/api/lda/update" \
      -H "Content-Type: application/json" \
      -d @"$SYNOLOGY_PATH/output/lda_results/latest.json"
fi

# 정치인 데이터 전송
if [ -f "$SYNOLOGY_PATH/data/politicians.json" ]; then
    curl -X POST "$VERCEL_URL/api/politicians/update" \
      -H "Content-Type: application/json" \
      -d @"$SYNOLOGY_PATH/data/politicians.json"
fi
```

### 2. Vercel → Synology 상태 확인

**Vercel에서 Synology 상태 모니터링**:
```javascript
// api/synology-status.js
export default async function handler(req, res) {
    const synologyUrl = process.env.SYNOLOGY_API_URL;
    
    try {
        const response = await fetch(`${synologyUrl}/api/health`);
        const data = await response.json();
        
        res.status(200).json({
            status: 'connected',
            synology: data,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'disconnected',
            error: error.message
        });
    }
}
```

## 📊 모니터링 대시보드

### 1. 연결 상태 확인
- **URL**: https://newsbot.kr/api/synology-status
- **기능**: Synology 연결 상태, 데이터 동기화 상태

### 2. 데이터 동기화 로그
- **URL**: https://newsbot.kr/api/sync-logs
- **기능**: 최근 동기화 기록, 오류 로그

### 3. 성능 모니터링
- **URL**: https://newsbot.kr/api/performance
- **기능**: API 응답 시간, 데이터 처리량

## 🔧 문제 해결

### 1. 연결 실패 시
```bash
# Synology 연결 테스트
curl -I https://your-synology-ip:5000/api/health

# Vercel 연결 테스트
curl -I https://newsbot.kr/api/health
```

### 2. 데이터 동기화 실패 시
```bash
# 수동 동기화
cd /volume1/docker/newsanalyzer
./forward_to_vercel.sh
```

### 3. 포트 충돌 시
```bash
# 포트 확인
netstat -tulpn | grep :5000

# 프로세스 종료
sudo kill -9 $(lsof -t -i:5000)
```

## ✅ 체크리스트

- [ ] Synology NewsAnalyzer 배포 완료
- [ ] Vercel newsbot.kr 배포 완료
- [ ] 포워딩 스크립트 설정
- [ ] 자동화 Cron 작업 설정
- [ ] 모니터링 대시보드 구성
- [ ] 연결 테스트 완료
- [ ] 데이터 동기화 테스트 완료

**🎯 최종 목표: Synology에서 수집한 데이터가 newsbot.kr에서 실시간으로 표시되도록 포워딩 설정**
