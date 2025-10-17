#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS 연령별 상세 통계 수집 (병렬 처리 8개)
"""

import requests
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

SERVICE_ID = "8806b098778b4d6e84cd"
SECURITY_KEY = "5736845d40cf49ec8da5"
AUTH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"
POP_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json"
AGE_SEX_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/searchpopulation.json"

YEARS = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
OUTPUT = "sgis_enhanced_multiyear_stats.json"
MAX_WORKERS = 8

# 글로벌 통계
stats_lock = threading.Lock()
global_stats = {"collected": 0, "errors": 0, "start_time": time.time()}

def check_net():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except:
        return False

def wait_net():
    while not check_net():
        print(".", end="", flush=True)
        time.sleep(30)

def get_token():
    for i in range(5):
        try:
            wait_net()
            r = requests.get(AUTH_URL, params={
                "consumer_key": SERVICE_ID,
                "consumer_secret": SECURITY_KEY
            }, timeout=10)
            return r.json()['result']['accessToken']
        except:
            time.sleep(5)
    return None

def collect_single(token, year, code):
    """단일 읍면동 데이터 수집"""
    for attempt in range(3):
        try:
            # 기본 인구 통계
            r1 = requests.get(POP_URL, params={
                "accessToken": token,
                "year": year,
                "adm_cd": code
            }, timeout=10)
            d1 = r1.json()
            
            if 'result' not in d1 or not d1['result']:
                return None
            
            base = d1['result'][0]
            
            # 연령별 성별 인구
            r2 = requests.get(AGE_SEX_URL, params={
                "accessToken": token,
                "year": year,
                "adm_cd": code,
                "low_search": "1"
            }, timeout=10)
            d2 = r2.json()
            
            # 연령대 파싱
            ages = {}
            if 'result' in d2:
                for item in d2['result']:
                    suffix = item['adm_cd'][-6:]
                    if int(suffix[:2]) == 2:  # 10세 단위
                        detail = int(suffix[2:])
                        age_idx = detail // 100 if detail >= 100 else detail // 10
                        is_female = detail >= 100
                        
                        age_map = {
                            0: "0-9세", 1: "10-19세", 2: "20-29세", 3: "30-39세",
                            4: "40-49세", 5: "50-59세", 6: "60-69세", 7: "70-79세",
                            8: "80세 이상", 9: "80세 이상"
                        }
                        
                        age = age_map.get(age_idx, "기타")
                        if age not in ages:
                            ages[age] = {"male": 0, "female": 0, "total": 0}
                        
                        pop = int(item['population'])
                        if is_female:
                            ages[age]["female"] = pop
                        else:
                            ages[age]["male"] = pop
                        ages[age]["total"] = ages[age]["male"] + ages[age]["female"]
            
            with stats_lock:
                global_stats["collected"] += 1
            
            return {
                "basic": {
                    "total_population": int(base.get('tot_ppltn', 0)),
                    "avg_age": float(base.get('avg_age', 0)),
                    "population_density": float(base.get('ppltn_dnsty', 0)),
                    "oldage_support_ratio": float(base.get('oldage_suprt_per', 0)),
                    "youth_support_ratio": float(base.get('juv_suprt_per', 0)),
                    "aging_index": float(base.get('aged_child_idx', 0))
                },
                "age_groups": ages
            }
            
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            else:
                with stats_lock:
                    global_stats["errors"] += 1
                return None
    
    return None

def save_data(data):
    """데이터 저장"""
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   SGIS 연령별 상세 통계 병렬 수집 (8개 동시 호출)       ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # 읍면동 코드 로드
    with open('sgis_comprehensive_stats.json', 'r') as f:
        codes = list(json.load(f).get('regions', {}).keys())
    print(f"✅ {len(codes):,}개 읍면동\n")
    
    # 기존 데이터 로드
    try:
        with open(OUTPUT, 'r') as f:
            out = json.load(f)
        print(f"✅ 기존: {len(out.get('regions_by_year', {}))}개 연도\n")
    except:
        out = {
            "metadata": {
                "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "years": YEARS
            },
            "regions_by_year": {}
        }
        print("✅ 신규 수집\n")
    
    # 토큰 발급
    token = get_token()
    if not token:
        print("❌ 토큰 실패")
        return
    print(f"✅ 토큰: {token[:20]}...\n")
    
    token_time = time.time()
    
    # 연도별 수집
    for year in YEARS:
        if year not in out['regions_by_year']:
            out['regions_by_year'][year] = {}
        
        yd = out['regions_by_year'][year]
        done = len(yd)
        
        if done >= len(codes) - 5:
            print(f"⏭️  {year}년 완료 ({done}/{len(codes)})")
            continue
        
        print(f"📅 {year}년 수집 중... (기존:{done}개, 남은:{len(codes)-done}개)")
        
        # 수집할 코드 목록
        todo_codes = [c for c in codes if c not in yd]
        
        # 병렬 수집
        global_stats["collected"] = 0
        global_stats["errors"] = 0
        global_stats["start_time"] = time.time()
        
        collected = 0
        save_counter = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(collect_single, token, year, code): code 
                for code in todo_codes
            }
            
            for future in as_completed(futures):
                code = futures[future]
                try:
                    result = future.result()
                    if result:
                        yd[code] = result
                        collected += 1
                        save_counter += 1
                        
                        # 100개마다 저장 및 진행 표시
                        if save_counter >= 100:
                            save_data(out)
                            elapsed = time.time() - global_stats["start_time"]
                            rate = global_stats["collected"] / (elapsed / 3600) if elapsed > 0 else 0
                            print(f"   📊 {done + collected}/{len(codes)} ({(done+collected)/len(codes)*100:.1f}%) "
                                  f"| 속도: {rate:.0f}개/시간 | 에러: {global_stats['errors']}개")
                            save_counter = 0
                        
                        # 토큰 갱신
                        if time.time() - token_time > 3000:
                            token = get_token()
                            token_time = time.time()
                            print(f"   🔄 토큰 갱신")
                            
                except Exception as e:
                    pass
        
        # 연도 완료 후 저장
        save_data(out)
        print(f"✅ {year}년 완료: {len(yd)}개\n")
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                 ✅ 전체 수집 완료                         ║")
    print("╚════════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
