#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS API를 사용하여 통계주제도 데이터 수집
- 인구와 가구 (CTGR_001)
- 주거와 교통 (CTGR_002)
- 복지와 문화 (CTGR_003)
- 노동과 경제 (CTGR_004)
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

THEMA_URLS = {
    "CTGR_001": {
        "name": "인구와 가구",
        "list_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_001/list.json",
        "data_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_001/data.json"
    },
    "CTGR_002": {
        "name": "주거와 교통",
        "list_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_002/list.json",
        "data_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_002/data.json"
    },
    "CTGR_003": {
        "name": "복지와 문화",
        "list_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_003/list.json",
        "data_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_003/data.json"
    },
    "CTGR_004": {
        "name": "노동과 경제",
        "list_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_004/list.json",
        "data_url": "https://sgisapi.kostat.go.kr/OpenAPI3/themamap/CTGR_004/data.json"
    }
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

def get_thema_list(access_token: str, list_url: str) -> List[Dict]:
    """통계주제도 목록 조회"""
    try:
        params = {
            "accessToken": access_token
        }
        
        response = requests.get(list_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            result = data.get("result", {})
            # 다양한 키 형태 처리
            for key in result.keys():
                if 'List' in key:
                    return result[key]
            return []
        return []
            
    except Exception as e:
        print(f"  ❌ 목록 조회 오류: {e}")
        return []

def get_thema_data(access_token: str, data_url: str, thema_id: str, region_div: str = "2") -> Dict:
    """통계주제도 데이터 조회"""
    try:
        params = {
            "accessToken": access_token,
            "stat_thema_map_id": thema_id,
            "region_div": region_div,
            "adm_cd": "00"  # 전국
        }
        
        response = requests.get(data_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("errCd") == 0:
            return data.get("result", {})
        return {}
            
    except Exception as e:
        return {}

def collect_thema_stats():
    """통계주제도 데이터 수집"""
    print("=" * 60)
    print("📈 통계주제도 데이터 수집 시작")
    print("=" * 60)
    
    # 1. 액세스 토큰 발급
    access_token = get_access_token()
    if not access_token:
        return
    
    thema_data = {
        "metadata": {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "SGIS 통계주제도 데이터",
            "categories": {k: v["name"] for k, v in THEMA_URLS.items()}
        },
        "categories": {}
    }
    
    # 2. 각 카테고리별 데이터 수집
    for category_code, category_info in THEMA_URLS.items():
        category_name = category_info["name"]
        print(f"\n📊 {category_name} ({category_code})")
        
        # 목록 조회
        thema_list = get_thema_list(access_token, category_info["list_url"])
        time.sleep(0.5)
        
        if not thema_list:
            print(f"  ⚠️ 목록이 비어있습니다")
            continue
        
        print(f"  ├─ 주제도 {len(thema_list)}개 발견")
        
        category_data = {
            "name": category_name,
            "themes": []
        }
        
        # 각 주제도별 데이터 수집 (대표 3개만)
        for idx, theme in enumerate(thema_list[:3]):
            theme_id = theme.get('stat_thema_map_id')
            theme_title = theme.get('title', '')
            
            if not theme_id:
                continue
            
            print(f"  │  ├─ {theme_title[:30]}...", end=" ", flush=True)
            
            # 시군구 레벨 데이터 조회
            theme_data_result = get_thema_data(access_token, category_info["data_url"], theme_id, "2")
            time.sleep(0.5)
            
            if theme_data_result:
                category_data["themes"].append({
                    "id": theme_id,
                    "title": theme_title,
                    "description": theme.get('thema_map_exp', ''),
                    "source": theme.get('rel_stat_info', ''),
                    "display_method": theme.get('disp_mthd', ''),
                    "base_year": theme.get('base_year', ''),
                    "region_div": theme.get('region_div', []),
                    "year_info": theme.get('yearInfo', []),
                    "data_info": {
                        "data1_nm": theme.get('data1_nm'),
                        "data1_unit": theme.get('data1_unit'),
                        "data2_nm": theme.get('data2_nm'),
                        "data2_unit": theme.get('data2_unit')
                    },
                    "result_data": theme_data_result.get('resultData', [])
                })
                print("✓")
            else:
                print("⚠️")
        
        thema_data["categories"][category_code] = category_data
        print(f"  └─ 완료: {len(category_data['themes'])}개 주제도 수집")
    
    # 3. 최종 JSON 파일 저장
    output_file = "sgis_thema_stats.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(thema_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 통계주제도 데이터 수집 완료!")
    print("=" * 60)
    
    total_themes = sum(len(cat.get('themes', [])) for cat in thema_data['categories'].values())
    print(f"📊 카테고리: {len(thema_data['categories'])}개")
    print(f"📊 주제도: {total_themes}개")
    print(f"💾 저장 파일: {output_file}")
    print("=" * 60)
    
    print("\n📋 수집된 카테고리:")
    for code, cat in thema_data['categories'].items():
        print(f"  {code}: {cat['name']} ({len(cat.get('themes', []))}개 주제도)")

if __name__ == "__main__":
    collect_thema_stats()

