#!/bin/bash
# 네트워크 연결 시 자동 LDA 처리 시작 스크립트
# 이 스크립트를 네트워크 연결 시 자동으로 실행되도록 설정

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/network_auto_lda.log"

echo "🌐 네트워크 연결 감지 - 자동 LDA 처리 시작" >> "$LOG_FILE"
echo "📅 $(date)" >> "$LOG_FILE"

# 네트워크 연결 확인
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo "✅ 인터넷 연결 확인됨" >> "$LOG_FILE"
    
    # 타겟 네트워크 확인 (192.168.219.x)
    if ifconfig | grep -q "192.168.219"; then
        echo "✅ 타겟 네트워크에 연결됨 (192.168.219.x)" >> "$LOG_FILE"
        
        # 자동 LDA 처리 시작
        cd "$SCRIPT_DIR"
        ./start_auto_lda.sh >> "$LOG_FILE" 2>&1 &
        
        echo "🚀 자동 LDA 처리 시스템 시작됨" >> "$LOG_FILE"
    else
        echo "❌ 타겟 네트워크에 연결되지 않음" >> "$LOG_FILE"
    fi
else
    echo "❌ 인터넷 연결 없음" >> "$LOG_FILE"
fi

echo "---" >> "$LOG_FILE"
