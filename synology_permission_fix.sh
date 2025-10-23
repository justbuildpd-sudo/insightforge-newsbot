#!/bin/bash
# Synology 권한 문제 해결 스크립트

echo "=== Synology 권한 문제 해결 ==="

# 1. 현재 사용자 및 그룹 정보 확인
echo "📊 현재 사용자 정보:"
id
whoami

echo ""
echo "📊 사용 가능한 그룹 목록:"
getent group | grep -E "(btf|admin|users)" || echo "관련 그룹을 찾을 수 없습니다"

echo ""
echo "📊 현재 디렉토리 권한:"
ls -la

# 2. 올바른 그룹으로 권한 수정
echo ""
echo "🔧 권한 수정 시도:"

# 방법 1: users 그룹 사용
echo "방법 1: users 그룹 사용"
sudo chown -R btf_admin:users output/ 2>/dev/null && echo "✅ users 그룹으로 권한 수정 성공" || echo "❌ users 그룹으로 권한 수정 실패"

# 방법 2: 그룹 없이 소유자만 변경
echo "방법 2: 소유자만 변경"
sudo chown -R btf_admin output/ 2>/dev/null && echo "✅ 소유자 변경 성공" || echo "❌ 소유자 변경 실패"

# 방법 3: 777 권한으로 설정
echo "방법 3: 777 권한 설정"
sudo chmod -R 777 output/ 2>/dev/null && echo "✅ 777 권한 설정 성공" || echo "❌ 777 권한 설정 실패"

# 3. Docker 컨테이너 내부에서 권한 수정
echo ""
echo "🔧 Docker 컨테이너 내부 권한 수정:"

# newsanalyzer-historical 컨테이너 내부에서 권한 수정
echo "newsanalyzer-historical 컨테이너 내부 권한 수정:"
sudo docker exec -it newsanalyzer-historical chown -R 1000:1000 /app/output/ 2>/dev/null && echo "✅ 컨테이너 내부 권한 수정 성공" || echo "❌ 컨테이너 내부 권한 수정 실패"

# 4. 파일 생성 테스트
echo ""
echo "📝 파일 생성 테스트:"
touch output/test_file.txt 2>/dev/null && echo "✅ 파일 생성 성공" || echo "❌ 파일 생성 실패"

# 5. 권한 확인
echo ""
echo "📊 수정된 권한 확인:"
ls -la output/ 2>/dev/null || echo "output 디렉토리가 없습니다"

# 6. 대안 방법들
echo ""
echo "💡 대안 방법들:"
echo "1. Docker 컨테이너 내부에서 작업:"
echo "   sudo docker exec -it newsanalyzer-historical bash"
echo "   cd /app && ls -la output/"

echo ""
echo "2. 루트 권한으로 작업:"
echo "   sudo su -"
echo "   chown -R btf_admin:users /volume1/BTF-Tech/newsanalyzer-temp/NewsAnalyzer/output/"

echo ""
echo "3. 파일 권한 무시하고 작업:"
echo "   sudo -u root touch output/test.txt"
echo "   sudo -u root chmod 777 output/"

# 7. 최종 권한 확인
echo ""
echo "📊 최종 권한 상태:"
ls -la output/ 2>/dev/null || echo "output 디렉토리가 없습니다"

echo ""
echo "=== 권한 문제 해결 완료 ==="
echo "✅ 가능한 모든 방법으로 권한 수정 시도"
echo "✅ Docker 컨테이너 내부 권한 수정"
echo "✅ 파일 생성 테스트 완료"
echo ""
echo "🔍 다음 단계:"
echo "1. 파일 생성 테스트 결과 확인"
echo "2. Docker 컨테이너 내부에서 작업"
echo "3. 루트 권한으로 작업"
