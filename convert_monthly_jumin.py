#!/usr/bin/env python3
"""
월별 주민등록 인구 데이터 변환
2022-2025년 데이터를 JSON으로 변환
"""

import pandas as pd
import json
from pathlib import Path
import glob
import re

def parse_number(val):
    """쉼표 제거하고 숫자로 변환"""
    if pd.isna(val):
        return 0
    s = str(val).replace(',', '').strip()
    try:
        return int(float(s))
    except:
        return 0

# 데이터 수집
monthly_data = {}

# URL 인코딩된 파일 찾기
human_files = glob.glob('human/*.csv')
target_files = sorted([f for f in human_files if any(str(y) in f for y in [2022, 2023, 2024, 2025])])

print(f'📁 발견된 파일: {len(target_files)}개\n')

for file_path in target_files:
    print(f'📂 읽는 중: {Path(file_path).name[:40]}...')
    
    try:
        df = pd.read_csv(file_path, encoding='cp949')
        
        # 각 행은 하나의 행정구역
        for _, row in df.iterrows():
            try:
                # 행정구역 파싱 (예: "전국  (1000000000)")
                admin_cell = str(row['행정구역']).strip()
                code_match = re.search(r'\((\d+)\)', admin_cell)
                if not code_match:
                    continue
                
                admin_code = code_match.group(1)
                admin_name = admin_cell.split('(')[0].strip()
                
                # 첫 발견 시 초기화, 이후엔 추가만
                if admin_code not in monthly_data:
                    monthly_data[admin_code] = {
                        'code': admin_code,
                        'name': admin_name,
                        'monthly': []
                    }
                else:
                    # 이름 업데이트 (최신 것 사용)
                    if admin_name:
                        monthly_data[admin_code]['name'] = admin_name
                
                # 각 월별 컬럼 파싱
                for col in df.columns:
                    if '_총인구수' in col and '년' in col and '월' in col:
                        # "2022년01월_총인구수" -> "2022", "01"
                        year_month = col.split('_')[0]  # "2022년01월"
                        year_str = year_month.split('년')[0]
                        month_str = year_month.split('년')[1].replace('월', '').zfill(2)
                        
                        total_col = f'{year_month}_총인구수'
                        male_col = f'{year_month}_남자 인구수'
                        female_col = f'{year_month}_여자 인구수'
                        household_col = f'{year_month}_세대수'
                        
                        total_pop = parse_number(row.get(total_col, 0))
                        male_pop = parse_number(row.get(male_col, 0))
                        female_pop = parse_number(row.get(female_col, 0))
                        household = parse_number(row.get(household_col, 0))
                        
                        if total_pop == 0:
                            continue
                        
                        monthly_data[admin_code]['monthly'].append({
                            'year': int(year_str),
                            'month': int(month_str),
                            'date': f'{year_str}-{month_str}',
                            'population': total_pop,
                            'male': male_pop,
                            'female': female_pop,
                            'household': household,
                            'change': 0  # 나중에 계산
                        })
                
            except Exception as e:
                continue
        
        print(f'   ✅ 완료\n')
        
    except Exception as e:
        print(f'   ❌ 에러: {e}\n')
        continue

# 날짜순 정렬 및 증감 계산
for code in monthly_data:
    monthly_data[code]['monthly'].sort(key=lambda x: (x['year'], x['month']))
    
    # 증감 계산
    for i in range(1, len(monthly_data[code]['monthly'])):
        curr = monthly_data[code]['monthly'][i]
        prev = monthly_data[code]['monthly'][i-1]
        curr['change'] = curr['population'] - prev['population']

# 통계
total_regions = len(monthly_data)
total_months = sum(len(v['monthly']) for v in monthly_data.values())

print(f'✅ 변환 완료:')
print(f'   지역 수: {total_regions:,}')
print(f'   총 월별 데이터: {total_months:,}')
print(f'   평균 월수/지역: {total_months/total_regions if total_regions > 0 else 0:.1f}개월')

# 샘플 확인
sample_code = '1168000000'  # 강남구
if sample_code in monthly_data:
    sample_months = len(monthly_data[sample_code]['monthly'])
    print(f'\n📊 강남구 샘플:')
    print(f'   월별 데이터: {sample_months}개월')
    if sample_months > 0:
        first = monthly_data[sample_code]['monthly'][0]
        last = monthly_data[sample_code]['monthly'][-1]
        print(f'   기간: {first["date"]} ~ {last["date"]}')
        print(f'   첫 인구: {first["population"]:,}명')
        print(f'   최근 인구: {last["population"]:,}명')
        print(f'   변화: {last["population"] - first["population"]:+,}명')

# 저장
output = {
    'data_source': '주민등록인구통계',
    'period': '2022-01 ~ 2025-09',
    'total_regions': total_regions,
    'regions': monthly_data
}

output_file = 'insightforge-web/data/jumin_monthly_2022_2025.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'\n💾 저장 완료: {output_file}')
print(f'   파일 크기: {Path(output_file).stat().st_size / 1024 / 1024:.1f} MB')
