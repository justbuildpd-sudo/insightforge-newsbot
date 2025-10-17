#!/bin/bash
# 상세 모니터링 (실시간 갱신)

cd /Users/hopidad/Desktop/workspace

while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║       📊 다년도 데이터 수집 상세 모니터링                 ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # ============================================
    # 프로세스 상태
    # ============================================
    echo "┌─────────────────────────────────────────┐"
    echo "│ 🖥️  프로세스 상태                        │"
    echo "└─────────────────────────────────────────┘"
    
    if [ -f "collector_robust.pid" ]; then
        PID=$(cat collector_robust.pid)
        
        if ps -p $PID > /dev/null 2>&1; then
            ELAPSED=$(ps -p $PID -o etime= | xargs)
            CPU=$(ps -p $PID -o %cpu= | xargs)
            MEM=$(ps -p $PID -o rss= | xargs)
            MEM_MB=$(echo "scale=1; $MEM / 1024" | bc)
            
            echo "  상태: ✅ 실행 중"
            echo "  PID: $PID"
            echo "  실행 시간: $ELAPSED"
            echo "  CPU 사용률: $CPU%"
            echo "  메모리: ${MEM_MB}MB"
        else
            echo "  상태: ❌ 중단됨"
        fi
    else
        echo "  ❌ PID 파일 없음"
    fi
    
    echo ""
    
    # ============================================
    # 수집 진행률
    # ============================================
    echo "┌─────────────────────────────────────────┐"
    echo "│ 📈 수집 진행률                           │"
    echo "└─────────────────────────────────────────┘"
    
    if [ -f "sgis_multiyear_stats_partial.json" ]; then
        # Python으로 정밀 계산
        python3 << 'PYEOF'
import json
import sys

with open('sgis_multiyear_stats_partial.json', 'r') as f:
    data = json.load(f)

TOTAL_YEARS = 9
TARGET_PER_YEAR = 3553
TOTAL_TARGET = TOTAL_YEARS * TARGET_PER_YEAR

years_data = data.get('regions_by_year', {})
total_collected = sum(len(regions) for regions in years_data.values())

overall_progress = (total_collected / TOTAL_TARGET) * 100
year_progress = (len(years_data) / TOTAL_YEARS) * 100

print(f"  연도 진행률: {len(years_data)} / {TOTAL_YEARS} = {year_progress:.3f}%")
print(f"  읍면동 진행률: {total_collected:,} / {TOTAL_TARGET:,} = {overall_progress:.3f}%")
print()

# 진행바
filled = int(overall_progress * 45 / 100)
bar = '█' * filled + '░' * (45 - filled)
print(f"  [{bar}] {overall_progress:.3f}%")
print()

print("  연도별 상세:")
for year, regions in sorted(years_data.items()):
    count = len(regions)
    percent = (count / TARGET_PER_YEAR) * 100
    year_bar_filled = int(percent * 20 / 100)
    year_bar = '█' * year_bar_filled + '░' * (20 - year_bar_filled)
    print(f"    {year}: [{year_bar}] {percent:.3f}% ({count:,}개)")
PYEOF
    fi
    
    echo ""
    
    # ============================================
    # 현재 작업
    # ============================================
    echo "┌─────────────────────────────────────────┐"
    echo "│ 🔄 현재 작업                             │"
    echo "└─────────────────────────────────────────┘"
    
    if [ -f "sgis_multiyear_robust.log" ]; then
        CURRENT_YEAR=$(grep "📅.*년 데이터 수집 중" sgis_multiyear_robust.log | tail -1)
        echo "  $CURRENT_YEAR"
        
        # 최근 완료된 시도 3개
        echo ""
        echo "  최근 완료:"
        grep "📍.*✓" sgis_multiyear_robust.log | tail -3 | while read line; do
            SIDO=$(echo "$line" | grep -o "📍[^✓]*" | sed 's/📍//')
            echo "    ✓$SIDO"
        done
        
        # 현재 진행 중인 시도
        echo ""
        echo "  진행 중:"
        CURRENT=$(tail -1 sgis_multiyear_robust.log)
        if [[ $CURRENT == *"📍"* ]]; then
            echo "    $CURRENT"
        fi
    fi
    
    echo ""
    
    # ============================================
    # 네트워크 상태
    # ============================================
    echo "┌─────────────────────────────────────────┐"
    echo "│ 🌐 네트워크 상태                         │"
    echo "└─────────────────────────────────────────┘"
    
    # 인터넷 연결 확인
    if curl -s --max-time 2 https://www.google.com > /dev/null 2>&1; then
        echo "  인터넷: ✅ 연결됨"
    else
        echo "  인터넷: ❌ 끊김"
    fi
    
    # SGIS API 연결 확인
    if curl -s --max-time 2 https://sgisapi.kostat.go.kr > /dev/null 2>&1; then
        echo "  SGIS API: ✅ 접속 가능"
    else
        echo "  SGIS API: ❌ 접속 불가"
    fi
    
    # 최근 에러 확인
    ERROR_COUNT=$(grep -c "오류\|실패\|error\|Error" sgis_multiyear_robust.log 2>/dev/null)
    if [ ! -z "$ERROR_COUNT" ] && [ $ERROR_COUNT -gt 0 ]; then
        echo "  최근 에러: ⚠️ ${ERROR_COUNT}건"
    else
        echo "  에러: ✅ 없음"
    fi
    
    echo ""
    
    # ============================================
    # 예상 완료 시간
    # ============================================
    echo "┌─────────────────────────────────────────┐"
    echo "│ ⏱️  예상 완료 시간                        │"
    echo "└─────────────────────────────────────────┘"
    
    if [ ! -z "$TOTAL_YEARS" ] && [ ! -z "$ELAPSED" ]; then
        REMAINING=$((9 - TOTAL_YEARS))
        
        echo "  남은 연도: ${REMAINING}개"
        echo "  현재 속도: ${TOTAL_YEARS}개 연도 / $ELAPSED"
        
        # 간단한 예상 시간 계산
        if [ $TOTAL_YEARS -gt 0 ]; then
            echo "  예상: 내일 오후 ~ 모레 오전"
        fi
    fi
    
    echo ""
    echo "┌─────────────────────────────────────────┐"
    echo "│ 💡 TIP: Ctrl+C로 종료                    │"
    echo "└─────────────────────────────────────────┘"
    
    sleep 30
done

