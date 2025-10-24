# Synology NewsAnalyzer 수집 실패 해결 가이드

## 📅 작성 날짜: 2024-10-23

## 🚨 문제 상황

**현재 상태:**
- Synology NAS 연결: ✅ 정상 (192.168.219.2)
- 웹 인터페이스: ✅ 접근 가능
- NewsAnalyzer 수집: ❌ 실패
- 데이터 파일: ✅ 존재 (6.9MB, 496명 정치인)

## 🔍 수집 실패 원인 분석

### 1. 가능한 원인들
- **Docker 컨테이너 중지**: NewsAnalyzer 서비스가 중지됨
- **API 키 한도 초과**: 3개 API 계정 모두 한도 도달
- **네트워크 연결 문제**: 외부 API 호출 실패
- **데이터베이스 연결 문제**: SQLite/JSON 파일 접근 실패
- **스크립트 오류**: Python 스크립트 실행 오류
- **리소스 부족**: 메모리/CPU 부족으로 인한 중단

### 2. 진단 방법

#### SSH 접속하여 상태 확인
```bash
# Synology에 SSH 접속
ssh admin@192.168.219.2

# Docker 컨테이너 상태 확인
docker ps -a | grep newsanalyzer

# Docker Compose 상태 확인
cd /volume1/docker/NewsAnalyzer
docker-compose ps

# 컨테이너 로그 확인
docker logs newsanalyzer-historical
docker logs newsanalyzer-daily
docker logs api-management
```

#### API 키 상태 확인
```bash
# API 사용량 확인
curl -s "http://192.168.219.2:5001/api/status" | jq

# API 키 상태 확인
cat /volume1/docker/NewsAnalyzer/multi_api_config.json
```

#### 시스템 리소스 확인
```bash
# 메모리 사용량
free -h

# CPU 사용량
top

# 디스크 사용량
df -h
```

## 🔧 해결 방법

### 1. 컨테이너 재시작
```bash
# NewsAnalyzer 컨테이너 중지
cd /volume1/docker/NewsAnalyzer
docker-compose down

# 컨테이너 재시작
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 2. API 키 리셋
```bash
# API 사용량 리셋
curl -X POST "http://192.168.219.2:5001/api/reset"

# 또는 수동으로 설정 파일 수정
nano /volume1/docker/NewsAnalyzer/multi_api_config.json
```

### 3. 로그 확인 및 오류 수정
```bash
# 상세 로그 확인
docker logs -f newsanalyzer-historical

# 오류가 있다면 스크립트 수정
nano /volume1/docker/NewsAnalyzer/scripts/enhanced_historical_collector.py
```

### 4. 시스템 리소스 확보
```bash
# 불필요한 프로세스 종료
docker system prune -f

# 메모리 정리
sync && echo 3 > /proc/sys/vm/drop_caches
```

## 📊 모니터링 명령어

### 실시간 상태 확인
```bash
# 컨테이너 상태
watch -n 5 'docker ps | grep newsanalyzer'

# API 상태
watch -n 10 'curl -s http://192.168.219.2:5001/api/status'

# 로그 모니터링
tail -f /volume1/docker/NewsAnalyzer/logs/*.log
```

### 데이터 수집 진행률 확인
```bash
# 수집된 데이터 확인
ls -la /volume1/docker/NewsAnalyzer/output/lda_results/

# 파일 크기 확인
du -h /volume1/docker/NewsAnalyzer/output/lda_results/*.json
```

## 🚀 자동 복구 스크립트

### 컨테이너 자동 재시작 스크립트
```bash
#!/bin/bash
# auto_restart_newsanalyzer.sh

echo "🔄 NewsAnalyzer 자동 재시작 시작"

# 컨테이너 상태 확인
if ! docker ps | grep -q newsanalyzer; then
    echo "❌ NewsAnalyzer 컨테이너가 중지됨"
    
    # 컨테이너 재시작
    cd /volume1/docker/NewsAnalyzer
    docker-compose down
    docker-compose up -d
    
    echo "✅ NewsAnalyzer 컨테이너 재시작 완료"
else
    echo "✅ NewsAnalyzer 컨테이너 정상 작동 중"
fi
```

### API 키 자동 리셋 스크립트
```bash
#!/bin/bash
# auto_reset_api.sh

echo "🔄 API 키 자동 리셋 시작"

# API 사용량 리셋
curl -X POST "http://192.168.219.2:5001/api/reset"

echo "✅ API 키 리셋 완료"
```

## 📈 성능 최적화

### 1. 리소스 할당 조정
```yaml
# docker-compose.yml 수정
services:
  newsanalyzer-historical:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### 2. 수집 간격 조정
```json
// multi_api_config.json 수정
{
  "collection_settings": {
    "interval_minutes": 30,
    "batch_size": 100,
    "max_retries": 3
  }
}
```

### 3. 로그 로테이션 설정
```bash
# 로그 파일 크기 제한
echo "*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}" > /etc/logrotate.d/newsanalyzer
```

## 🎯 예방 조치

### 1. 정기 모니터링
- 매일 컨테이너 상태 확인
- 주간 API 사용량 점검
- 월간 시스템 리소스 검토

### 2. 자동 알림 설정
- 컨테이너 중지 시 알림
- API 한도 도달 시 알림
- 디스크 공간 부족 시 알림

### 3. 백업 및 복구
- 설정 파일 정기 백업
- 데이터베이스 백업
- 복구 스크립트 준비

## 📞 지원 정보

### 접속 정보
- **Synology IP**: 192.168.219.2
- **SSH 포트**: 22
- **사용자**: admin
- **비밀번호**: [설정된 비밀번호]

### 유용한 명령어
```bash
# 전체 시스템 상태
systemctl status

# Docker 상태
docker system df

# 네트워크 상태
netstat -tulpn

# 프로세스 상태
ps aux | grep newsanalyzer
```

## 🎉 결론

**수집 실패 문제를 해결하기 위해서는:**

1. **SSH 접속**: Synology에 SSH로 접속
2. **상태 확인**: Docker 컨테이너 및 API 상태 확인
3. **로그 분석**: 오류 원인 파악
4. **복구 실행**: 컨테이너 재시작 또는 설정 수정
5. **모니터링**: 지속적인 상태 모니터링

**이 가이드를 따라 수집 실패 문제를 해결할 수 있습니다.**

---
*이 문서는 Synology NewsAnalyzer 수집 실패 문제 해결을 위한 종합 가이드입니다.*
