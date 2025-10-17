#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API를 사용하여 기술업종 통계 데이터 수집
- 전국 기술업종 정보
- 시도별 기술업종 정보
- 시군구별 기술업종 정보
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
TECH_INFO_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/technicalbiz/companyinfo.json"
SIDO_TECH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/technicalbiz/sidocompanyinfo.json"
SGG_TECH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/technicalbiz/sggcompanyinfo.json"

# 기술업종 코드
TECH_CODES = {
    "11": "첨단기술",
    "12": "고기술",
    "13": "중고기술",
    "14": "중저기술",
    "15": "저기술"
}

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

def get_national_tech_info(access_token: str) -> List[Dict]:
    """전국 기술업종 정보"""
    try:
        params = {
            "accessToken": access_token
        }
        
        response = requests.get(TECH_INFO_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        return []
            
    except Exception as e:
        print(f"❌ 전국 기술업종 조회 오류: {e}")
        return []

def get_sido_tech_info(access_token: str) -> List[Dict]:
    """시도별 기술업종 정보"""
    try:
        params = {
            "accessToken": access_token
        }
        
        response = requests.get(SIDO_TECH_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        return []
            
    except Exception as e:
        print(f"❌ 시도별 기술업종 조회 오류: {e}")
        return []

def get_sgg_tech_info(access_token: str, tech_cd: str) -> List[Dict]:
    """시군구별 기술업종 정보"""
    try:
        params = {
            "accessToken": access_token,
            "techbiz_cd": tech_cd
        }
        
        response = requests.get(SGG_TECH_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", [])
        return []
            
    except Exception as e:
        return []

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

def collect_tech_stats():
    """전국 기술업종 통계 데이터 수집"""
    print("=" * 60)
    print("🔬 전국 기술업종 통계 데이터 수집 시작")
    print("=" * 60)
    
    # 1. 액세스 토큰 발급
    access_token = get_access_token()
    if not access_token:
        return
    
    tech_data = {
        "metadata": {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "SGIS 기술업종 통계 데이터",
            "tech_categories": TECH_CODES
        },
        "national": {},
        "sido": {},
        "sigungu": {}
    }
    
    # 2. 전국 기술업종 정보
    print("\n📊 전국 기술업종 정보 수집 중...")
    national_tech = get_national_tech_info(access_token)
    tech_data["national"] = national_tech
    print(f"   ✅ {len(national_tech)}개 연도 데이터")
    time.sleep(0.5)
    
    # 3. 시도별 기술업종 정보
    print("\n📍 시도별 기술업종 정보 수집 중...")
    sido_tech = get_sido_tech_info(access_token)
    
    for sido_info in sido_tech:
        sido_cd = sido_info.get('sido_cd')
        if sido_cd:
            tech_data["sido"][sido_cd] = sido_info
            print(f"   ├─ {sido_info.get('sido_nm')} ✓")
    
    print(f"   ✅ {len(tech_data['sido'])}개 시도")
    time.sleep(0.5)
    
    # 4. 시군구별 기술업종 정보 (각 기술 유형별로)
    print("\n🏢 시군구별 기술업종 정보 수집 중...")
    
    for tech_cd, tech_name in TECH_CODES.items():
        print(f"\n   📌 {tech_name} ({tech_cd})")
        
        sgg_tech = get_sgg_tech_info(access_token, tech_cd)
        time.sleep(0.5)
        
        for sgg_info in sgg_tech:
            sido_cd = sgg_info.get('sido_cd')
            sgg_cd = sgg_info.get('sgg_cd')
            
            if sido_cd and sgg_cd:
                sigungu_code = f"{sido_cd}{sgg_cd}"
                
                if sigungu_code not in tech_data["sigungu"]:
                    tech_data["sigungu"][sigungu_code] = {
                        "code": sigungu_code,
                        "sido_code": sido_cd,
                        "sido_name": sgg_info.get('sido_nm', ''),
                        "sigungu_name": sgg_info.get('sgg_nm', ''),
                        "x_coord": sgg_info.get('x_coor', ''),
                        "y_coord": sgg_info.get('y_coor', ''),
                        "tech_categories": {}
                    }
                
                tech_data["sigungu"][sigungu_code]["tech_categories"][tech_cd] = {
                    "name": tech_name,
                    "corp_cnt": safe_int(sgg_info.get('techbiz_corp_cnt')),
                    "corp_per": safe_float(sgg_info.get('techbiz_corp_per')),
                    "corp_growth_rate": safe_float(sgg_info.get('techbiz_corp_irdsrate'))
                }
        
        print(f"      ✅ {len(sgg_tech)}개 시군구")
    
    # 메타데이터 업데이트
    tech_data["metadata"]["total_sigungu"] = len(tech_data["sigungu"])
    
    # 5. 최종 JSON 파일 저장
    output_file = "sgis_tech_stats.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tech_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 기술업종 통계 데이터 수집 완료!")
    print("=" * 60)
    print(f"📊 전국 데이터: {len(tech_data['national'])}개 연도")
    print(f"📊 시도 데이터: {len(tech_data['sido'])}개")
    print(f"📊 시군구 데이터: {len(tech_data['sigungu'])}개")
    print(f"💾 저장 파일: {output_file}")
    print("=" * 60)
    
    print("\n📋 수집된 기술업종 분류:")
    for code, name in TECH_CODES.items():
        print(f"  {code}: {name}")

if __name__ == "__main__":
    collect_tech_stats()

