#!/bin/bash

echo "=========================================="
echo "🔍 웹 서비스 상태 확인"
echo "=========================================="
echo ""

echo "📡 백엔드 상태:"
curl -s http://localhost:8000/api/national/sido > /dev/null 2>&1
if [ $? -eq 0 ]; then
    TOTAL=$(curl -s http://localhost:8000/api/national/sido | jq -r '.total')
    echo "  ✅ 정상 작동 (시도 ${TOTAL}개)"
else
    echo "  ❌ 연결 실패"
fi
echo ""

echo "🌐 프론트엔드 상태:"
curl -s http://localhost:3000 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ 정상 작동"
else
    echo "  ❌ 연결 실패"
fi
echo ""

echo "📄 파일 확인:"
echo "  index.html: $(ls -lh /Users/hopidad/Desktop/workspace/insightforge-web/frontend/index.html | awk '{print $5}')"
echo "  app.js: $(ls -lh /Users/hopidad/Desktop/workspace/insightforge-web/frontend/app.js | awk '{print $5}')"
echo ""

echo "🔌 프로세스:"
ps aux | grep "python3.*main.py" | grep -v grep | head -1 && echo "  ✅ 백엔드 실행 중" || echo "  ❌ 백엔드 중단"
ps aux | grep "python3.*http.server" | grep -v grep | head -1 && echo "  ✅ 프론트엔드 실행 중" || echo "  ❌ 프론트엔드 중단"
echo ""

echo "🎯 다음 단계:"
echo "  1. 브라우저에서 http://localhost:3000 열기"
echo "  2. F12 또는 Cmd+Option+I로 개발자 도구 열기"
echo "  3. Console 탭에서 로그 확인"
echo "=========================================="

