#!/bin/bash
# 실시간 모니터링 (1초마다 갱신)

cd /Users/hopidad/Desktop/workspace

while true; do
    clear
    echo "=========================================="
    echo "📊 다년도 데이터 수집 실시간 모니터링"
    echo "=========================================="
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # PID 확인
    if [ -f "collector_robust.pid" ]; then
        PID=$(cat collector_robust.pid)
        
        if ps -p $PID > /dev/null 2>&1; then
            echo "🔄 프로세스: ✅ 실행 중 (PID: $PID)"
            ELAPSED=$(ps -p $PID -o etime | tail -1 | xargs)
            CPU=$(ps -p $PID -o %cpu | tail -1 | xargs)
            MEM=$(ps -p $PID -o rss | tail -1 | xargs)
            MEM_MB=$(echo "scale=1; $MEM / 1024" | bc)
            
            echo "  ⏱️  실행 시간: $ELAPSED"
            echo "  💻 CPU: $CPU%"
            echo "  🧠 메모리: ${MEM_MB}MB"
        else
            echo "❌ 프로세스 중단됨"
        fi
    fi
    
    echo ""
    echo "=========================================="
    echo "📈 진행 상황"
    echo "=========================================="
    
    # 완료된 연도
    if [ -f "multiyear_progress.json" ]; then
        COMPLETED=$(jq -r '.completed_years | length' multiyear_progress.json 2>/dev/null)
        echo "✅ 완료된 연도: $COMPLETED개"
        jq -r '.completed_years[]' multiyear_progress.json 2>/dev/null | while read year; do
            COUNT=$(jq -r ".regions_by_year[\"$year\"] | keys | length" sgis_multiyear_stats_partial.json 2>/dev/null)
            echo "  ✓ $year: ${COUNT}개 읍면동"
        done
    fi
    
    echo ""
    
    # 현재 작업
    if [ -f "sgis_multiyear_robust.log" ]; then
        CURRENT_YEAR=$(grep "📅.*년 데이터 수집 중" sgis_multiyear_robust.log | tail -1 | grep -o "[0-9]\{4\}")
        CURRENT_SIDO=$(grep "📍" sgis_multiyear_robust.log | tail -1 | grep -o "📍.*" | sed 's/✓.*//' | xargs)
        
        if [ ! -z "$CURRENT_YEAR" ]; then
            echo "🔄 현재 작업: $CURRENT_YEAR년"
            echo "  └─ $CURRENT_SIDO"
        fi
    fi
    
    echo ""
    echo "=========================================="
    echo "💾 데이터 파일"
    echo "=========================================="
    
    if [ -f "sgis_multiyear_stats_partial.json" ]; then
        SIZE=$(ls -lh sgis_multiyear_stats_partial.json | awk '{print $5}')
        
        # Python으로 정밀 계산
        python3 << 'PYEOF'
import json

with open('sgis_multiyear_stats_partial.json', 'r') as f:
    data = json.load(f)

TOTAL_YEARS = 9
TARGET_PER_YEAR = 3553
TOTAL_TARGET = TOTAL_YEARS * TARGET_PER_YEAR

years_data = data.get('regions_by_year', {})
total_collected = sum(len(regions) for regions in years_data.values())

overall_progress = (total_collected / TOTAL_TARGET) * 100
year_progress = (len(years_data) / TOTAL_YEARS) * 100

print(f"  파일 크기: {data.get('metadata', {}).get('collection_date', 'N/A')}")
print(f"  저장된 연도: {len(years_data)}개")
print(f"  연도 진행률: {year_progress:.3f}%")
print(f"  읍면동 진행률: {overall_progress:.3f}%")
print()

# 진행바
filled = int(overall_progress * 40 / 100)
bar = '█' * filled + '░' * (40 - filled)
print(f"  [{bar}] {overall_progress:.3f}%")
print()

print("  연도별 상세:")
for year, regions in sorted(years_data.items()):
    count = len(regions)
    percent = (count / TARGET_PER_YEAR) * 100
    print(f"    {year}: {percent:.3f}% ({count:,}개)")
PYEOF
    fi
    
    echo ""
    echo "=========================================="
    echo "📝 최근 로그 (최근 5줄)"
    echo "=========================================="
    
    if [ -f "sgis_multiyear_robust.log" ]; then
        tail -5 sgis_multiyear_robust.log | sed 's/^/  /'
    fi
    
    echo ""
    echo "=========================================="
    echo "🔄 자동 갱신 중... (Ctrl+C로 종료)"
    echo "=========================================="
    
    sleep 30
done

