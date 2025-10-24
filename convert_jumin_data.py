#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주민등록 인구 데이터를 행정동별로 변환
"""
import csv
import json
import os
from collections import defaultdict

# 최신 파일 찾기
human_dir = 'human'
files = sorted([f for f in os.listdir(human_dir) if f.endswith('.csv')])
latest_file = files[-1]

print(f"📂 처리 파일: {latest_file}")

# 데이터 읽기
jumin_data = {}

filepath = os.path.join(human_dir, latest_file)

with open(filepath, 'r', encoding='cp949') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # 2025년 9월 데이터 인덱스 찾기
    sep_idx = None
    for i, col in enumerate(header):
        if '2025년09월_총인구수' in col or '09월_총인구' in col:
            sep_idx = i
            break
    
    if not sep_idx:
        # 마지막 월 데이터 사용
        # 헤더 구조: ..., X월_총인구수, X월_세대수, X월_세대당인구, X월_남자, X월_여자, X월_남여비율, ...
        # 마지막 6개 컬럼
        sep_idx = len(header) - 6
    
    print(f"📊 사용할 데이터 인덱스: {sep_idx}")
    print(f"   컬럼: {header[sep_idx:sep_idx+6]}")
    
    for row in reader:
        region_name = row[0]
        
        # 행정동 코드 추출 (괄호 안)
        if '(' not in region_name:
            continue
        
        parts = region_name.split('(')
        full_name = parts[0].strip()
        code_part = parts[1].replace(')', '').strip()
        
        # 동 단위만 처리
        if not code_part or len(code_part) < 10:
            continue
        
        try:
            # 데이터 파싱
            total_pop = int(row[sep_idx].replace(',', '').strip()) if sep_idx < len(row) and row[sep_idx].strip() else 0
            household = int(row[sep_idx + 1].replace(',', '').strip()) if sep_idx + 1 < len(row) and row[sep_idx + 1].strip() else 0
            avg_size = float(row[sep_idx + 2].replace(',', '').strip()) if sep_idx + 2 < len(row) and row[sep_idx + 2].strip() else 0
            male = int(row[sep_idx + 3].replace(',', '').strip()) if sep_idx + 3 < len(row) and row[sep_idx + 3].strip() else 0
            female = int(row[sep_idx + 4].replace(',', '').strip()) if sep_idx + 4 < len(row) and row[sep_idx + 4].strip() else 0
            
            jumin_data[code_part] = {
                'code': code_part,
                'full_name': full_name,
                'total_population': total_pop,
                'household_cnt': household,
                'avg_household_size': avg_size,
                'male_population': male,
                'female_population': female,
                'year_month': '2025-09'
            }
            
        except (ValueError, IndexError) as e:
            continue

print(f"\n✅ 총 {len(jumin_data)}개 행정동 데이터 변환 완료")

# 샘플 출력
for code, data in list(jumin_data.items())[:3]:
    print(f"\n{data['full_name']} ({code}):")
    print(f"  인구: {data['total_population']:,}명")
    print(f"  세대: {data['household_cnt']:,}가구")

# 저장
output_file = 'insightforge-web/data/jumin_population_2025.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'source': '행정안전부 주민등록 인구통계',
            'year_month': '2025-09',
            'total_regions': len(jumin_data)
        },
        'regions': jumin_data
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 저장 완료: {output_file}")

# 개포1동 확인
for code, data in jumin_data.items():
    if '개포1동' in data['full_name']:
        print(f"\n📍 개포1동 확인:")
        print(f"  코드: {code}")
        print(f"  이름: {data['full_name']}")
        print(f"  인구: {data['total_population']:,}명")
        print(f"  세대: {data['household_cnt']:,}가구")
        break

