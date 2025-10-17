#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from collections import defaultdict

print("=== 전국 단위 인구 데이터 생성 ===\n")

census_dir = '/Users/hopidad/Desktop/workspace/census'

# 행정구역 코드 매핑 (앞 5자리)
admin_code_map = {}

# 연도별 데이터 구조
years = ['2000', '2005', '2010', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']

# 통합 데이터
national_data = defaultdict(lambda: {
    'admin_code': '',
    'sido': '',
    'sigungu': '',
    'dong': '',
    'population': {},
    'density': {},
    'avg_age': {},
    'aging_index': {},
    'youth_ratio': {},
    'elderly_ratio': {}
})

# 1. 2023년 총인구 데이터로 행정구역 매핑 생성
total_pop_file = os.path.join(census_dir, '(행정구역)2024년기준_2023년_인구총괄(총인구).txt')

print(f"📊 행정구역 코드 매핑 생성...")
with open(total_pop_file, 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('^')
        if len(parts) >= 4:
            year = parts[0]
            admin_code = parts[1]  # 8자리 코드
            population = int(parts[3])
            
            # 5자리 코드로 시군구 구분
            code_5 = admin_code[:5]
            
            if code_5 not in admin_code_map:
                # 행정구역 코드 해석
                sido_code = admin_code[:2]
                sigungu_code = admin_code[2:5]
                
                admin_code_map[code_5] = {
                    'code': admin_code,
                    'sido_code': sido_code,
                    'sigungu_code': sigungu_code
                }

print(f"✅ 총 {len(admin_code_map)}개 행정구역 발견\n")

# 2. 각 연도별 데이터 파싱
for year in years:
    print(f"📅 {year}년 데이터 처리 중...")
    
    # 총인구
    pop_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(총인구).txt')
    if os.path.exists(pop_file):
        with open(pop_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]  # 5자리만 사용
                    population = int(parts[3])
                    national_data[admin_code]['admin_code'] = admin_code
                    national_data[admin_code]['population'][year] = population
    
    # 인구밀도
    density_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(인구밀도).txt')
    if os.path.exists(density_file):
        with open(density_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    density = float(parts[3])
                    national_data[admin_code]['density'][year] = density
    
    # 평균나이
    age_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(평균나이).txt')
    if os.path.exists(age_file):
        with open(age_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    avg_age = float(parts[3])
                    national_data[admin_code]['avg_age'][year] = avg_age
    
    # 노령화지수
    aging_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(노령화지수).txt')
    if os.path.exists(aging_file):
        with open(aging_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    aging_index = float(parts[3])
                    national_data[admin_code]['aging_index'][year] = aging_index
    
    # 유년부양비
    youth_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(유년부양비).txt')
    if os.path.exists(youth_file):
        with open(youth_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    youth_ratio = float(parts[3])
                    national_data[admin_code]['youth_ratio'][year] = youth_ratio
    
    # 노년부양비
    elderly_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(노년부양비).txt')
    if os.path.exists(elderly_file):
        with open(elderly_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    elderly_ratio = float(parts[3])
                    national_data[admin_code]['elderly_ratio'][year] = elderly_ratio

print(f"\n✅ 총 {len(national_data)}개 행정구역 데이터 생성")

# 3. 시도/시군구/동 이름 매핑 (행정구역 코드 기반)
sido_names = {
    '11': '서울특별시', '26': '부산광역시', '27': '대구광역시', '28': '인천광역시',
    '29': '광주광역시', '30': '대전광역시', '31': '울산광역시', '36': '세종특별자치시',
    '41': '경기도', '42': '강원특별자치도', '43': '충청북도', '44': '충청남도',
    '45': '전북특별자치도', '46': '전라남도', '47': '경상북도', '48': '경상남도',
    '50': '제주특별자치도'
}

# 시군구 코드별 이름은 실제 데이터에서 추출 필요
# 일단 코드만 저장
for code, data in national_data.items():
    sido_code = code[:2]
    data['sido'] = sido_names.get(sido_code, f"시도코드{sido_code}")
    data['sigungu_code'] = code[2:5]

# 4. 데이터 저장
output_file = 'national_population_comprehensive.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dict(national_data), f, ensure_ascii=False, indent=2)

file_size_mb = os.path.getsize(output_file) / 1024 / 1024

print(f"\n✅ {output_file} 생성 완료")
print(f"파일 크기: {file_size_mb:.2f}MB")

# 5. 통계
print(f"\n📊 데이터 통계:")
sido_counts = defaultdict(int)
for code, data in national_data.items():
    sido_counts[data['sido']] += 1

for sido, count in sorted(sido_counts.items()):
    print(f"  {sido}: {count}개 행정구역")

# 샘플 데이터 출력
print(f"\n📋 샘플 데이터 (서울 3개):")
seoul_count = 0
for code, data in sorted(national_data.items()):
    if data['sido'] == '서울특별시' and seoul_count < 3:
        print(f"\n{code}:")
        print(f"  시도: {data['sido']}")
        print(f"  2023년 인구: {data['population'].get('2023', 0):,}명")
        print(f"  2023년 평균나이: {data['avg_age'].get('2023', 0):.1f}세")
        print(f"  2023년 노령화지수: {data['aging_index'].get('2023', 0):.1f}")
        seoul_count += 1

