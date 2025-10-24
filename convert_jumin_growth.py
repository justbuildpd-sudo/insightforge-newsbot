#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주민등록 인구증감 데이터 변환
"""
import csv
import json
import os

# 최신 파일
files = sorted([f for f in os.listdir('humanre') if f.endswith('.csv')])
latest_file = files[-1]

print(f"📂 처리 파일: {latest_file}")

growth_data = {}

filepath = os.path.join('humanre', latest_file)

with open(filepath, 'r', encoding='cp949') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # 헤더 분석
    print(f"\n📊 컬럼 수: {len(header)}")
    
    # 2025년 9월 관련 컬럼 찾기
    sep_cols = {}
    for i, col in enumerate(header):
        if '2025년09월' in col:
            sep_cols[col] = i
    
    print(f"📋 2025년 9월 컬럼: {len(sep_cols)}개")
    
    for row in reader:
        region_name = row[0]
        
        # 행정동 코드 추출
        if '(' not in region_name:
            continue
        
        parts = region_name.split('(')
        full_name = parts[0].strip()
        code_part = parts[1].replace(')', '').strip()
        
        # 동 단위만
        if not code_part or len(code_part) < 10:
            continue
        
        try:
            # 2025년 9월 데이터 추출
            # 인구증감 관련 컬럼들
            data_dict = {}
            
            for col_name, idx in sep_cols.items():
                if idx < len(row):
                    value = row[idx].replace(',', '').strip()
                    try:
                        data_dict[col_name] = int(value) if value and value != '' else 0
                    except ValueError:
                        data_dict[col_name] = value
            
            growth_data[code_part] = {
                'code': code_part,
                'full_name': full_name,
                'data': data_dict
            }
            
        except Exception as e:
            continue

print(f"\n✅ 총 {len(growth_data)}개 행정동 증감 데이터 변환 완료")

# 샘플 출력 - 개포1동
for code, data in growth_data.items():
    if '개포1동' in data['full_name']:
        print(f"\n📍 {data['full_name']} ({code}):")
        print("  2025년 9월 데이터:")
        for key, val in list(data['data'].items())[:10]:
            print(f"    {key}: {val}")
        break

# 저장
output_file = 'insightforge-web/data/jumin_growth_2025.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'source': '행정안전부 주민등록 인구증감',
            'year_month': '2025-09',
            'total_regions': len(growth_data)
        },
        'regions': growth_data
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 저장 완료: {output_file}")

