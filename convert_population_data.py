#!/usr/bin/env python3
"""
주민등록 인구 데이터 변환 (2008-2025년 9월)
human/ 폴더의 월간 데이터를 연간 데이터로 집계
"""

import pandas as pd
import json
import glob
from pathlib import Path
import os
import re

# 결과 저장용
population_by_year = {}
population_change_by_year = {}

print("📊 주민등록 인구 데이터 변환 시작 (2008-2025년 9월)\n")

# 1. 인구 및 세대 현황 데이터 (human/)
human_files = sorted([f for f in os.listdir('human') if f.endswith('.csv')])
print(f"📁 인구 파일: {len(human_files)}개")

for filename in human_files:
    file_path = os.path.join('human', filename)
    
    # 연도 추출 (예: 201501_201512)
    year_match = re.search(r'(\d{4})\d{2}_', filename)
    if not year_match:
        continue
    
    year = int(year_match.group(1))
    
    if year < 2008:
        continue
    
    print(f"   {year}년 처리 중...")
    
    try:
        # CSV 읽기
        df = pd.read_csv(file_path, encoding='cp949')
        df.columns = df.columns.str.strip()
        
        # 행정구역 열 확인
        if '행정구역' not in df.columns:
            print(f"      ⚠️  행정구역 열 없음")
            continue
        
        # 해당 연도의 모든 월 데이터 추출
        year_cols = [col for col in df.columns if col.startswith(f'{year}년')]
        
        if len(year_cols) == 0:
            print(f"      ⚠️  {year}년 데이터 없음")
            continue
        
        # 총인구수, 세대수 컬럼 찾기
        pop_cols = [col for col in year_cols if '총인구수' in col]
        household_cols = [col for col in year_cols if '세대수' in col]
        male_cols = [col for col in year_cols if '남자 인구수' in col or '남자인구수' in col]
        female_cols = [col for col in year_cols if '여자 인구수' in col or '여자인구수' in col]
        
        if year not in population_by_year:
            population_by_year[year] = {}
        
        # 각 행정구역별로 처리
        for idx, row in df.iterrows():
            region = str(row['행정구역']).strip()
            
            # 숫자에서 쉼표 제거하고 평균 계산
            def parse_and_avg(cols):
                values = []
                for col in cols:
                    val = str(row[col]).replace(',', '').strip()
                    try:
                        v = float(val)
                        if not pd.isna(v):
                            values.append(v)
                    except:
                        pass
                if values:
                    avg = sum(values) / len(values)
                    return int(avg) if not pd.isna(avg) else 0
                return 0
            
            total_pop = parse_and_avg(pop_cols)
            households = parse_and_avg(household_cols)
            male = parse_and_avg(male_cols) if male_cols else None
            female = parse_and_avg(female_cols) if female_cols else None
            
            if total_pop > 0:
                population_by_year[year][region] = {
                    'total_population': total_pop,
                    'households': households,
                    'male': male,
                    'female': female
                }
        
        region_count = len(population_by_year[year])
        print(f"      ✅ {region_count}개 행정구역")
        
    except Exception as e:
        print(f"      ❌ 에러: {e}")
        import traceback
        traceback.print_exc()

# 2. 인구 증감 데이터 (humanre/)
humanre_files = sorted([f for f in os.listdir('humanre') if f.endswith('.csv')])
print(f"\n📁 인구증감 파일: {len(humanre_files)}개")

for filename in humanre_files:
    file_path = os.path.join('humanre', filename)
    
    # 연도 추출
    year_match = re.search(r'(\d{4})\d{2}_', filename)
    if not year_match:
        continue
    
    year = int(year_match.group(1))
    
    if year < 2008:
        continue
    
    print(f"   {year}년 처리 중...")
    
    try:
        df = pd.read_csv(file_path, encoding='cp949')
        df.columns = df.columns.str.strip()
        
        if '행정구역' not in df.columns:
            print(f"      ⚠️  행정구역 열 없음")
            continue
        
        # 해당 연도의 모든 월 데이터 추출
        year_cols = [col for col in df.columns if col.startswith(f'{year}년')]
        
        if len(year_cols) == 0:
            print(f"      ⚠️  {year}년 데이터 없음")
            continue
        
        # 인구증감 관련 컬럼 찾기
        birth_cols = [col for col in year_cols if '출생' in col]
        death_cols = [col for col in year_cols if '사망' in col]
        movein_cols = [col for col in year_cols if '전입' in col]
        moveout_cols = [col for col in year_cols if '전출' in col]
        change_cols = [col for col in year_cols if '증감' in col]
        
        if year not in population_change_by_year:
            population_change_by_year[year] = {}
        
        # 각 행정구역별로 처리
        for idx, row in df.iterrows():
            region = str(row['행정구역']).strip()
            
            def parse_and_sum(cols):
                values = []
                for col in cols:
                    val = str(row[col]).replace(',', '').strip()
                    try:
                        v = float(val)
                        if not pd.isna(v):
                            values.append(v)
                    except:
                        pass
                if values:
                    total = sum(values)
                    return int(total) if not pd.isna(total) else 0
                return 0
            
            births = parse_and_sum(birth_cols) if birth_cols else None
            deaths = parse_and_sum(death_cols) if death_cols else None
            move_in = parse_and_sum(movein_cols) if movein_cols else None
            move_out = parse_and_sum(moveout_cols) if moveout_cols else None
            net_change = parse_and_sum(change_cols) if change_cols else None
            
            population_change_by_year[year][region] = {
                'births': births,
                'deaths': deaths,
                'move_in': move_in,
                'move_out': move_out,
                'net_change': net_change
            }
        
        region_count = len(population_change_by_year[year])
        print(f"      ✅ {region_count}개 행정구역")
        
    except Exception as e:
        print(f"      ❌ 에러: {e}")
        import traceback
        traceback.print_exc()

# 통합 데이터 생성
integrated_data = {}
all_years = sorted(set(list(population_by_year.keys()) + list(population_change_by_year.keys())))

print(f"\n📊 데이터 통합 중...")
for year in all_years:
    integrated_data[str(year)] = {
        'population': population_by_year.get(year, {}),
        'population_change': population_change_by_year.get(year, {})
    }
    
    pop_count = len(population_by_year.get(year, {}))
    change_count = len(population_change_by_year.get(year, {}))
    print(f"   {year}년: 인구 {pop_count}개 구역, 증감 {change_count}개 구역")

# 저장
output_file = 'insightforge-web/data/population_yearly_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(integrated_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 변환 완료!")
print(f"   연도: {all_years}")
print(f"   저장: {output_file}")
print(f"\n📈 통계:")
for year in all_years:
    pop_regions = len(integrated_data[str(year)]['population'])
    if pop_regions > 0:
        sample_region = list(integrated_data[str(year)]['population'].keys())[0]
        sample_data = integrated_data[str(year)]['population'][sample_region]
        print(f"   {year}년: {pop_regions}개 구역")
        print(f"      예시 ({sample_region}): 인구 {sample_data.get('total_population', 0):,}명")

