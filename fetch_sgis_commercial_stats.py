#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API를 사용하여 상권 통계 데이터 수집
- 거주인구 요약 (연령대별)
- 성별인구 비율
- 거처종류 (주택 유형)
- 소상공인 업종별 사업체 비율
- 지역 종합 정보
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
PPL_SUMMARY_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/startupbiz/pplsummary.json"
GENDER_RATIO_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/startupbiz/mfratiosummary.json"
HOUSE_SUMMARY_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/startupbiz/housesummary.json"
CORP_DIST_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/startupbiz/corpdistsummary.json"
REGION_TOTAL_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/startupbiz/regiontotal.json"

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
            token = data["result"]["accessToken"]
            print(f"✅ 액세스 토큰 발급 성공")
            return token
        else:
            print(f"❌ 토큰 발급 실패: {data.get('errMsg')}")
            return None
            
    except Exception as e:
        print(f"❌ 토큰 발급 오류: {e}")
        return None

def get_population_summary(access_token: str, adm_cd: str) -> Dict:
    """거주인구 요약 정보 (연령대별)"""
    try:
        params = {
            "accessToken": access_token,
            "adm_cd": adm_cd
        }
        
        response = requests.get(PPL_SUMMARY_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0 and data.get("result"):
            return data["result"][0] if isinstance(data["result"], list) else data["result"]
        return {}
            
    except Exception as e:
        return {}

def get_gender_ratio(access_token: str, adm_cd: str) -> Dict:
    """성별 인구 비율"""
    try:
        params = {
            "accessToken": access_token,
            "adm_cd": adm_cd
        }
        
        response = requests.get(GENDER_RATIO_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0 and data.get("result"):
            return data["result"][0] if isinstance(data["result"], list) else data["result"]
        return {}
            
    except Exception as e:
        return {}

def get_house_summary(access_token: str, adm_cd: str) -> Dict:
    """거처 종류 (주택 유형)"""
    try:
        params = {
            "accessToken": access_token,
            "adm_cd": adm_cd
        }
        
        response = requests.get(HOUSE_SUMMARY_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0 and data.get("result"):
            return data["result"][0] if isinstance(data["result"], list) else data["result"]
        return {}
            
    except Exception as e:
        return {}

def get_corp_distribution(access_token: str, adm_cd: str) -> List[Dict]:
    """소상공인 업종별 사업체 비율"""
    try:
        params = {
            "accessToken": access_token,
            "adm_cd": adm_cd
        }
        
        response = requests.get(CORP_DIST_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0 and data.get("result"):
            result = data["result"][0] if isinstance(data["result"], list) else data["result"]
            return result.get("theme_list", [])
        return []
            
    except Exception as e:
        return []

def get_region_total(access_token: str, adm_cd: str) -> Dict:
    """지역 종합 정보"""
    try:
        params = {
            "accessToken": access_token,
            "adm_cd": adm_cd
        }
        
        response = requests.get(REGION_TOTAL_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0 and data.get("result"):
            return data["result"][0] if isinstance(data["result"], list) else data["result"]
        return {}
            
    except Exception as e:
        return {}

def safe_float(value, default=0.0):
    """안전한 float 변환"""
    try:
        return float(value) if value and value != 'N/A' else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """안전한 int 변환"""
    try:
        return int(value) if value and value != 'N/A' else default
    except (ValueError, TypeError):
        return default

def collect_commercial_stats():
    """전국 상권 통계 데이터 수집"""
    print("=" * 60)
    print("🏪 전국 상권 통계 데이터 수집 시작")
    print("=" * 60)
    
    # 1. 액세스 토큰 발급
    access_token = get_access_token()
    if not access_token:
        return
    
    # 2. 기존 시군구 데이터 로드
    try:
        with open('sgis_national_regions.json', 'r', encoding='utf-8') as f:
            regions_data = json.load(f)
    except FileNotFoundError:
        print("❌ sgis_national_regions.json 파일을 찾을 수 없습니다")
        return
    
    commercial_data = {
        "metadata": {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "SGIS 상권 통계 데이터",
            "total_regions": 0
        },
        "regions": {}
    }
    
    regions_list = regions_data.get('regions', {})
    total_count = 0
    
    # 3. 시군구별 상권 통계 수집 (읍면동은 너무 많아서 시군구만)
    for sido_cd, sido_info in regions_list.items():
        sido_name = sido_info.get('sido_name', '')
        sigungu_list = sido_info.get('sigungu_list', [])
        
        print(f"\n📍 {sido_name} ({sido_cd})")
        print(f"   시군구: {len(sigungu_list)}개")
        
        for sigungu in sigungu_list:
            sigungu_cd = sigungu['sigungu_code']
            sigungu_name = sigungu['sigungu_name']
            
            print(f"   ├─ {sigungu_name} ({sigungu_cd}): ", end="", flush=True)
            
            # 연령별 인구
            ppl_summary = get_population_summary(access_token, sigungu_cd)
            time.sleep(0.3)
            
            # 성별 비율
            gender_ratio = get_gender_ratio(access_token, sigungu_cd)
            time.sleep(0.3)
            
            # 주택 유형
            house_summary = get_house_summary(access_token, sigungu_cd)
            time.sleep(0.3)
            
            # 업종 분포
            corp_dist = get_corp_distribution(access_token, sigungu_cd)
            time.sleep(0.3)
            
            # 지역 종합
            region_total = get_region_total(access_token, sigungu_cd)
            time.sleep(0.3)
            
            # 데이터 통합
            commercial_data["regions"][sigungu_cd] = {
                "code": sigungu_cd,
                "sido_code": sido_cd,
                "sido_name": sido_name,
                "sigungu_name": sigungu_name,
                "full_address": sigungu.get('full_address', ''),
                "population_by_age": {
                    "under_10_per": safe_float(ppl_summary.get('teenage_less_than_per')),
                    "under_10_cnt": safe_int(ppl_summary.get('teenage_less_than_cnt')),
                    "teen_per": safe_float(ppl_summary.get('teenage_per')),
                    "teen_cnt": safe_int(ppl_summary.get('teenage_cnt')),
                    "twenty_per": safe_float(ppl_summary.get('twenty_per')),
                    "twenty_cnt": safe_int(ppl_summary.get('twenty_cnt')),
                    "thirty_per": safe_float(ppl_summary.get('thirty_per')),
                    "thirty_cnt": safe_int(ppl_summary.get('thirty_cnt')),
                    "forty_per": safe_float(ppl_summary.get('forty_per')),
                    "forty_cnt": safe_int(ppl_summary.get('forty_cnt')),
                    "fifty_per": safe_float(ppl_summary.get('fifty_per')),
                    "fifty_cnt": safe_int(ppl_summary.get('fifty_cnt')),
                    "sixty_per": safe_float(ppl_summary.get('sixty_per')),
                    "sixty_cnt": safe_int(ppl_summary.get('sixty_cnt')),
                    "seventy_plus_per": safe_float(ppl_summary.get('seventy_more_than_per')),
                    "seventy_plus_cnt": safe_int(ppl_summary.get('seventy_more_than_cnt'))
                },
                "gender": {
                    "male_per": safe_float(gender_ratio.get('m_per')),
                    "male_cnt": safe_int(gender_ratio.get('m_ppl')),
                    "female_per": safe_float(gender_ratio.get('f_per')),
                    "female_cnt": safe_int(gender_ratio.get('f_ppl')),
                    "total_population": safe_int(gender_ratio.get('total_ppl'))
                },
                "house_type": {
                    "apartment_per": safe_float(house_summary.get('apart_per')),
                    "apartment_cnt": safe_int(house_summary.get('apart_cnt')),
                    "detached_per": safe_float(house_summary.get('detach_house_per')),
                    "detached_cnt": safe_int(house_summary.get('detach_house_cnt')),
                    "row_house_per": safe_float(house_summary.get('row_house_per')),
                    "row_house_cnt": safe_int(house_summary.get('row_house_cnt')),
                    "officetel_per": safe_float(house_summary.get('officetel_per')),
                    "officetel_cnt": safe_int(house_summary.get('officetel_cnt'))
                },
                "business_distribution": corp_dist[:20] if corp_dist else [],  # 상위 20개 업종
                "region_summary": {
                    "apartment_per": safe_float(region_total.get('apart_per')),
                    "resident_population_per": safe_float(region_total.get('resid_ppltn_per')),
                    "worker_population_per": safe_float(region_total.get('job_ppltn_per')),
                    "one_person_family_per": safe_float(region_total.get('one_person_family_per')),
                    "senior_65_plus_per": safe_float(region_total.get('sixty_five_more_ppltn_per')),
                    "twenty_age_per": safe_float(region_total.get('twenty_ppltn_per'))
                }
            }
            
            total_count += 1
            print("✓")
            
            # 중간 저장 (100개마다)
            if total_count % 100 == 0:
                print(f"\n💾 중간 저장... (현재 {total_count}개 시군구)")
                with open('sgis_commercial_stats_partial.json', 'w', encoding='utf-8') as f:
                    json.dump(commercial_data, f, ensure_ascii=False, indent=2)
    
    # 메타데이터 업데이트
    commercial_data["metadata"]["total_regions"] = total_count
    
    # 4. 최종 JSON 파일 저장
    output_file = "sgis_commercial_stats.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(commercial_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 상권 통계 데이터 수집 완료!")
    print("=" * 60)
    print(f"📊 수집된 시군구: {total_count}개")
    print(f"💾 저장 파일: {output_file}")
    print("=" * 60)
    
    print("\n📋 수집된 데이터 항목:")
    print("  - 연령대별 인구 (10대 미만 ~ 70대 이상)")
    print("  - 성별 인구 비율")
    print("  - 주택 유형 (아파트, 단독, 연립, 오피스텔)")
    print("  - 업종별 사업체 분포 (상위 20개)")
    print("  - 지역 종합 정보 (1인가구, 65세이상, 20대 등)")

if __name__ == "__main__":
    collect_commercial_stats()

