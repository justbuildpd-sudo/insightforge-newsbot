#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API를 사용하여 다년도 통계 데이터 수집
2015년 ~ 2023년 (9개 연도)
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional

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

def get_access_token() -> Optional[str]:
    """액세스 토큰 발급"""
    try:
        params = {
            "consumer_key": SERVICE_ID,
            "consumer_secret": SECURITY_KEY
        }
        
        response = requests.get(AUTH_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data["result"]["accessToken"]
        return None
    except Exception as e:
        print(f"❌ 토큰 발급 오류: {e}")
        return None

def get_stats(access_token: str, url: str, year: str, adm_cd: str = "") -> List[Dict]:
    """통계 조회"""
    try:
        params = {
            "accessToken": access_token,
            "year": year,
            "low_search": "1"
        }
        
        if adm_cd:
            params["adm_cd"] = adm_cd
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        return []
    except Exception as e:
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

def collect_multiyear_stats():
    """다년도 통계 데이터 수집"""
    print("=" * 60)
    print("📅 다년도 통계 데이터 수집 시작 (2015-2023)")
    print("=" * 60)
    
    access_token = get_access_token()
    if not access_token:
        return
    
    print(f"✅ 토큰 발급 성공")
    
    # 행정구역 데이터 로드
    try:
        with open('sgis_national_regions.json', 'r', encoding='utf-8') as f:
            regions_data = json.load(f)
    except FileNotFoundError:
        print("❌ sgis_national_regions.json 파일을 찾을 수 없습니다")
        return
    
    multiyear_data = {
        "metadata": {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "years": YEARS,
            "description": "SGIS 다년도 통계 (읍면동 레벨)"
        },
        "regions_by_year": {}
    }
    
    regions_list = regions_data.get('regions', {})
    
    # 연도별 수집
    for year in YEARS:
        print(f"\n📅 {year}년 데이터 수집 중...")
        
        year_data = {}
        total_count = 0
        
        for sido_cd, sido_info in regions_list.items():
            sido_name = sido_info.get('sido_name', '')
            sigungu_list = sido_info.get('sigungu_list', [])
            
            print(f"  📍 {sido_name} ", end="", flush=True)
            
            for sigungu in sigungu_list:
                sigungu_cd = sigungu['sigungu_code']
                emdong_list = sigungu.get('emdong_list', [])
                
                for emdong in emdong_list:
                    emdong_cd = emdong['emdong_code']
                    
                    # 가구통계
                    household_data = get_stats(access_token, HOUSEHOLD_URL, year, emdong_cd)
                    time.sleep(0.3)
                    
                    # 주택통계
                    house_data = get_stats(access_token, HOUSE_URL, year, emdong_cd)
                    time.sleep(0.3)
                    
                    # 사업체통계
                    company_data = get_stats(access_token, COMPANY_URL, year, emdong_cd)
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
                        print(".", end="", flush=True)
                
                print(" ", end="", flush=True)
            
            print("✓")
        
        multiyear_data["regions_by_year"][year] = year_data
        print(f"  ✅ {year}년: {total_count}개 읍면동 수집")
        
        # 중간 저장
        with open('sgis_multiyear_stats_partial.json', 'w', encoding='utf-8') as f:
            json.dump(multiyear_data, f, ensure_ascii=False, indent=2)
    
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
    # 경고: 이 스크립트는 매우 오래 걸립니다 (약 11시간)
    # 3,553개 읍면동 × 9년 × 3종류 통계 × 0.3초 = 약 8시간
    print("⚠️ 경고: 이 작업은 약 8~11시간이 소요됩니다.")
    print("⚠️ 백그라운드로 실행하는 것을 권장합니다.")
    print("")
    
    user_input = input("계속하시겠습니까? (y/n): ")
    if user_input.lower() == 'y':
        collect_multiyear_stats()
    else:
        print("취소되었습니다.")

