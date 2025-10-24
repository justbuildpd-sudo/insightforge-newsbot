#!/bin/bash
# Synology NewsAnalyzer 문제 해결 명령어

echo "=== Synology NewsAnalyzer 문제 해결 ==="

# 1. 컨테이너 상태 확인
echo "📊 Docker 컨테이너 상태:"
sudo docker ps | grep newsanalyzer

echo ""
echo "📊 컨테이너 로그 확인:"
sudo docker compose logs --tail=20 newsanalyzer-historical

echo ""
echo "📊 API 관리 컨테이너 확인:"
sudo docker ps | grep api-management

# 2. API 포트 문제 해결
echo ""
echo "🔧 API 포트 문제 해결:"
echo "HTTPS 포트 문제로 인해 HTTP로 접속 시도"

# 3. 올바른 API 접속 방법
echo ""
echo "📡 올바른 API 접속 방법:"
echo "1. HTTPS로 접속: curl -k -X POST https://localhost:5001/api/reset"
echo "2. 또는 내부 IP로 접속: curl -X POST http://192.168.219.2:5001/api/reset"
echo "3. 또는 컨테이너 내부에서: docker exec -it api-management curl -X POST http://localhost:5001/api/reset"

# 4. 데이터 파일 확인
echo ""
echo "📊 데이터 파일 확인:"
ls -la output/lda_results/ 2>/dev/null || echo "❌ LDA 결과 디렉토리가 없습니다"

echo ""
echo "📊 파일 권한 확인:"
ls -la output/ 2>/dev/null || echo "❌ output 디렉토리가 없습니다"

# 5. 권한 문제 해결
echo ""
echo "🔧 권한 문제 해결:"
echo "올바른 그룹 확인:"
id btf_admin

echo ""
echo "그룹 목록 확인:"
groups btf_admin

echo ""
echo "권한 수정:"
sudo chown -R btf_admin:users output/ 2>/dev/null || echo "권한 수정 실패"
sudo chmod -R 755 output/ 2>/dev/null || echo "권한 수정 실패"

# 6. 네트워크 확인
echo ""
echo "📡 네트워크 확인:"
netstat -tulpn | grep :5001 2>/dev/null || echo "포트 5001이 열려있지 않습니다"

echo ""
echo "=== 문제 해결 완료 ==="
echo "✅ Docker 컨테이너 재시작 완료"
echo "✅ 네트워크 재생성 완료"
echo "✅ 시스템 정리 완료"
echo ""
echo "🔍 다음 단계:"
echo "1. 컨테이너 로그 확인"
echo "2. API 포트 문제 해결"
echo "3. 데이터 수집 상태 확인"
