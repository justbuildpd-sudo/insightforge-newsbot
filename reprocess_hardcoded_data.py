#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
하드코딩된 데이터 재가공기
동>구>시>도 순서로 데이터를 재구성하고 합산값까지 계산
"""

import json
from collections import defaultdict

def create_hierarchical_data():
    """동>구>시>도 순서로 데이터 재구성"""
    print("📊 하드코딩된 데이터 재가공 시작...")
    
    # 원본 하드코딩 데이터 (dashboard.html에서 추출)
    raw_data = {
        # 시도 데이터
        "sido_data": {
            "서울특별시": {"code": "11", "total_regions": 25},
            "부산광역시": {"code": "26", "total_regions": 16},
            "대구광역시": {"code": "27", "total_regions": 8},
            "인천광역시": {"code": "28", "total_regions": 10},
            "광주광역시": {"code": "29", "total_regions": 5},
            "대전광역시": {"code": "30", "total_regions": 5},
            "울산광역시": {"code": "31", "total_regions": 5},
            "세종특별자치시": {"code": "36", "total_regions": 1},
            "경기도": {"code": "41", "total_regions": 31},
            "강원특별자치도": {"code": "42", "total_regions": 18},
            "충청북도": {"code": "43", "total_regions": 11},
            "충청남도": {"code": "44", "total_regions": 15},
            "전북특별자치도": {"code": "45", "total_regions": 14},
            "전라남도": {"code": "46", "total_regions": 22},
            "경상북도": {"code": "47", "total_regions": 23},
            "경상남도": {"code": "48", "total_regions": 18},
            "제주특별자치도": {"code": "49", "total_regions": 2}
        },
        
        # 시군구 데이터 (서울 전체)
        "sigungu_data": {
            "종로구": {"population": 150000, "area": 23.9},
            "중구": {"population": 130000, "area": 9.96},
            "용산구": {"population": 240000, "area": 21.87},
            "성동구": {"population": 300000, "area": 16.85},
            "광진구": {"population": 350000, "area": 17.05},
            "동대문구": {"population": 350000, "area": 14.22},
            "중랑구": {"population": 400000, "area": 18.51},
            "성북구": {"population": 450000, "area": 24.57},
            "강북구": {"population": 320000, "area": 23.61},
            "도봉구": {"population": 350000, "area": 20.7},
            "노원구": {"population": 550000, "area": 35.44},
            "은평구": {"population": 480000, "area": 29.7},
            "서대문구": {"population": 320000, "area": 17.61},
            "마포구": {"population": 380000, "area": 23.87},
            "양천구": {"population": 480000, "area": 17.4},
            "강서구": {"population": 580000, "area": 41.4},
            "구로구": {"population": 420000, "area": 20.12},
            "금천구": {"population": 240000, "area": 13.01},
            "영등포구": {"population": 400000, "area": 24.56},
            "동작구": {"population": 400000, "area": 16.35},
            "관악구": {"population": 520000, "area": 29.57},
            "서초구": {"population": 450000, "area": 47.0},
            "강남구": {"population": 550000, "area": 39.5},
            "송파구": {"population": 650000, "area": 33.87},
            "강동구": {"population": 440000, "area": 24.59}
        },
        
        # 동별 데이터 (강남구 일부)
        "dong_data": {
            "신사동": {"population": 12500, "households": 5200, "area": 1.2},
            "논현1동": {"population": 18500, "households": 7800, "area": 1.8},
            "논현2동": {"population": 16200, "households": 6800, "area": 1.5},
            "압구정동": {"population": 22100, "households": 9200, "area": 2.1},
            "청담동": {"population": 19800, "households": 8200, "area": 1.9},
            "삼성1동": {"population": 15600, "households": 6500, "area": 1.4},
            "삼성2동": {"population": 14200, "households": 5900, "area": 1.3},
            "대치1동": {"population": 17800, "households": 7400, "area": 1.7},
            "대치2동": {"population": 16500, "households": 6900, "area": 1.6},
            "대치4동": {"population": 19200, "households": 8000, "area": 1.8},
            "역삼1동": {"population": 20100, "households": 8400, "area": 1.9},
            "역삼2동": {"population": 18800, "households": 7800, "area": 1.8},
            "도곡1동": {"population": 17400, "households": 7200, "area": 1.6},
            "도곡2동": {"population": 15900, "households": 6600, "area": 1.5},
            "개포1동": {"population": 13600, "households": 5700, "area": 1.3},
            "개포2동": {"population": 14800, "households": 6200, "area": 1.4},
            "개포4동": {"population": 16300, "households": 6800, "area": 1.5},
            "일원1동": {"population": 12700, "households": 5300, "area": 1.2},
            "일원본동": {"population": 14100, "households": 5900, "area": 1.3},
            "수서동": {"population": 19500, "households": 8100, "area": 1.8},
            "세곡동": {"population": 16800, "households": 7000, "area": 1.6}
        },
        
        # SGIS 동별 데이터
        "sgis_dong_data": {
            "종로구 청운효자동": {"density": 7236.1, "avg_age": 45.2, "year": "2023"},
            "종로구 사직동": {"density": 1431.8, "avg_age": 42.8, "year": "2023"},
            "종로구 삼청동": {"density": 4019.3, "avg_age": 48.5, "year": "2023"},
            "종로구 부암동": {"density": 1842.7, "avg_age": 46.3, "year": "2023"},
            "종로구 평창동": {"density": 20466.1, "avg_age": 44.1, "year": "2023"},
            "종로구 무악동": {"density": 27031.7, "avg_age": 47.9, "year": "2023"},
            "종로구 교남동": {"density": 7086.7, "avg_age": 43.6, "year": "2023"},
            "종로구 가회동": {"density": 11500.0, "avg_age": 45.8, "year": "2023"},
            "종로구 종로1.2.3.4가동": {"density": 12500.0, "avg_age": 42.3, "year": "2023"},
            "종로구 종로5.6가동": {"density": 15000.0, "avg_age": 44.7, "year": "2023"},
            "종로구 이화동": {"density": 18000.0, "avg_age": 46.2, "year": "2023"},
            "종로구 혜화동": {"density": 22000.0, "avg_age": 48.9, "year": "2023"},
            "종로구 명륜3가동": {"density": 25000.0, "avg_age": 45.4, "year": "2023"},
            "종로구 창신동": {"density": 20000.0, "avg_age": 43.8, "year": "2023"},
            "종로구 숭인동": {"density": 18000.0, "avg_age": 47.1, "year": "2023"},
            "종로구 숭인2동": {"density": 16000.0, "avg_age": 46.5, "year": "2023"},
            "중구 소공동": {"density": 8000.0, "avg_age": 44.2, "year": "2023"},
            "중구 회현동": {"density": 12000.0, "avg_age": 42.6, "year": "2023"},
            "중구 명동": {"density": 15000.0, "avg_age": 45.8, "year": "2023"},
            "중구 필동": {"density": 18000.0, "avg_age": 47.3, "year": "2023"},
            "중구 장충동": {"density": 20000.0, "avg_age": 46.9, "year": "2023"},
            "중구 광희동": {"density": 22000.0, "avg_age": 44.5, "year": "2023"},
            "중구 을지로동": {"density": 25000.0, "avg_age": 43.1, "year": "2023"},
            "중구 신당동": {"density": 18000.0, "avg_age": 45.7, "year": "2023"},
            "중구 다산동": {"density": 16000.0, "avg_age": 48.2, "year": "2023"},
            "중구 약수동": {"density": 14000.0, "avg_age": 46.8, "year": "2023"},
            "중구 청구동": {"density": 12000.0, "avg_age": 44.9, "year": "2023"},
            "중구 신당5동": {"density": 10000.0, "avg_age": 47.4, "year": "2023"},
            "중구 동화동": {"density": 8000.0, "avg_age": 45.6, "year": "2023"},
            "중구 황학동": {"density": 6000.0, "avg_age": 48.1, "year": "2023"},
            "중구 중림동": {"density": 4000.0, "avg_age": 46.3, "year": "2023"},
            "용산구 후암동": {"density": 15000.0, "avg_age": 44.7, "year": "2023"},
            "용산구 용산2가동": {"density": 18000.0, "avg_age": 42.3, "year": "2023"},
            "용산구 남영동": {"density": 20000.0, "avg_age": 45.9, "year": "2023"},
            "용산구 청파동": {"density": 22000.0, "avg_age": 47.2, "year": "2023"},
            "용산구 원효로1동": {"density": 25000.0, "avg_age": 46.8, "year": "2023"},
            "용산구 원효로2동": {"density": 23000.0, "avg_age": 44.5, "year": "2023"},
            "용산구 효창동": {"density": 21000.0, "avg_age": 48.1, "year": "2023"},
            "용산구 용문동": {"density": 19000.0, "avg_age": 45.6, "year": "2023"},
            "용산구 한강로동": {"density": 17000.0, "avg_age": 43.9, "year": "2023"},
            "용산구 이촌1동": {"density": 15000.0, "avg_age": 47.3, "year": "2023"},
            "용산구 이촌2동": {"density": 13000.0, "avg_age": 45.8, "year": "2023"},
            "용산구 이태원1동": {"density": 11000.0, "avg_age": 42.7, "year": "2023"},
            "용산구 이태원2동": {"density": 9000.0, "avg_age": 44.2, "year": "2023"},
            "용산구 한남동": {"density": 7000.0, "avg_age": 46.5, "year": "2023"},
            "용산구 서빙고동": {"density": 5000.0, "avg_age": 48.9, "year": "2023"},
            "용산구 보광동": {"density": 3000.0, "avg_age": 45.3, "year": "2023"},
            "성동구 왕십리도선동": {"density": 25000.0, "avg_age": 43.8, "year": "2023"},
            "성동구 마장동": {"density": 22000.0, "avg_age": 46.2, "year": "2023"},
            "성동구 사근동": {"density": 20000.0, "avg_age": 44.7, "year": "2023"},
            "성동구 행당1동": {"density": 18000.0, "avg_age": 47.1, "year": "2023"},
            "성동구 행당2동": {"density": 16000.0, "avg_age": 45.9, "year": "2023"},
            "성동구 응봉동": {"density": 14000.0, "avg_age": 48.3, "year": "2023"},
            "성동구 금호1가동": {"density": 12000.0, "avg_age": 46.5, "year": "2023"},
            "성동구 금호2.3가동": {"density": 10000.0, "avg_age": 44.8, "year": "2023"},
            "성동구 금호4가동": {"density": 8000.0, "avg_age": 47.2, "year": "2023"},
            "성동구 옥수동": {"density": 6000.0, "avg_age": 45.6, "year": "2023"},
            "성동구 성수1가1동": {"density": 4000.0, "avg_age": 43.9, "year": "2023"},
            "성동구 성수1가2동": {"density": 2000.0, "avg_age": 46.1, "year": "2023"},
            "성동구 성수2가1동": {"density": 0.0, "avg_age": 44.5, "year": "2023"},
            "성동구 성수2가3동": {"density": 0.0, "avg_age": 47.8, "year": "2023"},
            "성동구 송정동": {"density": 0.0, "avg_age": 45.3, "year": "2023"},
            "성동구 용답동": {"density": 0.0, "avg_age": 48.6, "year": "2023"},
            "광진구 중곡1동": {"density": 15000.0, "avg_age": 44.2, "year": "2023"},
            "광진구 중곡2동": {"density": 18000.0, "avg_age": 46.7, "year": "2023"},
            "광진구 중곡3동": {"density": 20000.0, "avg_age": 45.1, "year": "2023"},
            "광진구 중곡4동": {"density": 22000.0, "avg_age": 47.4, "year": "2023"},
            "광진구 능동": {"density": 25000.0, "avg_age": 46.8, "year": "2023"},
            "광진구 구의1동": {"density": 23000.0, "avg_age": 44.9, "year": "2023"},
            "광진구 구의2동": {"density": 21000.0, "avg_age": 45.6, "year": "2023"},
            "광진구 구의3동": {"density": 19000.0, "avg_age": 47.2, "year": "2023"},
            "광진구 광장동": {"density": 17000.0, "avg_age": 45.8, "year": "2023"},
            "광진구 자양1동": {"density": 15000.0, "avg_age": 43.7, "year": "2023"},
            "광진구 자양2동": {"density": 13000.0, "avg_age": 46.3, "year": "2023"},
            "광진구 자양3동": {"density": 11000.0, "avg_age": 44.8, "year": "2023"},
            "광진구 자양4동": {"density": 9000.0, "avg_age": 47.5, "year": "2023"},
            "광진구 화양동": {"density": 7000.0, "avg_age": 45.9, "year": "2023"},
            "강남구 신사동": {"density": 12000.0, "avg_age": 42.3, "year": "2023"},
            "강남구 논현1동": {"density": 15000.0, "avg_age": 44.7, "year": "2023"},
            "강남구 논현2동": {"density": 18000.0, "avg_age": 46.1, "year": "2023"},
            "강남구 압구정동": {"density": 20000.0, "avg_age": 48.5, "year": "2023"},
            "강남구 청담동": {"density": 22000.0, "avg_age": 45.8, "year": "2023"},
            "강남구 삼성1동": {"density": 25000.0, "avg_age": 47.2, "year": "2023"},
            "강남구 삼성2동": {"density": 23000.0, "avg_age": 44.6, "year": "2023"},
            "강남구 대치1동": {"density": 21000.0, "avg_age": 46.9, "year": "2023"},
            "강남구 대치2동": {"density": 19000.0, "avg_age": 45.3, "year": "2023"},
            "강남구 대치4동": {"density": 17000.0, "avg_age": 47.7, "year": "2023"},
            "강남구 역삼1동": {"density": 15000.0, "avg_age": 43.8, "year": "2023"},
            "강남구 역삼2동": {"density": 13000.0, "avg_age": 46.2, "year": "2023"},
            "강남구 도곡1동": {"density": 11000.0, "avg_age": 44.9, "year": "2023"},
            "강남구 도곡2동": {"density": 9000.0, "avg_age": 47.1, "year": "2023"},
            "강남구 개포1동": {"density": 7000.0, "avg_age": 45.6, "year": "2023"},
            "강남구 개포2동": {"density": 5000.0, "avg_age": 48.3, "year": "2023"},
            "강남구 개포4동": {"density": 3000.0, "avg_age": 46.7, "year": "2023"},
            "강남구 일원1동": {"density": 1000.0, "avg_age": 44.2, "year": "2023"},
            "강남구 일원본동": {"density": 0.0, "avg_age": 47.5, "year": "2023"},
            "강남구 수서동": {"density": 0.0, "avg_age": 45.9, "year": "2023"},
            "강남구 세곡동": {"density": 0.0, "avg_age": 46.4, "year": "2023"}
        }
    }
    
    # 계층적 데이터 구조 생성
    hierarchical_data = {
        "metadata": {
            "created_at": "2025-10-27",
            "data_type": "hierarchical_regional_data",
            "structure": "동>구>시>도",
            "total_sidos": 17,
            "total_sigungus": 0,  # 계산 후 업데이트
            "total_dongs": 0      # 계산 후 업데이트
        },
        "sidos": {},
        "statistics": {
            "total_population": 0,
            "total_area": 0,
            "total_households": 0,
            "avg_density": 0,
            "avg_age": 0
        }
    }
    
    # 시도별 데이터 구성
    for sido_name, sido_info in raw_data["sido_data"].items():
        hierarchical_data["sidos"][sido_name] = {
            "code": sido_info["code"],
            "total_regions": sido_info["total_regions"],
            "sigungus": {},
            "statistics": {
                "total_population": 0,
                "total_area": 0,
                "total_households": 0,
                "avg_density": 0,
                "avg_age": 0,
                "dong_count": 0
            }
        }
    
    # 서울특별시 시군구 데이터 구성
    if "서울특별시" in hierarchical_data["sidos"]:
        seoul_sigungus = hierarchical_data["sidos"]["서울특별시"]["sigungus"]
        
        for sigungu_name, sigungu_info in raw_data["sigungu_data"].items():
            seoul_sigungus[sigungu_name] = {
                "population": sigungu_info["population"],
                "area": sigungu_info["area"],
                "dongs": {},
                "statistics": {
                    "total_population": sigungu_info["population"],
                    "total_area": sigungu_info["area"],
                    "total_households": 0,
                    "avg_density": sigungu_info["population"] / sigungu_info["area"] if sigungu_info["area"] > 0 else 0,
                    "avg_age": 0,
                    "dong_count": 0
                }
            }
    
    # 강남구 동 데이터 구성
    if "강남구" in hierarchical_data["sidos"]["서울특별시"]["sigungus"]:
        gangnam_dongs = hierarchical_data["sidos"]["서울특별시"]["sigungus"]["강남구"]["dongs"]
        
        for dong_name, dong_info in raw_data["dong_data"].items():
            gangnam_dongs[dong_name] = {
                "population": dong_info["population"],
                "households": dong_info["households"],
                "area": dong_info["area"],
                "sgis_data": {},
                "statistics": {
                    "total_population": dong_info["population"],
                    "total_area": dong_info["area"],
                    "total_households": dong_info["households"],
                    "density": dong_info["population"] / dong_info["area"] if dong_info["area"] > 0 else 0,
                    "avg_age": 0
                }
            }
    
    # SGIS 데이터 매칭
    for dong_key, sgis_info in raw_data["sgis_dong_data"].items():
        parts = dong_key.split(" ")
        if len(parts) >= 2:
            sigungu_name = parts[0]
            dong_name = " ".join(parts[1:])
            
            # 강남구 동 데이터에 SGIS 정보 추가
            if (sigungu_name == "강남구" and 
                dong_name in hierarchical_data["sidos"]["서울특별시"]["sigungus"]["강남구"]["dongs"]):
                
                hierarchical_data["sidos"]["서울특별시"]["sigungus"]["강남구"]["dongs"][dong_name]["sgis_data"] = {
                    "density": sgis_info["density"],
                    "avg_age": sgis_info["avg_age"],
                    "year": sgis_info["year"]
                }
                
                # 통계 업데이트
                hierarchical_data["sidos"]["서울특별시"]["sigungus"]["강남구"]["dongs"][dong_name]["statistics"]["avg_age"] = sgis_info["avg_age"]
    
    # 합산값 계산
    calculate_statistics(hierarchical_data)
    
    return hierarchical_data

def calculate_statistics(data):
    """동>구>시>도 순서로 합산값 계산"""
    print("📊 합산값 계산 중...")
    
    total_population = 0
    total_area = 0
    total_households = 0
    total_dongs = 0
    total_sigungus = 0
    
    for sido_name, sido_data in data["sidos"].items():
        sido_population = 0
        sido_area = 0
        sido_households = 0
        sido_dongs = 0
        
        for sigungu_name, sigungu_data in sido_data["sigungus"].items():
            sigungu_population = 0
            sigungu_area = 0
            sigungu_households = 0
            sigungu_dongs = 0
            
            for dong_name, dong_data in sigungu_data["dongs"].items():
                sigungu_population += dong_data["population"]
                sigungu_area += dong_data["area"]
                sigungu_households += dong_data["households"]
                sigungu_dongs += 1
                
                total_dongs += 1
            
            # 시군구 통계 업데이트
            sigungu_data["statistics"]["total_population"] = sigungu_population
            sigungu_data["statistics"]["total_area"] = sigungu_area
            sigungu_data["statistics"]["total_households"] = sigungu_households
            sigungu_data["statistics"]["dong_count"] = sigungu_dongs
            sigungu_data["statistics"]["avg_density"] = sigungu_population / sigungu_area if sigungu_area > 0 else 0
            
            sido_population += sigungu_population
            sido_area += sigungu_area
            sido_households += sigungu_households
            sido_dongs += sigungu_dongs
            
            total_sigungus += 1
        
        # 시도 통계 업데이트
        sido_data["statistics"]["total_population"] = sido_population
        sido_data["statistics"]["total_area"] = sido_area
        sido_data["statistics"]["total_households"] = sido_households
        sido_data["statistics"]["dong_count"] = sido_dongs
        sido_data["statistics"]["avg_density"] = sido_population / sido_area if sido_area > 0 else 0
        
        total_population += sido_population
        total_area += sido_area
        total_households += sido_households
    
    # 전체 통계 업데이트
    data["statistics"]["total_population"] = total_population
    data["statistics"]["total_area"] = total_area
    data["statistics"]["total_households"] = total_households
    data["statistics"]["avg_density"] = total_population / total_area if total_area > 0 else 0
    data["metadata"]["total_sigungus"] = total_sigungus
    data["metadata"]["total_dongs"] = total_dongs
    
    print(f"✅ 합산값 계산 완료:")
    print(f"   - 총 인구: {total_population:,}명")
    print(f"   - 총 면적: {total_area:.1f}km²")
    print(f"   - 총 세대: {total_households:,}세대")
    print(f"   - 총 동: {total_dongs}개")
    print(f"   - 총 시군구: {total_sigungus}개")

def save_hierarchical_data(data):
    """계층적 데이터 저장"""
    print("💾 계층적 데이터 저장 중...")
    
    # 전체 데이터 저장
    with open('hierarchical_regional_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 대시보드용 간소화된 데이터 저장
    dashboard_data = {
        "metadata": data["metadata"],
        "statistics": data["statistics"],
        "sidos": {}
    }
    
    for sido_name, sido_data in data["sidos"].items():
        dashboard_data["sidos"][sido_name] = {
            "code": sido_data["code"],
            "statistics": sido_data["statistics"],
            "sigungus": {}
        }
        
        for sigungu_name, sigungu_data in sido_data["sigungus"].items():
            dashboard_data["sidos"][sido_name]["sigungus"][sigungu_name] = {
                "statistics": sigungu_data["statistics"],
                "dongs": {}
            }
            
            for dong_name, dong_data in sigungu_data["dongs"].items():
                dashboard_data["sidos"][sido_name]["sigungus"][sigungu_name]["dongs"][dong_name] = {
                    "statistics": dong_data["statistics"],
                    "sgis_data": dong_data.get("sgis_data", {})
                }
    
    with open('dashboard_hierarchical_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 데이터 저장 완료:")
    print("   - hierarchical_regional_data.json (전체 데이터)")
    print("   - dashboard_hierarchical_data.json (대시보드용)")

def main():
    """메인 실행 함수"""
    print("=== 하드코딩된 데이터 재가공기 시작 ===")
    
    # 계층적 데이터 생성
    hierarchical_data = create_hierarchical_data()
    
    # 데이터 저장
    save_hierarchical_data(hierarchical_data)
    
    print("\n🎉 하드코딩된 데이터 재가공 완료!")
    print("📊 동>구>시>도 순서로 데이터 구조화")
    print("📊 모든 레벨에서 합산값 계산 완료")

if __name__ == "__main__":
    main()
