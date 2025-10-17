#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API 다년도 통계 수집 (네트워크 단절 대응 버전)
- 자동 재시도
- 토큰 자동 갱신
- 진행 상태 저장 및 재개
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
import os

# API 인증 정보
SERVICE_ID = "8806b098778b4d6e84cd"
SECURITY_KEY = "5736845d40cf49ec8da5"

# API 엔드포인트
AUTH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"
HOUSEHOLD_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/household.json"
HOUSE_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/house.json"
COMPANY_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/company.json"

# 수집할 연도
YEARS = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

# 진행 상태 파일
PROGRESS_FILE = "multiyear_progress.json"
PARTIAL_FILE = "sgis_multiyear_stats_partial.json"

def check_internet():
    """인터넷 연결 확인"""
    try:
        # timeout을 10초로 늘림 (네트워크 변경 시 지연 고려)
        requests.get("https://www.google.com", timeout=10)
        return True
    except:
        return False

def wait_for_internet():
    """인터넷 연결 대기 (30초 단위)"""
    retry_count = 0
    while not check_internet():
        retry_count += 1
        if retry_count == 1:
            print("\n⚠️ 인터넷 연결 끊김. 재연결 대기 중...", end="", flush=True)
        else:
            print(".", end="", flush=True)
        time.sleep(30)  # 30초 대기
    
    if retry_count > 0:
        print(" ✅ 복구됨")

def get_access_token(retry_count=5) -> Optional[str]:
    """액세스 토큰 발급 (재시도 포함)"""
    for attempt in range(retry_count):
        try:
            wait_for_internet()
            
            params = {
                "consumer_key": SERVICE_ID,
                "consumer_secret": SECURITY_KEY
            }
            
            response = requests.get(AUTH_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("errCd") == 0:
                return data["result"]["accessToken"]
            
            print(f"⚠️ 토큰 발급 실패 (시도 {attempt + 1}/{retry_count})")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 토큰 발급 오류 (시도 {attempt + 1}/{retry_count}): {e}")
            time.sleep(5)
    
    return None

def get_stats_with_retry(access_token_ref: List[str], url: str, year: str, adm_cd: str = "", max_retries=5) -> List[Dict]:
    """통계 조회 (재시도 및 토큰 갱신 포함)"""
    for attempt in range(max_retries):
        try:
            # 첫 시도나 재시도 시에만 인터넷 체크
            if attempt > 0:
                wait_for_internet()
            
            params = {
                "accessToken": access_token_ref[0],
                "year": year,
                "low_search": "1"
            }
            
            if adm_cd:
                params["adm_cd"] = adm_cd
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # 토큰 만료 체크
            if data.get("errCd") == 100:  # 토큰 만료
                print("\n🔄 토큰 갱신 중...")
                new_token = get_access_token()
                if new_token:
                    access_token_ref[0] = new_token
                    continue
            
            if data.get("errCd") == 0:
                return data.get("result", [])
            
            # 데이터 없음은 정상 (일부 지역)
            if "검색결과가 존재하지 않습니다" in str(data.get("errMsg", "")):
                return []
            
            time.sleep(1)
        except requests.exceptions.Timeout:
            print(f"\n⏱️ 타임아웃 (시도 {attempt + 1}/{max_retries})", end=" ", flush=True)
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"\n🔌 연결 오류 (시도 {attempt + 1}/{max_retries})", end=" ", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"\n❌ 오류 (시도 {attempt + 1}/{max_retries}): {e}", end=" ", flush=True)
            time.sleep(2)
    
    return []

def safe_int(value, default=0):
    try:
        return int(value) if value and value != 'N/A' else default
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value) if value and value != 'N/A' else default
    except (ValueError, TypeError):
        return default

def load_progress():
    """진행 상태 로드"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"completed_years": [], "current_year": None, "current_sido_idx": 0}

def save_progress(progress):
    """진행 상태 저장"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def collect_multiyear_stats():
    """다년도 통계 데이터 수집 (재개 가능)"""
    print("=" * 60)
    print("📅 다년도 통계 데이터 수집 (네트워크 단절 대응)")
    print("=" * 60)
    
    # 진행 상태 로드
    progress = load_progress()
    
    # 토큰 발급 (리스트로 참조 전달)
    access_token_ref = [get_access_token()]
    if not access_token_ref[0]:
        print("❌ 토큰 발급 실패")
        return
    
    print(f"✅ 토큰 발급 성공")
    
    # 행정구역 데이터 로드
    try:
        with open('sgis_national_regions.json', 'r', encoding='utf-8') as f:
            regions_data = json.load(f)
    except FileNotFoundError:
        print("❌ sgis_national_regions.json 파일을 찾을 수 없습니다")
        return
    
    # 기존 데이터 로드 (재개)
    if os.path.exists(PARTIAL_FILE):
        try:
            with open(PARTIAL_FILE, 'r', encoding='utf-8') as f:
                multiyear_data = json.load(f)
            print(f"🔄 기존 데이터 로드: {len(multiyear_data.get('regions_by_year', {}))}개 연도")
        except:
            multiyear_data = {
                "metadata": {
                    "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "years": YEARS,
                    "description": "SGIS 다년도 통계 (읍면동 레벨)"
                },
                "regions_by_year": {}
            }
    else:
        multiyear_data = {
            "metadata": {
                "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "years": YEARS,
                "description": "SGIS 다년도 통계 (읍면동 레벨)"
            },
            "regions_by_year": {}
        }
    
    regions_list = regions_data.get('regions', {})
    
    # 완료된 연도 건너뛰기
    for year in YEARS:
        if year in progress.get("completed_years", []):
            print(f"⏭️ {year}년은 이미 완료됨 (건너뛰기)")
            continue
        
        print(f"\n📅 {year}년 데이터 수집 중...")
        year_data = multiyear_data["regions_by_year"].get(year, {})
        total_count = len(year_data)  # 기존 수집된 개수
        save_counter = 0  # 저장 카운터
        
        for sido_cd, sido_info in regions_list.items():
            sido_name = sido_info.get('sido_name', '')
            sigungu_list = sido_info.get('sigungu_list', [])
            
            print(f"  📍 {sido_name} ", end="", flush=True)
            
            for sigungu in sigungu_list:
                sigungu_cd = sigungu['sigungu_code']
                emdong_list = sigungu.get('emdong_list', [])
                
                for emdong in emdong_list:
                    emdong_cd = emdong['emdong_code']
                    
                    # 이미 수집된 데이터는 건너뛰기
                    if emdong_cd in year_data:
                        print("·", end="", flush=True)
                        continue
                    
                    # 가구통계 (재시도 포함)
                    household_data = get_stats_with_retry(access_token_ref, HOUSEHOLD_URL, year, emdong_cd)
                    time.sleep(0.3)
                    
                    # 주택통계
                    house_data = get_stats_with_retry(access_token_ref, HOUSE_URL, year, emdong_cd)
                    time.sleep(0.3)
                    
                    # 사업체통계
                    company_data = get_stats_with_retry(access_token_ref, COMPANY_URL, year, emdong_cd)
                    time.sleep(0.3)
                    
                    if household_data or house_data or company_data:
                        household_info = household_data[0] if household_data else {}
                        house_info = house_data[0] if house_data else {}
                        company_info = company_data[0] if company_data else {}
                        
                        year_data[emdong_cd] = {
                            "code": emdong_cd,
                            "household": {
                                "household_cnt": safe_int(household_info.get('household_cnt')),
                                "family_member_cnt": safe_int(household_info.get('family_member_cnt')),
                                "avg_family_member_cnt": safe_float(household_info.get('avg_family_member_cnt'))
                            },
                            "house": {
                                "house_cnt": safe_int(house_info.get('house_cnt'))
                            },
                            "company": {
                                "corp_cnt": safe_int(company_info.get('corp_cnt')),
                                "tot_worker": safe_int(company_info.get('tot_worker'))
                            }
                        }
                        total_count += 1
                        save_counter += 1
                        print(".", end="", flush=True)
                        
                        # 100개마다 중간 저장
                        if save_counter >= 100:
                            multiyear_data["regions_by_year"][year] = year_data
                            with open(PARTIAL_FILE, 'w', encoding='utf-8') as f:
                                json.dump(multiyear_data, f, ensure_ascii=False, indent=2)
                            save_counter = 0
            
            print(" ✓", flush=True)
        
        multiyear_data["regions_by_year"][year] = year_data
        print(f"  ✅ {year}년: {total_count}개 읍면동 수집")
        
        # 연도별 저장 (네트워크 단절 대비)
        with open(PARTIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(multiyear_data, f, ensure_ascii=False, indent=2)
        
        # 진행 상태 업데이트
        progress["completed_years"].append(year)
        save_progress(progress)
        print(f"  💾 {year}년 데이터 저장 완료")
    
    # 최종 저장
    output_file = "sgis_multiyear_stats.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(multiyear_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 다년도 통계 데이터 수집 완료!")
    print("=" * 60)
    print(f"📊 수집 연도: {len(YEARS)}개 ({YEARS[0]} ~ {YEARS[-1]})")
    print(f"💾 저장 파일: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    print("🛡️ 네트워크 단절 대응 기능:")
    print("  - 자동 재시도 (최대 5회)")
    print("  - 토큰 자동 갱신")
    print("  - 연도별 중간 저장")
    print("  - 중단 후 재개 가능")
    print("")
    print("⚠️ 예상 소요 시간: 약 27~36시간 (1일 이상)")
    print("")
    
    collect_multiyear_stats()

