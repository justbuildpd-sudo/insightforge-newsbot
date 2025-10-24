# Synology 권한 문제 해결 방법

## 📅 작성 날짜: 2024-10-23

## 🚨 문제 상황

**권한 문제**: `chown: invalid group: 'btf_admin:btf_admin'`
**원인**: Synology에서 `btf_admin` 그룹이 존재하지 않음

## 🔍 권한 문제 진단

### 1. 사용자 정보 확인
```bash
# 현재 사용자 정보
id

# 사용자명 확인
whoami

# 사용 가능한 그룹 확인
getent group | grep -E "(btf|admin|users)"
```

### 2. 현재 권한 상태 확인
```bash
# 현재 디렉토리 권한
ls -la

# output 디렉토리 권한
ls -la output/

# 파일 생성 테스트
touch output/test_file.txt
```

## 🔧 해결 방법들

### 방법 1: 올바른 그룹 사용

```bash
# users 그룹 사용 (가장 일반적)
sudo chown -R btf_admin:users output/

# 또는 admin 그룹 사용
sudo chown -R btf_admin:admin output/

# 또는 그룹 없이 소유자만 변경
sudo chown -R btf_admin output/
```

### 방법 2: 권한 우회

```bash
# 777 권한으로 설정 (모든 권한)
sudo chmod -R 777 output/

# 또는 755 권한으로 설정
sudo chmod -R 755 output/
```

### 방법 3: Docker 컨테이너 내부에서 권한 수정

```bash
# newsanalyzer-historical 컨테이너 내부에서 권한 수정
sudo docker exec -it newsanalyzer-historical chown -R 1000:1000 /app/output/

# 또는 루트 권한으로 실행
sudo docker exec -u root -it newsanalyzer-historical chown -R 1000:1000 /app/output/
```

### 방법 4: 루트 권한으로 작업

```bash
# 루트로 전환
sudo su -

# 루트 권한으로 권한 수정
chown -R btf_admin:users /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/output/

# 일반 사용자로 돌아가기
exit
```

### 방법 5: 파일 권한 무시

```bash
# 루트 권한으로 파일 생성
sudo -u root touch output/test.txt

# 루트 권한으로 권한 설정
sudo -u root chmod 777 output/
```

## 📊 단계별 해결 과정

### 1단계: 정보 수집
```bash
# 사용자 정보 확인
id
whoami

# 그룹 정보 확인
getent group | grep -E "(btf|admin|users)"

# 현재 권한 확인
ls -la output/
```

### 2단계: 권한 수정 시도
```bash
# 방법 1: users 그룹 사용
sudo chown -R btf_admin:users output/

# 방법 2: 소유자만 변경
sudo chown -R btf_admin output/

# 방법 3: 777 권한 설정
sudo chmod -R 777 output/
```

### 3단계: 테스트
```bash
# 파일 생성 테스트
touch output/test_file.txt

# 권한 확인
ls -la output/
```

### 4단계: Docker 컨테이너 내부 작업
```bash
# 컨테이너 내부 접속
sudo docker exec -it newsanalyzer-historical bash

# 컨테이너 내부에서 권한 수정
chown -R 1000:1000 /app/output/
chmod -R 755 /app/output/
```

## 🚀 자동화 스크립트

### 권한 문제 해결 스크립트
```bash
#!/bin/bash
# permission_fix.sh

echo "=== Synology 권한 문제 해결 ==="

# 1. 정보 수집
echo "📊 사용자 정보:"
id
whoami

echo ""
echo "📊 사용 가능한 그룹:"
getent group | grep -E "(btf|admin|users)"

# 2. 권한 수정 시도
echo ""
echo "🔧 권한 수정 시도:"

# 방법 1: users 그룹
sudo chown -R btf_admin:users output/ 2>/dev/null && echo "✅ users 그룹 성공" || echo "❌ users 그룹 실패"

# 방법 2: 소유자만 변경
sudo chown -R btf_admin output/ 2>/dev/null && echo "✅ 소유자 변경 성공" || echo "❌ 소유자 변경 실패"

# 방법 3: 777 권한
sudo chmod -R 777 output/ 2>/dev/null && echo "✅ 777 권한 성공" || echo "❌ 777 권한 실패"

# 3. 테스트
echo ""
echo "📝 파일 생성 테스트:"
touch output/test_file.txt 2>/dev/null && echo "✅ 파일 생성 성공" || echo "❌ 파일 생성 실패"

# 4. 결과 확인
echo ""
echo "📊 최종 권한 상태:"
ls -la output/
```

## 🎯 권한 문제 해결 체크리스트

### ✅ 기본 확인사항
- [ ] 사용자 정보 확인 (`id`)
- [ ] 그룹 정보 확인 (`getent group`)
- [ ] 현재 권한 확인 (`ls -la`)
- [ ] 파일 생성 테스트 (`touch`)

### ✅ 권한 수정 시도
- [ ] users 그룹 사용 (`chown -R btf_admin:users`)
- [ ] 소유자만 변경 (`chown -R btf_admin`)
- [ ] 777 권한 설정 (`chmod -R 777`)
- [ ] Docker 컨테이너 내부 권한 수정

### ✅ 테스트 및 확인
- [ ] 파일 생성 테스트 성공
- [ ] 권한 변경 확인
- [ ] Docker 컨테이너 내부 접근 가능
- [ ] 데이터 수집 정상 작동

## 🚨 긴급 해결 방법

### 1. 루트 권한으로 강제 수정
```bash
sudo su -
chown -R btf_admin:users /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/output/
chmod -R 755 /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/output/
exit
```

### 2. Docker 컨테이너 재생성
```bash
sudo docker compose down
sudo docker compose up -d
```

### 3. 파일 시스템 권한 무시
```bash
sudo -u root chmod -R 777 output/
sudo -u root chown -R btf_admin:users output/
```

## 📞 지원 정보

### 현재 위치
- **경로**: `/volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer`
- **사용자**: `btf_admin`
- **권한**: `sudo` 사용 가능

### 유용한 명령어
```bash
# 권한 확인
ls -la output/

# 사용자 정보
id btf_admin

# 그룹 정보
groups btf_admin

# 파일 생성 테스트
touch output/test.txt
```

## 🎉 결론

**권한 문제 해결을 위해서는:**

1. **정보 수집**: 사용자 및 그룹 정보 확인
2. **권한 수정**: 올바른 그룹으로 권한 변경
3. **테스트**: 파일 생성 및 권한 확인
4. **Docker 작업**: 컨테이너 내부에서 권한 수정

**이 방법들을 순서대로 시도하여 권한 문제를 해결할 수 있습니다.**

---
*이 문서는 Synology에서 발생하는 권한 문제를 해결하기 위한 종합 가이드입니다.*
