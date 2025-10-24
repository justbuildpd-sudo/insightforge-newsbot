# Synology 컨테이너 재시작 대기 및 상태 확인 가이드

## 📅 작성 날짜: 2024-10-23

## 🚨 현재 상황

**컨테이너 상태**: 재시작 중
**오류 메시지**: "Container is restarting, wait until the container is running"
**문제**: 컨테이너가 완전히 시작되지 않아 권한 수정 불가

## 🔍 컨테이너 상태 확인

### 1. 컨테이너 상태 확인
```bash
# 모든 컨테이너 상태 확인
sudo docker ps -a | grep newsanalyzer

# 실행 중인 컨테이너만 확인
sudo docker ps | grep newsanalyzer-historical

# Docker Compose 상태 확인
sudo docker compose ps
```

### 2. 컨테이너 재시작 상태 확인
```bash
# 컨테이너가 "Up" 상태인지 확인
sudo docker ps | grep "newsanalyzer-historical.*Up"

# 컨테이너 재시작 로그 확인
sudo docker compose logs --tail=20 newsanalyzer-historical
```

## ⏳ 컨테이너 재시작 대기

### 1. 자동 대기 스크립트
```bash
#!/bin/bash
# 컨테이너 재시작 대기 스크립트

echo "⏳ 컨테이너 재시작 완료 대기 중..."

# 재시작 완료까지 대기 (최대 60초)
for i in {1..12}; do
    echo "대기 중... ($i/12)"
    if sudo docker ps | grep -q "newsanalyzer-historical.*Up"; then
        echo "✅ newsanalyzer-historical 컨테이너가 실행 중입니다"
        break
    fi
    sleep 5
done
```

### 2. 수동 대기 방법
```bash
# 1. 컨테이너 상태 확인
sudo docker ps | grep newsanalyzer-historical

# 2. "Up" 상태가 될 때까지 대기
# 3. 재시작 완료 후 권한 수정 시도
```

## 🔧 권한 수정 재시도

### 1. 컨테이너 실행 확인 후 권한 수정
```bash
# 컨테이너가 실행 중인지 확인
sudo docker ps | grep "newsanalyzer-historical.*Up"

# 권한 수정 시도
sudo docker exec -it newsanalyzer-historical chown -R 1000:1000 /app/output/

# 또는 루트 권한으로 시도
sudo docker exec -u root -it newsanalyzer-historical chown -R 1000:1000 /app/output/
```

### 2. 컨테이너 재시작 후 권한 수정
```bash
# 컨테이너 재시작
sudo docker compose restart newsanalyzer-historical

# 재시작 완료 대기
sleep 10

# 상태 확인
sudo docker ps | grep newsanalyzer-historical

# 권한 수정 시도
sudo docker exec -it newsanalyzer-historical chown -R 1000:1000 /app/output/
```

## 📊 컨테이너 로그 확인

### 1. 실시간 로그 모니터링
```bash
# 실시간 로그 확인
sudo docker compose logs -f newsanalyzer-historical

# 최근 로그 확인
sudo docker compose logs --tail=50 newsanalyzer-historical
```

### 2. 오류 로그 확인
```bash
# 오류 로그만 확인
sudo docker compose logs newsanalyzer-historical 2>&1 | grep -i error

# 경고 로그 확인
sudo docker compose logs newsanalyzer-historical 2>&1 | grep -i warn
```

## 🚀 문제 해결 단계

### 1단계: 컨테이너 상태 확인
```bash
# 컨테이너 상태 확인
sudo docker ps -a | grep newsanalyzer

# 실행 중인 컨테이너 확인
sudo docker ps | grep newsanalyzer-historical
```

### 2단계: 재시작 완료 대기
```bash
# 컨테이너가 "Up" 상태가 될 때까지 대기
while ! sudo docker ps | grep -q "newsanalyzer-historical.*Up"; do
    echo "컨테이너 재시작 대기 중..."
    sleep 5
done
echo "✅ 컨테이너가 실행 중입니다"
```

### 3단계: 권한 수정 시도
```bash
# 권한 수정 시도
sudo docker exec -it newsanalyzer-historical chown -R 1000:1000 /app/output/

# 결과 확인
sudo docker exec -it newsanalyzer-historical ls -la /app/output/
```

### 4단계: 테스트
```bash
# 파일 생성 테스트
touch output/test_file.txt

# 권한 확인
ls -la output/
```

## 🔍 컨테이너 문제 진단

### 1. 컨테이너가 계속 재시작되는 경우
```bash
# 컨테이너 로그 확인
sudo docker compose logs newsanalyzer-historical

# 컨테이너 상태 확인
sudo docker inspect newsanalyzer-historical

# 컨테이너 재시작
sudo docker compose restart newsanalyzer-historical
```

### 2. 컨테이너가 시작되지 않는 경우
```bash
# 컨테이너 강제 중지
sudo docker compose down

# 컨테이너 재시작
sudo docker compose up -d

# 상태 확인
sudo docker compose ps
```

### 3. 네트워크 문제인 경우
```bash
# 네트워크 확인
sudo docker network ls

# 컨테이너 네트워크 확인
sudo docker inspect newsanalyzer-historical | grep -i network
```

## 📊 모니터링 명령어

### 1. 실시간 상태 모니터링
```bash
# 컨테이너 상태 모니터링
watch -n 5 'sudo docker ps | grep newsanalyzer'

# 로그 실시간 모니터링
sudo docker compose logs -f newsanalyzer-historical
```

### 2. 리소스 사용량 모니터링
```bash
# 컨테이너 리소스 사용량
sudo docker stats --no-stream | grep newsanalyzer

# 시스템 리소스 확인
free -h
df -h
```

## 🎯 체크리스트

### ✅ 컨테이너 상태 확인
- [ ] 컨테이너가 "Up" 상태인지 확인
- [ ] 재시작 완료 대기
- [ ] 로그에 오류 없음
- [ ] 네트워크 연결 정상

### ✅ 권한 수정 완료
- [ ] 컨테이너 내부 권한 수정
- [ ] 파일 생성 테스트 성공
- [ ] 권한 변경 확인
- [ ] 데이터 수집 정상 작동

## 🚨 긴급 해결 방법

### 1. 컨테이너 완전 재시작
```bash
sudo docker compose down
sudo docker compose up -d
```

### 2. 컨테이너 강제 재시작
```bash
sudo docker restart newsanalyzer-historical
```

### 3. 시스템 재시작
```bash
sudo reboot
```

## 📞 지원 정보

### 현재 위치
- **경로**: `/volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
- **사용자**: `btf_admin`
- **권한**: `sudo` 사용 가능

### 유용한 명령어
```bash
# 컨테이너 상태
sudo docker ps

# 컨테이너 로그
sudo docker compose logs newsanalyzer-historical

# 컨테이너 재시작
sudo docker compose restart newsanalyzer-historical
```

## 🎉 결론

**컨테이너 재시작 문제 해결을 위해서는:**

1. **상태 확인**: 컨테이너가 "Up" 상태인지 확인
2. **대기**: 재시작 완료까지 대기
3. **로그 확인**: 오류 메시지 확인
4. **권한 수정**: 컨테이너 실행 후 권한 수정
5. **테스트**: 파일 생성 및 권한 확인

**이 단계를 따라 컨테이너 재시작 문제를 해결할 수 있습니다.**

---
*이 문서는 Synology에서 컨테이너 재시작 대기 및 상태 확인을 위한 가이드입니다.*
