#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from collections import defaultdict

print("=== 전국 시군구 종합 데이터 생성 ===\n")

census_dir = '/Users/hopidad/Desktop/workspace/census'

# 1. 시군구 매핑 로드
print("📋 시군구 이름 로드...")
df_admin = pd.read_excel('election/행정동_법정동_20250901.xlsx')

# 시군구만 필터링 (10자리, 뒤 5자리가 00000)
df_sigungu = df_admin[
    (df_admin['행정동코드'].astype(str).str.len() == 10) & 
    (df_admin['행정동코드'].astype(str).str.endswith('00000')) &
    (df_admin['시군구명'].notna())
]

sigungu_map = {}
for _, row in df_sigungu.iterrows():
    code_10 = str(row['행정동코드'])
    code_5 = code_10[:5]  # 앞 5자리
    
    sigungu_map[code_5] = {
        'code_10': code_10,
        'sido': row['시도명'],
        'sigungu': row['시군구명']
    }

print(f"✅ {len(sigungu_map)}개 시군구 매핑")

# 2. 연도별 데이터 파싱
years = ['2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2010', '2005', '2000']

national_data = {}

for sigungu_code, info in sigungu_map.items():
    national_data[sigungu_code] = {
        'code': sigungu_code,
        'sido': info['sido'],
        'sigungu': info['sigungu'],
        'population': {},
        'density': {},
        'avg_age': {},
        'aging_index': {},
        'youth_ratio': {},
        'elderly_ratio': {}
    }

print(f"\n데이터 파싱 시작...\n")

for year in years:
    print(f"📅 {year}년", end=': ')
    
    # 각 시군구별로 동 단위 데이터를 합산
    sigungu_totals = defaultdict(lambda: {
        'population': 0,
        'density_sum': 0,
        'density_count': 0,
        'age_sum': 0,
        'age_count': 0,
        'aging_sum': 0,
        'aging_count': 0,
        'youth_sum': 0,
        'youth_count': 0,
        'elderly_sum': 0,
        'elderly_count': 0
    })
    
    # 총인구
    pop_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(총인구).txt')
    if os.path.exists(pop_file):
        with open(pop_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1].strip()
                    if len(admin_code) >= 5:
                        sigungu_code = admin_code[:5]
                        if sigungu_code in sigungu_map:
                            population = int(parts[3])
                            sigungu_totals[sigungu_code]['population'] += population
    
    # 인구밀도 (평균)
    density_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(인구밀도).txt')
    if os.path.exists(density_file):
        with open(density_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1].strip()
                    if len(admin_code) >= 5:
                        sigungu_code = admin_code[:5]
                        if sigungu_code in sigungu_map:
                            try:
                                density = float(parts[3])
                                sigungu_totals[sigungu_code]['density_sum'] += density
                                sigungu_totals[sigungu_code]['density_count'] += 1
                            except:
                                pass
    
    # 평균나이
    age_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(평균나이).txt')
    if os.path.exists(age_file):
        with open(age_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1].strip()
                    if len(admin_code) >= 5:
                        sigungu_code = admin_code[:5]
                        if sigungu_code in sigungu_map:
                            try:
                                avg_age = float(parts[3])
                                sigungu_totals[sigungu_code]['age_sum'] += avg_age
                                sigungu_totals[sigungu_code]['age_count'] += 1
                            except:
                                pass
    
    # 노령화지수
    aging_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(노령화지수).txt')
    if os.path.exists(aging_file):
        with open(aging_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1].strip()
                    if len(admin_code) >= 5:
                        sigungu_code = admin_code[:5]
                        if sigungu_code in sigungu_map:
                            try:
                                aging_index = float(parts[3])
                                sigungu_totals[sigungu_code]['aging_sum'] += aging_index
                                sigungu_totals[sigungu_code]['aging_count'] += 1
                            except:
                                pass
    
    # 데이터 저장
    for sigungu_code, totals in sigungu_totals.items():
        if sigungu_code in national_data:
            national_data[sigungu_code]['population'][year] = totals['population']
            
            if totals['density_count'] > 0:
                national_data[sigungu_code]['density'][year] = round(
                    totals['density_sum'] / totals['density_count'], 2
                )
            
            if totals['age_count'] > 0:
                national_data[sigungu_code]['avg_age'][year] = round(
                    totals['age_sum'] / totals['age_count'], 1
                )
            
            if totals['aging_count'] > 0:
                national_data[sigungu_code]['aging_index'][year] = round(
                    totals['aging_sum'] / totals['aging_count'], 1
                )
    
    print(f"{len(sigungu_totals)}개 시군구")

# 저장
output_file = 'national_comprehensive_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(national_data, f, ensure_ascii=False, indent=2)

file_size_mb = os.path.getsize(output_file) / 1024 / 1024

print(f"\n✅ {output_file} 생성 완료 ({file_size_mb:.2f}MB)")
print(f"✅ 전국 {len(national_data)}개 행정구역 (시도 17 + 시군구 252 + 동 3,558)")

# 최종 통계
print(f"\n📊 최종 통계:")
sido_pop = defaultdict(int)
for code, data in national_data.items():
    if data['level'] == 'sigungu':
        sido_pop[data['sido']] += data['population'].get('2023', 0)

print(f"\n시도별 인구 (2023년):")
for sido, pop in sorted(sido_pop.items(), key=lambda x: x[1], reverse=True):
    print(f"  {sido}: {pop:,}명")

# 샘플 출력
print(f"\n📋 샘플 (서울 5개 구):")
count = 0
for code, data in sorted(national_data.items()):
    if data['level'] == 'sigungu' and data['sido'] == '서울특별시' and count < 5:
        print(f"\n{data['sigungu']}:")
        print(f"  2023년: {data['population'].get('2023', 0):,}명")
        print(f"  2020년: {data['population'].get('2020', 0):,}명")
        print(f"  평균나이: {data['avg_age'].get('2023', 0)}세")
        print(f"  노령화지수: {data['aging_index'].get('2023', 0)}")
        count += 1
EOF
