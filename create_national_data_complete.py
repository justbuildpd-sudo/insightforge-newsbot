#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from collections import defaultdict

print("=== 전국 단위 종합 데이터 생성 ===\n")

census_dir = '/Users/hopidad/Desktop/workspace/census'

# 1. 행정구역 이름 매핑 로드
print("📋 행정구역 이름 로드...")
df_admin = pd.read_excel('election/행정동_법정동_20250901.xlsx')

# 행정동 코드로 매핑 (앞 5자리 기준)
admin_names = {}
for _, row in df_admin.iterrows():
    code = str(row['행정동코드'])
    if len(code) >= 5:
        code_5 = code[:5]
        if code_5 not in admin_names or pd.isna(admin_names.get(code_5, {}).get('dong')):
            admin_names[code_5] = {
                'sido': row['시도명'] if pd.notna(row['시도명']) else '',
                'sigungu': row['시군구명'] if pd.notna(row['시군구명']) else '',
                'dong': row['읍면동명'] if pd.notna(row['읍면동명']) else ''
            }

print(f"✅ {len(admin_names)}개 고유 행정구역 매핑")

# 2. 연도별 인구 데이터 파싱
years = ['2000', '2005', '2010', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']

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

for year in years:
    print(f"📅 {year}년 데이터 처리 중...", end=' ')
    
    count = 0
    
    # 총인구
    pop_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(총인구).txt')
    if os.path.exists(pop_file):
        with open(pop_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code_full = parts[1]
                    admin_code = admin_code_full[:5]
                    population = int(parts[3])
                    
                    national_data[admin_code]['admin_code'] = admin_code
                    national_data[admin_code]['population'][year] = population
                    
                    # 이름 매핑
                    if admin_code in admin_names:
                        national_data[admin_code]['sido'] = admin_names[admin_code]['sido']
                        national_data[admin_code]['sigungu'] = admin_names[admin_code]['sigungu']
                        national_data[admin_code]['dong'] = admin_names[admin_code]['dong']
                    
                    count += 1
    
    # 인구밀도
    density_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(인구밀도).txt')
    if os.path.exists(density_file):
        with open(density_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    try:
                        density = float(parts[3])
                        national_data[admin_code]['density'][year] = density
                    except:
                        pass
    
    # 평균나이
    age_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(평균나이).txt')
    if os.path.exists(age_file):
        with open(age_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    try:
                        avg_age = float(parts[3])
                        national_data[admin_code]['avg_age'][year] = avg_age
                    except:
                        pass
    
    # 노령화지수
    aging_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(노령화지수).txt')
    if os.path.exists(aging_file):
        with open(aging_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    try:
                        aging_index = float(parts[3])
                        national_data[admin_code]['aging_index'][year] = aging_index
                    except:
                        pass
    
    # 유년부양비
    youth_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(유년부양비).txt')
    if os.path.exists(youth_file):
        with open(youth_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    try:
                        youth_ratio = float(parts[3])
                        national_data[admin_code]['youth_ratio'][year] = youth_ratio
                    except:
                        pass
    
    # 노년부양비
    elderly_file = os.path.join(census_dir, f'(행정구역)2024년기준_{year}년_인구총괄(노년부양비).txt')
    if os.path.exists(elderly_file):
        with open(elderly_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('^')
                if len(parts) >= 4:
                    admin_code = parts[1][:5]
                    try:
                        elderly_ratio = float(parts[3])
                        national_data[admin_code]['elderly_ratio'][year] = elderly_ratio
                    except:
                        pass
    
    print(f"{count}개 처리")

print(f"\n✅ 총 {len(national_data)}개 행정구역 데이터 생성")

# 3. 데이터 저장
output_file = 'national_population_comprehensive.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dict(national_data), f, ensure_ascii=False, indent=2)

file_size_mb = os.path.getsize(output_file) / 1024 / 1024

print(f"\n✅ {output_file} 생성 완료")
print(f"파일 크기: {file_size_mb:.2f}MB")

# 4. 통계
print(f"\n📊 시도별 통계:")
sido_stats = defaultdict(lambda: {'count': 0, 'population_2023': 0})

for code, data in national_data.items():
    sido = data['sido']
    if sido:
        sido_stats[sido]['count'] += 1
        sido_stats[sido]['population_2023'] += data['population'].get('2023', 0)

for sido, stats in sorted(sido_stats.items()):
    pop = stats['population_2023']
    if pop > 0:
        print(f"  {sido}: {stats['count']}개 행정구역, 인구 {pop:,}명")

# 5. 샘플 데이터 출력
print(f"\n📋 샘플 데이터:")
samples = [
    ('서울특별시', '종로구', '청운효자동'),
    ('부산광역시', '', ''),
    ('경기도', '', '')
]

sample_count = 0
for code, data in sorted(national_data.items()):
    if sample_count >= 5:
        break
    
    if data['sido'] and data['population'].get('2023', 0) > 10000:
        print(f"\n[{code}] {data['sido']} {data['sigungu']} {data['dong']}")
        print(f"  2023년 인구: {data['population'].get('2023', 0):,}명")
        print(f"  평균나이: {data['avg_age'].get('2023', 0):.1f}세")
        print(f"  인구밀도: {data['density'].get('2023', 0):,.1f}명/km²")
        sample_count += 1

