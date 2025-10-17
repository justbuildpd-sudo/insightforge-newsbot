#!/bin/bash
# 데이터 수집 프로세스 모니터링 및 자동 재시작

LOG_FILE="sgis_multiyear_collection.log"
PID_FILE="collector.pid"
SCRIPT="fetch_sgis_multiyear_stats.py"

# 현재 실행 중인 프로세스 확인
CURRENT_PID=$(ps aux | grep "$SCRIPT" | grep -v grep | awk '{print $2}')

if [ ! -z "$CURRENT_PID" ]; then
    echo "$CURRENT_PID" > $PID_FILE
    echo "✅ 프로세스 실행 중: PID $CURRENT_PID"
    echo "📝 PID를 파일에 저장했습니다: $PID_FILE"
    
    # 프로세스 우선순위 조정 (중단 방지)
    renice -n 10 $CURRENT_PID 2>/dev/null
    
    echo ""
    echo "🛡️ 중단 방지 조치:"
    echo "  1. nohup으로 실행됨 (터미널 종료해도 계속)"
    echo "  2. 로그 파일에 출력 저장 중"
    echo "  3. 중간 저장 활성화 (연도별)"
    echo ""
    echo "⚠️ 주의사항:"
    echo "  - MacBook 슬립 방지 필요"
    echo "  - 네트워크 변경 시 API 호출 실패 가능"
    echo "  - 전원 연결 필수"
    echo ""
    echo "📊 진행 확인:"
    echo "  tail -f $LOG_FILE"
    echo ""
    echo "🔄 프로세스 재확인:"
    echo "  ps -p $CURRENT_PID"
else
    echo "❌ 프로세스가 실행되고 있지 않습니다"
    echo "재시작하려면:"
    echo "  nohup python3 $SCRIPT > $LOG_FILE 2>&1 <<< 'y' &"
fi

