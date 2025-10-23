#!/bin/bash
# Synology NewsAnalyzer 상태 확인 및 문제 해결 명령어

echo "=== Synology NewsAnalyzer 상태 확인 ==="

# 1. Docker 컨테이너 상태 확인
echo "📊 Docker 컨테이너 상태:"
sudo docker ps -a | grep newsanalyzer

echo ""
echo "📊 Docker Compose 상태:"
sudo docker compose ps

echo ""
echo "📊 컨테이너 리소스 사용량:"
sudo docker stats --no-stream | grep newsanalyzer

echo ""
echo "📊 NewsAnalyzer 로그 (최근 50줄):"
sudo docker compose logs --tail=50 newsanalyzer-historical

echo ""
echo "📊 API 관리 로그:"
sudo docker compose logs --tail=20 api-management

echo ""
echo "📊 데이터 파일 확인:"
ls -la output/lda_results/ 2>/dev/null || echo "❌ LDA 결과 디렉토리가 없습니다"

echo ""
echo "📊 API 설정 확인:"
cat multi_api_config.json 2>/dev/null || echo "❌ API 설정 파일이 없습니다"

echo ""
echo "📊 시스템 리소스:"
free -h
df -h /volume1

echo ""
echo "=== 문제 해결 명령어 ==="
echo "1. 컨테이너 재시작:"
echo "   sudo docker compose restart"

echo ""
echo "2. 컨테이너 완전 재시작:"
echo "   sudo docker compose down"
echo "   sudo docker compose up -d"

echo ""
echo "3. API 리셋:"
echo "   curl -X POST http://localhost:5001/api/reset"

echo ""
echo "4. 로그 실시간 모니터링:"
echo "   sudo docker compose logs -f newsanalyzer-historical"
