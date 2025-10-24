# Synology NewsAnalyzer 디버깅 단계

## 📅 작성 날짜: 2024-10-23

## 🎯 현재 상황

**접속됨**: Synology에 SSH 접속 완료
**위치**: `/volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
**상태**: NewsAnalyzer 수집 실패

## 🔍 단계별 디버깅

### 1단계: Docker 컨테이너 상태 확인

```bash
# 컨테이너 목록 확인
sudo docker ps -a | grep newsanalyzer

# Docker Compose 상태 확인
sudo docker compose ps

# 컨테이너 리소스 사용량 확인
sudo docker stats --no-stream | grep newsanalyzer
```

**예상 결과**:
- `newsanalyzer-historical`: 실행 중 또는 중지됨
- `newsanalyzer-daily`: 실행 중 또는 중지됨
- `api-management`: 실행 중 또는 중지됨

### 2단계: 로그 확인

```bash
# NewsAnalyzer 로그 확인 (최근 50줄)
sudo docker compose logs --tail=50 newsanalyzer-historical

# API 관리 로그 확인
sudo docker compose logs --tail=20 api-management

# 실시간 로그 모니터링
sudo docker compose logs -f newsanalyzer-historical
```

**확인할 오류**:
- `API limit exceeded`
- `Connection timeout`
- `Permission denied`
- `Out of memory`
- `File not found`

### 3단계: 데이터 파일 확인

```bash
# LDA 결과 디렉토리 확인
ls -la output/lda_results/

# 파일 크기 확인
du -h output/lda_results/*.json

# 최근 수정 시간 확인
stat output/lda_results/local_politicians_lda_analysis.json
```

**예상 결과**:
- `local_politicians_lda_analysis.json`: 존재하고 크기 증가 중
- `local_lda_progress.json`: 진행률 파일
- `assembly_lda_sample.json`: 샘플 데이터

### 4단계: API 설정 확인

```bash
# API 설정 파일 확인
cat multi_api_config.json

# API 사용량 확인
curl -s http://localhost:5001/api/status | jq

# API 리셋 (필요시)
curl -X POST http://localhost:5001/api/reset
```

**확인할 설정**:
- API 키 유효성
- 일일 한도 설정
- 현재 사용량
- 오류 메시지

### 5단계: 시스템 리소스 확인

```bash
# 메모리 사용량
free -h

# 디스크 사용량
df -h /volume1

# CPU 사용량
top -n 1

# 네트워크 연결
netstat -tulpn | grep :5001
```

## 🔧 문제 해결 방법

### 문제 1: 컨테이너가 중지됨

**증상**: `sudo docker ps -a`에서 상태가 "Exited"
**해결책**:
```bash
# 컨테이너 재시작
sudo docker compose restart

# 또는 완전 재시작
sudo docker compose down
sudo docker compose up -d
```

### 문제 2: API 한도 초과

**증상**: 로그에 "API limit exceeded" 오류
**해결책**:
```bash
# API 사용량 리셋
curl -X POST http://localhost:5001/api/reset

# 또는 수동으로 설정 파일 수정
nano multi_api_config.json
```

### 문제 3: 메모리 부족

**증상**: "Out of memory" 오류
**해결책**:
```bash
# 시스템 메모리 정리
sync && echo 3 > /proc/sys/vm/drop_caches

# Docker 시스템 정리
sudo docker system prune -f

# 컨테이너 리소스 제한 확인
sudo docker inspect newsanalyzer-historical | grep -i memory
```

### 문제 4: 네트워크 연결 실패

**증상**: "Connection timeout" 또는 "Network unreachable"
**해결책**:
```bash
# 네트워크 연결 테스트
ping -c 3 8.8.8.8

# DNS 확인
nslookup google.com

# 방화벽 확인
iptables -L | grep DROP
```

### 문제 5: 파일 권한 문제

**증상**: "Permission denied" 오류
**해결책**:
```bash
# 파일 권한 확인
ls -la output/lda_results/

# 권한 수정
sudo chown -R btf_admin:btf_admin output/
sudo chmod -R 755 output/
```

## 📊 모니터링 명령어

### 실시간 상태 모니터링

```bash
# 컨테이너 상태 모니터링
watch -n 5 'sudo docker ps | grep newsanalyzer'

# 리소스 사용량 모니터링
watch -n 10 'sudo docker stats --no-stream | grep newsanalyzer'

# 로그 실시간 모니터링
sudo docker compose logs -f newsanalyzer-historical
```

### 데이터 수집 진행률 모니터링

```bash
# 파일 크기 모니터링
watch -n 30 'ls -lh output/lda_results/local_politicians_lda_analysis.json'

# 진행률 파일 확인
cat output/lda_results/local_lda_progress.json | jq
```

## 🚀 자동화 스크립트

### 컨테이너 자동 재시작 스크립트

```bash
#!/bin/bash
# auto_restart.sh

echo "🔄 NewsAnalyzer 자동 재시작 시작"

# 컨테이너 상태 확인
if ! sudo docker ps | grep -q newsanalyzer-historical; then
    echo "❌ NewsAnalyzer 컨테이너가 중지됨"
    
    # 컨테이너 재시작
    sudo docker compose down
    sudo docker compose up -d
    
    echo "✅ NewsAnalyzer 컨테이너 재시작 완료"
else
    echo "✅ NewsAnalyzer 컨테이너 정상 작동 중"
fi
```

### API 자동 리셋 스크립트

```bash
#!/bin/bash
# auto_reset_api.sh

echo "🔄 API 자동 리셋 시작"

# API 사용량 리셋
curl -X POST http://localhost:5001/api/reset

echo "✅ API 리셋 완료"
```

## 🎯 체크리스트

### ✅ 기본 확인사항
- [ ] Docker 컨테이너 실행 중
- [ ] 로그에 오류 없음
- [ ] API 설정 정상
- [ ] 데이터 파일 생성됨
- [ ] 시스템 리소스 충분

### ✅ 문제 해결 완료
- [ ] 컨테이너 재시작 완료
- [ ] API 리셋 완료
- [ ] 권한 문제 해결
- [ ] 네트워크 연결 정상
- [ ] 수집 재개 확인

## 📞 지원 정보

### 현재 위치
- **경로**: `/volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
- **사용자**: `btf_admin`
- **권한**: `sudo` 사용 가능

### 유용한 명령어
```bash
# 현재 디렉토리 확인
pwd

# 파일 목록 확인
ls -la

# 권한 확인
whoami

# 시스템 정보
uname -a
```

## 🎉 결론

**NewsAnalyzer 문제 해결을 위해서는:**

1. **상태 확인**: Docker 컨테이너 및 로그 확인
2. **문제 진단**: 오류 메시지 분석
3. **해결 실행**: 적절한 해결책 적용
4. **모니터링**: 지속적인 상태 확인

**이 단계를 따라 NewsAnalyzer 수집 실패 문제를 해결할 수 있습니다.**

---
*이 문서는 Synology에서 NewsAnalyzer 문제를 해결하기 위한 단계별 가이드입니다.*
