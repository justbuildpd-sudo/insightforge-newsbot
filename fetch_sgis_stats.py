#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API를 사용하여 전국 통계 데이터 수집
- 가구통계
- 주택통계  
- 사업체통계
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

def get_household_stats(access_token: str, year: str, adm_cd: str = "") -> List[Dict]:
    """가구 통계 조회"""
    try:
        params = {
            "accessToken": access_token,
            "year": year,
            "low_search": "1"
        }
        
        if adm_cd:
            params["adm_cd"] = adm_cd
        
        response = requests.get(HOUSEHOLD_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        else:
            print(f"⚠️ 가구통계 조회 실패 ({adm_cd}): {data.get('errMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ 가구통계 조회 오류 ({adm_cd}): {e}")
        return []

def get_house_stats(access_token: str, year: str, adm_cd: str = "") -> List[Dict]:
    """주택 통계 조회"""
    try:
        params = {
            "accessToken": access_token,
            "year": year,
            "low_search": "1"
        }
        
        if adm_cd:
            params["adm_cd"] = adm_cd
        
        response = requests.get(HOUSE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        else:
            print(f"⚠️ 주택통계 조회 실패 ({adm_cd}): {data.get('errMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ 주택통계 조회 오류 ({adm_cd}): {e}")
        return []

def get_company_stats(access_token: str, year: str, adm_cd: str = "") -> List[Dict]:
    """사업체 통계 조회"""
    try:
        params = {
            "accessToken": access_token,
            "year": year,
            "low_search": "1"
        }
        
        if adm_cd:
            params["adm_cd"] = adm_cd
        
        response = requests.get(COMPANY_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        else:
            print(f"⚠️ 사업체통계 조회 실패 ({adm_cd}): {data.get('errMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ 사업체통계 조회 오류 ({adm_cd}): {e}")
        return []

def collect_comprehensive_stats():
    """전국 종합 통계 데이터 수집"""
    print("=" * 60)
    print("📊 전국 종합 통계 데이터 수집 시작")
    print("=" * 60)
    
    # 1. 액세스 토큰 발급
    access_token = get_access_token()
    if not access_token:
        return
    
    # 2. 행정구역 데이터 로드
    try:
        with open('sgis_national_regions.json', 'r', encoding='utf-8') as f:
            regions_data = json.load(f)
    except FileNotFoundError:
        print("❌ sgis_national_regions.json 파일을 찾을 수 없습니다")
        return
    
    # 3. 수집할 연도 설정 (최신년도)
    YEAR = "2023"
    
    comprehensive_data = {
        "metadata": {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "year": YEAR,
            "total_regions": 0
        },
        "regions": {}
    }
    
    regions_list = regions_data.get('regions', {})
    total_count = 0
    
    # 4. 각 시도별 통계 수집
    for sido_cd, sido_info in regions_list.items():
        sido_name = sido_info.get('sido_name', '')
        sigungu_list = sido_info.get('sigungu_list', [])
        
        print(f"\n📍 {sido_name} ({sido_cd})")
        print(f"   시군구: {len(sigungu_list)}개")
        
        for sigungu in sigungu_list:
            sigungu_cd = sigungu['sigungu_code']
            sigungu_name = sigungu['sigungu_name']
            emdong_list = sigungu.get('emdong_list', [])
            
            print(f"   ├─ {sigungu_name} ({sigungu_cd}): ", end="", flush=True)
            
            # 읍면동별 통계 수집
            print(f"읍면동 {len(emdong_list)}개 ", end="", flush=True)
            
            for emdong in emdong_list:
                emdong_cd = emdong['emdong_code']
                emdong_name = emdong['emdong_name']
                
                # 가구통계
                household_data = get_household_stats(access_token, YEAR, emdong_cd)
                time.sleep(0.3)
                
                # 주택통계
                house_data = get_house_stats(access_token, YEAR, emdong_cd)
                time.sleep(0.3)
                
                # 사업체통계
                company_data = get_company_stats(access_token, YEAR, emdong_cd)
                time.sleep(0.3)
                
                # 데이터 통합
                if household_data or house_data or company_data:
                    household_info = household_data[0] if household_data else {}
                    house_info = house_data[0] if house_data else {}
                    company_info = company_data[0] if company_data else {}
                    
                    # 안전한 숫자 변환 함수
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
                    
                    comprehensive_data["regions"][emdong_cd] = {
                        "code": emdong_cd,
                        "sido_code": sido_cd,
                        "sido_name": sido_name,
                        "sigungu_code": sigungu_cd,
                        "sigungu_name": sigungu_name,
                        "emdong_name": emdong_name,
                        "full_address": emdong.get('full_address', ''),
                        "x_coord": emdong.get('x_coord', ''),
                        "y_coord": emdong.get('y_coord', ''),
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
                        },
                        "year": YEAR
                    }
                    total_count += 1
                    print(".", end="", flush=True)
            
            print(" ✓")
        
        # 시도별 저장 (중간 저장)
        if total_count % 100 == 0:
            print(f"\n💾 중간 저장... (현재 {total_count}개 지역)")
            with open('sgis_comprehensive_stats_partial.json', 'w', encoding='utf-8') as f:
                json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
    
    # 메타데이터 업데이트
    comprehensive_data["metadata"]["total_regions"] = total_count
    
    # 5. 최종 JSON 파일 저장
    output_file = "sgis_comprehensive_stats.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 통계 데이터 수집 완료!")
    print("=" * 60)
    print(f"📊 수집된 지역: {total_count}개")
    print(f"📅 기준연도: {YEAR}")
    print(f"💾 저장 파일: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    collect_comprehensive_stats()

