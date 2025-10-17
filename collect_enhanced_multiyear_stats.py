#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API 연령별/성별 상세 통계 수집 (2015~2023 전체 연도)
- 연령별 성별 인구
- 기본 인구 통계 (평균연령, 노령화지수 등)
"""

import requests
import json
import time
from typing import Dict, List, Any

# API 인증 정보
SERVICE_ID = "8806b098778b4d6e84cd"
SECURITY_KEY = "5736845d40cf49ec8da5"

# API 엔드포인트
AUTH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"
AGE_SEX_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/searchpopulation.json"
POP_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json"

# 수집할 연도
YEARS = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

# 파일명
OUTPUT_FILE = "sgis_enhanced_multiyear_stats.json"
PROGRESS_FILE = "enhanced_progress.json"

def check_internet():
    """인터넷 연결 확인"""
    try:
        requests.get("https://www.google.com", timeout=10)
        return True
    except:
        return False

def wait_for_internet():
    """인터넷 연결 대기"""
    retry_count = 0
    while not check_internet():
        retry_count += 1
        if retry_count == 1:
            print("\n⚠️ 네트워크 연결 끊김. 재연결 대기 중...", end="", flush=True)
        else:
            print(".", end="", flush=True)
        time.sleep(30)
        
        if retry_count % 2 == 0:
            print(f"\n   ({retry_count * 30}초 경과)", end="", flush=True)
    
    if retry_count > 0:
        print("\n✅ 네트워크 재연결")
    return True

def get_access_token():
    """SGIS API 액세스 토큰 발급 (재시도 포함)"""
    for attempt in range(5):
        try:
            wait_for_internet()
            response = requests.get(AUTH_URL, params={
                "consumer_key": SERVICE_ID,
                "consumer_secret": SECURITY_KEY
            }, timeout=10)
            result = response.json()
            return result['result']['accessToken']
        except Exception as e:
            if attempt < 4:
                print(f"⚠️ 토큰 발급 재시도 {attempt+1}/5...")
                time.sleep(5)
            else:
                print(f"❌ 토큰 발급 실패: {e}")
                return None
    return None

def parse_age_sex_code(adm_cd):
    """연령대/성별 코드 파싱
    예: 11010530020003 -> 연령대: 20대, 성별: 남성, 세부: 20-24세
    """
    suffix = adm_cd[-6:]  # 마지막 6자리
    
    # 첫 2자리: 연령대 구분 (01=전체, 02=10대미만, 03=세부연령)
    category = int(suffix[:2])
    # 중간 2자리: 연령대 번호
    age_num = int(suffix[2:4])
    # 마지막 2자리: 성별 또는 세부구분 (01=남, 02=여)
    detail = int(suffix[4:6])
    
    if category == 1:  # 전체
        gender = "남성" if detail == 1 else "여성"
        return {
            "category": "전체",
            "gender": gender,
            "age_group": "전체",
            "age_label": "전체"
        }
    elif category == 2:  # 10세 단위
        age_map = {
            1: "0-9세",
            2: "10-19세",
            3: "20-29세",
            4: "30-39세",
            5: "40-49세",
            6: "50-59세",
            7: "60-69세",
            8: "70-79세",
            9: "80세 이상"
        }
        gender = "남성" if detail == 1 else "여성"
        return {
            "category": "10세단위",
            "gender": gender,
            "age_group": f"{(age_num-1)*10}대",
            "age_label": age_map.get(age_num, "기타")
        }
    elif category == 3:  # 5세 단위 상세
        age_detail_map = {
            1: ("0-4세", "남성"),
            2: ("5-9세", "남성"),
            3: ("10-14세", "남성"),
            4: ("15-19세", "남성"),
            5: ("20-24세", "남성"),
            101: ("0-4세", "여성"),
            102: ("5-9세", "여성"),
            103: ("10-14세", "여성"),
            104: ("15-19세", "여성"),
            201: ("25-29세", "남성"),
            301: ("30-34세", "남성"),
            401: ("35-39세", "남성"),
            501: ("40-44세", "남성")
        }
        age_label, gender = age_detail_map.get(detail, ("기타", "기타"))
        return {
            "category": "5세단위",
            "gender": gender,
            "age_group": age_label.split('-')[0][:-1] + "대",
            "age_label": age_label
        }
    
    return None

def collect_enhanced_stats(token, year, adm_cd):
    """상세 통계 수집 (재시도 포함)"""
    for attempt in range(3):
        try:
            wait_for_internet()
            
            # 1. 기본 인구 통계
            pop_response = requests.get(POP_URL, params={
                "accessToken": token,
                "year": year,
                "adm_cd": adm_cd
            }, timeout=10)
            
            pop_data = pop_response.json()
            if 'result' not in pop_data or len(pop_data['result']) == 0:
                return None
            
            base_stats = pop_data['result'][0]
            
            # 2. 연령별 성별 인구
            age_sex_response = requests.get(AGE_SEX_URL, params={
                "accessToken": token,
                "year": year,
                "adm_cd": adm_cd,
                "low_search": "1"
            }, timeout=10)
            
            age_sex_data = age_sex_response.json()
            
            # 연령대별로 정리
            age_groups = {}
            if 'result' in age_sex_data:
                for item in age_sex_data['result']:
                    code = item['adm_cd']
                    pop = int(item['population'])
                    
                    # 마지막 6자리 분석
                    suffix = code[-6:]
                    category = int(suffix[:2])
                    
                    if category == 2:  # 10세 단위만 사용
                        detail_code = int(suffix[2:])  # 뒤 4자리 전체
                        
                        # 상세 코드 매핑 (실제 API 응답 기반)
                        age_gender_map = {
                            1: ("0-9세", "남성"),
                            2: ("10-19세", "남성"),
                            3: ("20-29세", "남성"),
                            4: ("30-39세", "남성"),
                            101: ("0-9세", "여성"),
                            102: ("10-19세", "여성"),
                            103: ("20-29세", "여성"),
                            104: ("30-39세", "여성")
                        }
                        
                        if detail_code in age_gender_map:
                            age_label, gender_label = age_gender_map[detail_code]
                        else:
                            # 패턴 분석: 앞 2자리=연령대, 뒤 2자리=세부
                            age_num = detail_code // 100 if detail_code >= 100 else detail_code // 10
                            is_female = detail_code >= 100
                            
                            age_map_simple = {
                                0: "0-9세", 1: "10-19세", 2: "20-29세", 3: "30-39세",
                                4: "40-49세", 5: "50-59세", 6: "60-69세", 7: "70-79세",
                                8: "80세 이상"
                            }
                            
                            age_label = age_map_simple.get(age_num, "기타")
                            gender_label = "여성" if is_female else "남성"
                        
                        if age_label not in age_groups:
                            age_groups[age_label] = {"male": 0, "female": 0, "total": 0}
                        
                        if gender_label == "남성":
                            age_groups[age_label]["male"] = pop
                        elif gender_label == "여성":
                            age_groups[age_label]["female"] = pop
                        
                        age_groups[age_label]["total"] = age_groups[age_label]["male"] + age_groups[age_label]["female"]
        
            return {
                "basic": {
                    "total_population": int(base_stats.get('tot_ppltn', 0)),
                    "total_household": int(base_stats.get('tot_family', 0)),
                    "avg_age": float(base_stats.get('avg_age', 0)),
                    "avg_household_size": float(base_stats.get('avg_fmember_cnt', 0)),
                    "population_density": float(base_stats.get('ppltn_dnsty', 0)),
                    "oldage_support_ratio": float(base_stats.get('oldage_suprt_per', 0)),
                    "youth_support_ratio": float(base_stats.get('juv_suprt_per', 0)),
                    "aging_index": float(base_stats.get('aged_child_idx', 0))
                },
                "age_groups": age_groups
            }
            
        except Exception as e:
            if attempt < 2:
                print(f"⚠️ 재시도 {attempt+1}/3 ({year}/{adm_cd})")
                time.sleep(2)
                continue
            else:
                return None
    
    return None

def load_emdong_codes():
    """읍면동 코드 목록 로드"""
    with open('sgis_comprehensive_stats.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    regions = data.get('regions', {})
    emdong_codes = list(regions.keys())
    
    print(f"✅ {len(emdong_codes):,}개 읍면동 코드 로드")
    return emdong_codes

def save_progress(data):
    """진행 상황 저장"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 저장 완료")

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     SGIS 연령별 상세 통계 수집 (2015~2023 전체)         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # 읍면동 코드 로드
    emdong_codes = load_emdong_codes()
    
    # 기존 데이터 로드
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        print(f"✅ 기존 데이터 로드: {len(output_data.get('regions_by_year', {}))}개 연도")
    except FileNotFoundError:
        output_data = {
            "metadata": {
                "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "years": YEARS,
                "description": "SGIS 연령별 상세 통계 (읍면동 레벨)"
            },
            "regions_by_year": {}
        }
        print("✅ 새로운 데이터 수집 시작")
    
    # 토큰 발급
    access_token = get_access_token()
    if not access_token:
        print("❌ 토큰 발급 실패")
        return
    
    token_time = time.time()
    total_collected = 0
    
    # 연도별 수집
    for year in YEARS:
        if year not in output_data['regions_by_year']:
            output_data['regions_by_year'][year] = {}
        
        year_data = output_data['regions_by_year'][year]
        already_collected = len(year_data)
        
        if already_collected >= len(emdong_codes) - 10:
            print(f"⏭️  {year}년은 이미 완료됨 ({already_collected}/{len(emdong_codes)})")
            continue
        
        print(f"\n📅 {year}년 데이터 수집 중...")
        print(f"   기존: {already_collected}개, 남은: {len(emdong_codes) - already_collected}개")
        
        collected_count = 0
        error_count = 0
        
        for idx, emdong_code in enumerate(emdong_codes, 1):
            # 이미 수집된 경우 건너뛰기
            if emdong_code in year_data:
                continue
            
            # 토큰 갱신 (50분마다)
            if time.time() - token_time > 3000:
                access_token = get_access_token()
                if not access_token:
                    print("❌ 토큰 재발급 실패")
                    break
                token_time = time.time()
                print(f"🔄 토큰 갱신")
            
            # 상세 통계 수집
            stats = collect_enhanced_stats(access_token, year, emdong_code)
            
            if stats:
                year_data[emdong_code] = stats
                collected_count += 1
                total_collected += 1
                
                # 진행 상황 표시 (100개마다)
                if collected_count % 100 == 0:
                    print(f"   진행: {already_collected + collected_count}/{len(emdong_codes)} "
                          f"({((already_collected + collected_count)/len(emdong_codes)*100):.1f}%)")
                    save_progress(output_data)
            else:
                error_count += 1
            
            # API 제한 고려 (0.3초 대기)
            time.sleep(0.3)
        
        # 연도별 완료 후 저장
        save_progress(output_data)
        print(f"✅ {year}년 완료: {len(year_data)}개 수집, 에러: {error_count}개")
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    ✅ 수집 완료                           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"총 수집: {total_collected}개")
    print(f"파일: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

