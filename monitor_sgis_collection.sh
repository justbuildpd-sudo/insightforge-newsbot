#!/bin/bash
# SGIS 통계 수집 진행 상황 모니터링

echo "=========================================="
echo "📊 SGIS 통계 수집 진행 상황"
echo "=========================================="

LOG_FILE="sgis_stats_collection.log"
PARTIAL_FILE="sgis_comprehensive_stats_partial.json"

if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "📝 최근 로그 (마지막 20줄):"
    echo "------------------------------------------"
    tail -20 "$LOG_FILE"
    echo ""
    echo "------------------------------------------"
    echo ""
    
    # 진행률 계산
    TOTAL_REGIONS=3558
    if [ -f "$PARTIAL_FILE" ]; then
        COLLECTED=$(jq '.metadata.total_regions // 0' "$PARTIAL_FILE" 2>/dev/null || echo "0")
        PROGRESS=$(echo "scale=2; $COLLECTED * 100 / $TOTAL_REGIONS" | bc)
        echo "📈 진행률: $COLLECTED / $TOTAL_REGIONS 지역 ($PROGRESS%)"
    fi
    
    echo ""
    echo "🔄 프로세스 상태:"
    ps aux | grep fetch_sgis_stats.py | grep -v grep || echo "   프로세스 종료됨"
    
    echo ""
    echo "💾 파일 크기:"
    if [ -f "$PARTIAL_FILE" ]; then
        ls -lh "$PARTIAL_FILE" | awk '{print "   중간 저장: " $5}'
    fi
    if [ -f "sgis_comprehensive_stats.json" ]; then
        ls -lh sgis_comprehensive_stats.json | awk '{print "   최종 파일: " $5}'
    fi
else
    echo "❌ 로그 파일을 찾을 수 없습니다."
fi

echo ""
echo "=========================================="
echo "명령어:"
echo "  진행 확인: bash monitor_sgis_collection.sh"
echo "  실시간 로그: tail -f sgis_stats_collection.log"
echo "  프로세스 중단: pkill -f fetch_sgis_stats.py"
echo "=========================================="

