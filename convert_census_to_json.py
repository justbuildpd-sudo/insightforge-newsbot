#!/usr/bin/env python3
"""
Census 데이터를 JSON으로 변환
전국 모든 시군구 데이터 포함
"""

import os
import json
from collections import defaultdict

CENSUS_DIR = '/Users/hopidad/Desktop/workspace/census'
OUTPUT_FILE = '/Users/hopidad/Desktop/workspace/insightforge-web/data/national_census_data.json'
CODE_MAPPING_FILE = '/Users/hopidad/Desktop/workspace/insightforge-web/data/code_mapping.json'

# 연도 목록
YEARS = [2000, 2005, 2010, 2015, 2020]

# 필요한 데이터 파일 패턴
DATA_FILES = {
    '총인구': '인구총괄(총인구).txt',
    '평균나이': '인구총괄(평균나이).txt',
    '인구밀도': '인구총괄(인구밀도).txt',
    '노령화지수': '인구총괄(노령화지수).txt',
    '노년부양비': '인구총괄(노년부양비).txt',
    '유년부양비': '인구총괄(유년부양비).txt',
}

def load_census_file(filepath):
    """Census txt 파일 로드"""
    data = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('^')
                if len(parts) >= 4:
                    year = parts[0]
                    region_code = parts[1]
                    metric = parts[2]
                    value = parts[3]
                    
                    try:
                        # 숫자로 변환 시도
                        value = float(value)
                        if value == int(value):
                            value = int(value)
                    except:
                        pass
                    
                    if region_code not in data:
                        data[region_code] = {}
                    data[region_code][metric] = value
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return data

def get_region_name_from_code(code):
    """지역 코드에서 시도/시군구 이름 추출 (간단한 버전)"""
    sido_codes = {
        '11': '서울특별시',
        '21': '부산광역시',
        '22': '대구광역시',
        '23': '인천광역시',
        '24': '광주광역시',
        '25': '대전광역시',
        '26': '울산광역시',
        '29': '세종특별자치시',
        '31': '경기도',
        '32': '강원특별자치도',
        '33': '충청북도',
        '34': '충청남도',
        '35': '전북특별자치도',
        '36': '전라남도',
        '37': '경상북도',
        '38': '경상남도',
        '39': '제주특별자치도',
    }
    
    if len(code) >= 2:
        sido_code = code[:2]
        return sido_codes.get(sido_code, f'시도{sido_code}')
    return '알 수 없음'

def convert_census_to_json():
    """Census 데이터를 JSON으로 변환"""
    
    # code_mapping 로드
    code_mapping = {}
    if os.path.exists(CODE_MAPPING_FILE):
        with open(CODE_MAPPING_FILE, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
            code_mapping = mapping_data.get('mapping', {})
        print(f"✅ code_mapping 로드: {len(code_mapping)}개")
    
    national_data = {}
    
    for year in YEARS:
        print(f"\n처리 중: {year}년")
        year_data = {}
        
        for data_name, file_pattern in DATA_FILES.items():
            filename = f"(행정구역)2024년기준_{year}년_{file_pattern}"
            filepath = os.path.join(CENSUS_DIR, filename)
            
            if not os.path.exists(filepath):
                print(f"  파일 없음: {filename}")
                continue
            
            print(f"  로딩: {data_name}")
            file_data = load_census_file(filepath)
            
            for region_code, metrics in file_data.items():
                if region_code not in year_data:
                    year_data[region_code] = {
                        'code': region_code,
                        'sido': get_region_name_from_code(region_code),
                        'year': year
                    }
                
                # 데이터 통합
                for metric_key, metric_value in metrics.items():
                    if 'tot' in metric_key.lower() or 'pop' in metric_key.lower():
                        year_data[region_code]['population'] = metric_value
                    elif 'age' in metric_key.lower() or 'avg' in metric_key.lower():
                        year_data[region_code]['avg_age'] = metric_value
                    elif 'dens' in metric_key.lower():
                        year_data[region_code]['density'] = metric_value
                    elif 'aging' in metric_key.lower() or '노령' in metric_key:
                        year_data[region_code]['aging_index'] = metric_value
        
        # 연도별 데이터 저장
        for region_code, region_data in year_data.items():
            if region_code not in national_data:
                # code_mapping에서 명칭 찾기
                mapping = code_mapping.get(region_code, {})
                full_address = mapping.get('full_address', '')
                address_parts = full_address.split(' ') if full_address else []
                
                national_data[region_code] = {
                    'code': region_code,
                    'sido': region_data['sido'],
                    'full_address': full_address,
                    'sigungu_name': ' '.join(address_parts[1:3]) if len(address_parts) >= 2 else region_code,
                    'emdong_name': ' '.join(address_parts[2:]) if len(address_parts) >= 3 else '',
                    'history': {}
                }
            national_data[region_code]['history'][str(year)] = {
                'population': region_data.get('population'),
                'avg_age': region_data.get('avg_age'),
                'density': region_data.get('density'),
                'aging_index': region_data.get('aging_index')
            }
        
        print(f"  {len(year_data)}개 지역 데이터 수집")
    
    # 최신 데이터를 루트에도 복사
    for region_code, region_data in national_data.items():
        if '2020' in region_data['history']:
            latest = region_data['history']['2020']
            region_data['population'] = latest.get('population')
            region_data['avg_age'] = latest.get('avg_age')
            region_data['density'] = latest.get('density')
            region_data['aging_index'] = latest.get('aging_index')
    
    # 시도별로 그룹화
    sido_grouped = defaultdict(dict)
    for region_code, region_data in national_data.items():
        sido = region_data['sido']
        sido_grouped[sido][region_code] = region_data
    
    # 저장
    output_data = {
        'metadata': {
            'source': 'Census 행정구역별 인구통계',
            'years': YEARS,
            'total_regions': len(national_data),
            'total_sido': len(sido_grouped)
        },
        'by_code': national_data,
        'by_sido': dict(sido_grouped)
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 완료!")
    print(f"📊 총 {len(national_data)}개 지역 데이터")
    print(f"📍 {len(sido_grouped)}개 시도")
    print(f"💾 저장: {OUTPUT_FILE}")
    
    return output_data

if __name__ == '__main__':
    data = convert_census_to_json()
    
    # 통계 출력
    print("\n📊 시도별 지역 수:")
    for sido, regions in sorted(data['by_sido'].items()):
        print(f"  {sido}: {len(regions)}개")

