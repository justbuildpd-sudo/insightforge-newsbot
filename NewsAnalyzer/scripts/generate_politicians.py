#!/usr/bin/env python3
"""
정치인 목록 생성 - InsightForge 데이터에서 추출
"""

import json
import gzip
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR.parent / 'insightforge-web' / 'data'
OUTPUT_FILE = BASE_DIR / 'data' / 'politicians.json'

def load_json_gz(filepath):
    """gzip JSON 파일 로드"""
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        return json.load(f)

def generate_politicians():
    """정치인 목록 생성"""
    politicians = []
    
    # 1. 국회의원 (22대)
    print("📖 국회의원 로딩...")
    assembly_file = DATA_DIR / 'national_assembly_22nd_real.json'
    if assembly_file.exists():
        with open(assembly_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for region, pols in data.items():
                if isinstance(pols, list):
                    for pol in pols:
                        politicians.append({
                            **pol,
                            'type': '국회의원',
                            'level': 'national'
                        })
    
    # 2. 시의원 (8회)
    print("📖 시의원 로딩...")
    si_uiwon_file = DATA_DIR / 'seoul_si_uiwon_8th.json.gz'
    if si_uiwon_file.exists():
        data = load_json_gz(si_uiwon_file)
        for gu, pols in data.items():
            if isinstance(pols, list):
                for pol in pols:
                    politicians.append({
                        **pol,
                        'type': '시의원',
                        'level': 'city',
                        'gu': gu
                    })
    
    # 3. 구의원 (8회)
    print("📖 구의원 로딩...")
    gu_uiwon_file = DATA_DIR / 'seoul_gu_uiwon_8th.json.gz'
    if gu_uiwon_file.exists():
        data = load_json_gz(gu_uiwon_file)
        for gu, pols in data.items():
            if isinstance(pols, list):
                for pol in pols:
                    politicians.append({
                        **pol,
                        'type': '구의원',
                        'level': 'district',
                        'gu': gu
                    })
    
    # 4. 구청장
    print("📖 구청장 로딩...")
    gu_mayor_file = DATA_DIR / 'seoul_gu_mayor_8th.json'
    if gu_mayor_file.exists():
        with open(gu_mayor_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for gu, mayor_data in data.items():
                if isinstance(mayor_data, dict):
                    politicians.append({
                        **mayor_data,
                        'type': '구청장',
                        'level': 'district',
                        'gu': gu
                    })
    
    # 5. 시장
    print("📖 시장 로딩...")
    mayor_file = DATA_DIR / 'seoul_mayor_8th.json'
    if mayor_file.exists():
        with open(mayor_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and 'name' in value:
                        politicians.append({
                            **value,
                            'type': '시장',
                            'level': 'city'
                        })
    
    # 중복 제거 (이름 기준)
    unique_politicians = {}
    for pol in politicians:
        name = pol.get('name', '')
        if name and name not in unique_politicians:
            unique_politicians[name] = pol
    
    final_list = list(unique_politicians.values())
    
    # 저장
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 완료!")
    print(f"📊 총 {len(final_list)}명 (중복 제거 후)")
    print(f"💾 저장: {OUTPUT_FILE}")
    
    # 통계
    types_count = {}
    for pol in final_list:
        pol_type = pol.get('type', '기타')
        types_count[pol_type] = types_count.get(pol_type, 0) + 1
    
    print(f"\n📊 유형별 통계:")
    for pol_type, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pol_type}: {count}명")
    
    return final_list

if __name__ == '__main__':
    politicians = generate_politicians()

