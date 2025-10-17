#!/bin/bash
# 다년도 데이터 수집 모니터링

clear
echo "=========================================="
echo "📊 다년도 데이터 수집 모니터링"
echo "=========================================="
echo ""

# PID 확인
if [ -f "collector_robust.pid" ]; then
    PID=$(cat collector_robust.pid)
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔄 프로세스 상태: ✅ 실행 중 (PID: $PID)"
        ELAPSED=$(ps -p $PID -o etime | tail -1 | xargs)
        CPU=$(ps -p $PID -o %cpu | tail -1 | xargs)
        MEM=$(ps -p $PID -o rss | tail -1 | xargs)
        MEM_MB=$(echo "scale=1; $MEM / 1024" | bc)
        
        echo "  실행 시간: $ELAPSED"
        echo "  CPU 사용률: $CPU%"
        echo "  메모리: ${MEM_MB}MB"
    else
        echo "❌ 프로세스 중단됨 (PID: $PID)"
        echo ""
        echo "재시작하려면:"
        echo "  cd /Users/hopidad/Desktop/workspace"
        echo "  nohup python3 fetch_sgis_multiyear_robust.py > sgis_multiyear_robust.log 2>&1 &"
    fi
else
    echo "❌ PID 파일을 찾을 수 없습니다"
fi

echo ""
echo "=========================================="
echo "📈 수집 진행 상황"
echo "=========================================="

# 로그에서 진행 상황 추출
if [ -f "sgis_multiyear_robust.log" ]; then
    echo ""
    echo "✅ 완료된 연도:"
    grep "✅.*년:.*개 읍면동 수집" sgis_multiyear_robust.log | while read line; do
        echo "  $line"
    done
    
    echo ""
    echo "🔄 현재 작업:"
    CURRENT_YEAR=$(grep "📅.*년 데이터 수집 중" sgis_multiyear_robust.log | tail -1)
    echo "  $CURRENT_YEAR"
    
    CURRENT_SIDO=$(grep "📍" sgis_multiyear_robust.log | tail -1 | sed 's/✓.*//' | xargs)
    echo "  $CURRENT_SIDO"
fi

echo ""
echo "=========================================="
echo "💾 데이터 파일"
echo "=========================================="

if [ -f "sgis_multiyear_stats_partial.json" ]; then
    SIZE=$(ls -lh sgis_multiyear_stats_partial.json | awk '{print $5}')
    YEARS=$(jq '.regions_by_year | keys | length' sgis_multiyear_stats_partial.json 2>/dev/null)
    echo "  중간 저장: $SIZE ($YEARS개 연도)"
    
    echo ""
    echo "  연도별 수집 개수:"
    jq -r '.regions_by_year | to_entries[] | "    \(.key): \(.value | keys | length)개"' sgis_multiyear_stats_partial.json 2>/dev/null
else
    echo "  중간 저장 파일 없음"
fi

if [ -f "multiyear_progress.json" ]; then
    echo ""
    echo "  완료된 연도:"
    jq -r '.completed_years[]' multiyear_progress.json 2>/dev/null | while read year; do
        echo "    ✓ $year"
    done
fi

echo ""
echo "=========================================="
echo "📊 예상 진행률"
echo "=========================================="

TOTAL_YEARS=9
if [ ! -z "$YEARS" ]; then
    PROGRESS=$(echo "scale=1; $YEARS * 100 / $TOTAL_YEARS" | bc)
    echo "  완료: $YEARS / $TOTAL_YEARS 연도 (${PROGRESS}%)"
    
    REMAINING=$((TOTAL_YEARS - YEARS))
    if [ $REMAINING -gt 0 ]; then
        echo "  남은 연도: $REMAINING개"
        
        if [ ! -z "$ELAPSED" ]; then
            # 시간 파싱 (HH:MM:SS 또는 MM:SS 형식)
            if [[ $ELAPSED == *-* ]]; then
                # DD-HH:MM:SS 형식
                ELAPSED_CLEAN=$(echo $ELAPSED | sed 's/.*-//')
            else
                ELAPSED_CLEAN=$ELAPSED
            fi
            
            echo "  현재 속도: $YEARS개 연도 / $ELAPSED"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "🔧 명령어"
echo "=========================================="
echo "  실시간 로그: tail -f sgis_multiyear_robust.log"
echo "  상태 확인: bash monitor_multiyear.sh"
echo "  프로세스 중단: kill \$(cat collector_robust.pid)"
echo "=========================================="

