#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상세 데이터 수집 실시간 모니터
"""

import json
import time
import os
from datetime import datetime, timedelta

OUTPUT_FILE = "sgis_enhanced_multiyear_stats.json"
TOTAL_YEARS = 9
TOTAL_REGIONS = 3558

def clear_screen():
    """화면 클리어"""
    os.system('clear')

def get_collection_status():
    """수집 상태 조회"""
    try:
        with open(OUTPUT_FILE, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        # JSON 파일 손상 시 백업에서 복구 시도
        try:
            with open(OUTPUT_FILE + '.backup', 'r') as f:
                data = json.load(f)
            return data
        except:
            return None
    except Exception:
        return None

def format_time(seconds):
    """시간 포맷팅"""
    if seconds < 60:
        return f"{int(seconds)}초"
    elif seconds < 3600:
        return f"{int(seconds/60)}분"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}시간 {minutes}분"
    else:
        days = int(seconds / 86400)
        hours = int((seconds % 86400) / 3600)
        return f"{days}일 {hours}시간"

def main():
    start_time = time.time()
    last_total = 0
    
    while True:
        clear_screen()
        
        print("╔════════════════════════════════════════════════════════════╗")
        print("║       📊 연령별 상세 통계 수집 실시간 모니터             ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        data = get_collection_status()
        
        if not data:
            print("⏳ 수집 시작 대기 중...")
            time.sleep(5)
            continue
        
        years_data = data.get('regions_by_year', {})
        total_collected = sum(len(regions) for regions in years_data.values())
        total_target = TOTAL_YEARS * TOTAL_REGIONS
        
        # 진행률
        overall_percent = (total_collected / total_target) * 100
        
        print("📅 연도별 수집 현황:")
        for year in sorted(years_data.keys()):
            count = len(years_data[year])
            percent = (count / TOTAL_REGIONS) * 100
            status = "✅" if count >= TOTAL_REGIONS - 5 else "🔄"
            bar_len = int(percent / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"{status} {year}: [{bar}] {percent:5.1f}% ({count:,}개)")
        
        print()
        print(f"📊 전체 진행률: {overall_percent:.2f}%")
        print(f"   수집: {total_collected:,} / {total_target:,}개")
        print()
        
        # 속도 계산
        elapsed = time.time() - start_time
        if elapsed > 60:
            current_rate = (total_collected - last_total) / (elapsed / 3600) if elapsed > 0 else 0
            
            if current_rate > 0:
                remaining = total_target - total_collected
                eta_hours = remaining / current_rate
                completion_time = datetime.now() + timedelta(hours=eta_hours)
                
                print(f"⚡ 수집 속도: {int(current_rate)}개/시간")
                print(f"⏱️  예상 완료: {format_time(eta_hours * 3600)}")
                print(f"🎯 완료 시각: {completion_time.strftime('%m월 %d일 %H:%M')}")
                print()
        
        # 네트워크 상태
        try:
            import subprocess
            result = subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'], 
                                  capture_output=True, timeout=2)
            if result.returncode == 0:
                print("🌐 네트워크: ✅ 정상")
            else:
                print("🌐 네트워크: ⚠️ 불안정")
        except:
            print("🌐 네트워크: ❓ 확인 불가")
        
        print()
        print("─" * 60)
        print("💡 새로고침: 1분마다 | 종료: Ctrl+C")
        print()
        
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ 모니터 종료")

