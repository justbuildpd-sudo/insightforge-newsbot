#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통계지리정보서비스(SGIS) API를 사용하여 전국 행정구역 데이터 수집
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
STAGE_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/addr/stage.json"

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
            print(f"✅ 액세스 토큰 발급 성공: {token[:20]}...")
            return token
        else:
            print(f"❌ 토큰 발급 실패: {data.get('errMsg')}")
            return None
            
    except Exception as e:
        print(f"❌ 토큰 발급 오류: {e}")
        return None

def get_sido_list(access_token: str) -> List[Dict]:
    """시도 목록 조회"""
    try:
        params = {
            "accessToken": access_token
        }
        
        response = requests.get(STAGE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            sido_list = data["result"]
            print(f"✅ 시도 목록: {len(sido_list)}개")
            return sido_list
        else:
            print(f"❌ 시도 조회 실패: {data.get('errMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ 시도 조회 오류: {e}")
        return []

def get_sigungu_list(access_token: str, sido_cd: str) -> List[Dict]:
    """시군구 목록 조회"""
    try:
        params = {
            "accessToken": access_token,
            "cd": sido_cd
        }
        
        response = requests.get(STAGE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data["result"]
        else:
            print(f"❌ 시군구 조회 실패 ({sido_cd}): {data.get('errMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ 시군구 조회 오류 ({sido_cd}): {e}")
        return []

def get_emdong_list(access_token: str, sigungu_cd: str) -> List[Dict]:
    """읍면동 목록 조회"""
    try:
        params = {
            "accessToken": access_token,
            "cd": sigungu_cd
        }
        
        response = requests.get(STAGE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data["result"]
        else:
            print(f"❌ 읍면동 조회 실패 ({sigungu_cd}): {data.get('errMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ 읍면동 조회 오류 ({sigungu_cd}): {e}")
        return []

def collect_national_data():
    """전국 행정구역 데이터 수집"""
    print("=" * 60)
    print("🇰🇷 전국 행정구역 데이터 수집 시작")
    print("=" * 60)
    
    # 1. 액세스 토큰 발급
    access_token = get_access_token()
    if not access_token:
        return
    
    # 2. 시도 목록 조회
    sido_list = get_sido_list(access_token)
    if not sido_list:
        return
    
    national_data = {
        "metadata": {
            "total_sido": 0,
            "total_sigungu": 0,
            "total_emdong": 0,
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "regions": {}
    }
    
    total_sigungu_count = 0
    total_emdong_count = 0
    
    # 3. 각 시도별 시군구 및 읍면동 수집
    for sido in sido_list:
        sido_cd = sido["cd"]
        sido_name = sido["addr_name"]
        
        print(f"\n📍 {sido_name} ({sido_cd})")
        
        # 시군구 조회
        sigungu_list = get_sigungu_list(access_token, sido_cd)
        time.sleep(0.5)  # API 호출 간격
        
        if not sigungu_list:
            continue
        
        print(f"   └─ 시군구: {len(sigungu_list)}개")
        total_sigungu_count += len(sigungu_list)
        
        sido_data = {
            "sido_code": sido_cd,
            "sido_name": sido_name,
            "sigungu_list": []
        }
        
        for sigungu in sigungu_list:
            sigungu_cd = sigungu["cd"]
            sigungu_name = sigungu["addr_name"]
            
            print(f"      ├─ {sigungu_name} ({sigungu_cd})")
            
            # 읍면동 조회
            emdong_list = get_emdong_list(access_token, sigungu_cd)
            time.sleep(0.5)  # API 호출 간격
            
            if emdong_list:
                print(f"      │  └─ 읍면동: {len(emdong_list)}개")
                total_emdong_count += len(emdong_list)
            
            sigungu_data = {
                "sigungu_code": sigungu_cd,
                "sigungu_name": sigungu_name,
                "full_address": sigungu.get("full_addr", ""),
                "x_coord": sigungu.get("x_coor", ""),
                "y_coord": sigungu.get("y_coor", ""),
                "emdong_list": []
            }
            
            for emdong in emdong_list:
                emdong_data = {
                    "emdong_code": emdong["cd"],
                    "emdong_name": emdong["addr_name"],
                    "full_address": emdong.get("full_addr", ""),
                    "x_coord": emdong.get("x_coor", ""),
                    "y_coord": emdong.get("y_coor", "")
                }
                sigungu_data["emdong_list"].append(emdong_data)
            
            sido_data["sigungu_list"].append(sigungu_data)
        
        national_data["regions"][sido_cd] = sido_data
    
    # 메타데이터 업데이트
    national_data["metadata"]["total_sido"] = len(sido_list)
    national_data["metadata"]["total_sigungu"] = total_sigungu_count
    national_data["metadata"]["total_emdong"] = total_emdong_count
    
    # 4. JSON 파일 저장
    output_file = "sgis_national_regions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(national_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 데이터 수집 완료!")
    print("=" * 60)
    print(f"📊 총 시도: {len(sido_list)}개")
    print(f"📊 총 시군구: {total_sigungu_count}개")
    print(f"📊 총 읍면동: {total_emdong_count}개")
    print(f"💾 저장 파일: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    collect_national_data()

