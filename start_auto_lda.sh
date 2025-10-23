#!/bin/bash
# 자동 LDA 처리 시스템 시작 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/auto_lda.log"
PID_FILE="$SCRIPT_DIR/auto_lda.pid"

echo "🚀 자동 LDA 처리 시스템 시작"
echo "📁 작업 디렉토리: $SCRIPT_DIR"
echo "📝 로그 파일: $LOG_FILE"

# 기존 프로세스 확인
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️ 기존 프로세스가 실행 중입니다 (PID: $OLD_PID)"
        echo "🔄 기존 프로세스를 종료하고 새로 시작합니다..."
        kill "$OLD_PID" 2>/dev/null
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# Python 의존성 확인
if ! python3 -c "import requests, psutil" 2>/dev/null; then
    echo "📦 필요한 패키지 설치 중..."
    pip3 install requests psutil
fi

# 자동 LDA 처리 시작
cd "$SCRIPT_DIR"
python3 auto_lda_processor.py start &

# PID 저장
echo $! > "$PID_FILE"

echo "✅ 자동 LDA 처리 시스템이 백그라운드에서 시작되었습니다"
echo "📊 상태 확인: python3 auto_lda_processor.py status"
echo "🛑 중지: python3 auto_lda_processor.py stop"
echo "📝 로그 확인: tail -f $LOG_FILE"
