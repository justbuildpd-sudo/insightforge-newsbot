#!/usr/bin/env python3
"""
제7회 지방선거 데이터 변환 (2018년)
"""

import pandas as pd
import json
from pathlib import Path
import glob

# 시의원 데이터
si_uiwon_7th = {}
import os
si_all_files = os.listdir('election/시의원/')
si_files = ['election/시의원/' + f for f in si_all_files if '7' in f and '비례' not in f and '.xlsx' in f]

print(f'📁 제7회 시의원 파일: {len(si_files)}개\n')

for file_path in sorted(si_files):
    if '비례' in file_path:
        continue
        
    print(f'📂 읽는 중: {Path(file_path).name[:50]}...')
    
    try:
        df = pd.read_excel(file_path)
        
        # 구 이름 추출
        gu_name = None
        for part in Path(file_path).name.split('['):
            if '구]' in part:
                gu_name = part.replace(']', '').strip()
                break
        
        if not gu_name:
            continue
        
        if gu_name not in si_uiwon_7th:
            si_uiwon_7th[gu_name] = []
        
        # 데이터 파싱
        for _, row in df.iterrows():
            name = str(row.get('성명') or row.get('이름') or '').strip()
            party = str(row.get('정당') or row.get('정당명') or '').strip()
            district = str(row.get('선거구') or row.get('선거구명') or '').strip()
            
            if name and name != 'nan':
                si_uiwon_7th[gu_name].append({
                    'name': name,
                    'party': party,
                    'district': f'{gu_name}{district}' if district and district != 'nan' else gu_name,
                    'position': '서울시의원'
                })
        
        print(f'   ✅ {gu_name}: {len(si_uiwon_7th[gu_name])}명\n')
        
    except Exception as e:
        print(f'   ❌ 에러: {e}\n')

# 구의원 데이터
gu_uiwon_7th = {}
gu_all_files = os.listdir('election/구의원/')
gu_files = ['election/구의원/' + f for f in gu_all_files if '7' in f and '비례' not in f and '.xlsx' in f]

print(f'\n📁 제7회 구의원 파일: {len(gu_files)}개\n')

for file_path in sorted(gu_files):
    if '비례' in file_path:
        continue
        
    print(f'📂 읽는 중: {Path(file_path).name[:50]}...')
    
    try:
        df = pd.read_excel(file_path)
        
        # 구 이름 추출
        gu_name = None
        for part in Path(file_path).name.split('['):
            if '구]' in part:
                gu_name = part.replace(']', '').strip()
                break
        
        if not gu_name:
            continue
        
        if gu_name not in gu_uiwon_7th:
            gu_uiwon_7th[gu_name] = []
        
        # 데이터 파싱
        for _, row in df.iterrows():
            name = str(row.get('성명') or row.get('이름') or '').strip()
            party = str(row.get('정당') or row.get('정당명') or '').strip()
            district = str(row.get('선거구') or row.get('선거구명') or '').strip()
            
            if name and name != 'nan':
                gu_uiwon_7th[gu_name].append({
                    'name': name,
                    'party': party,
                    'district': f'{gu_name}{district}' if district and district != 'nan' else gu_name,
                    'position': '구의원'
                })
        
        print(f'   ✅ {gu_name}: {len(gu_uiwon_7th[gu_name])}명\n')
        
    except Exception as e:
        print(f'   ❌ 에러: {e}\n')

# 통계
total_si = sum(len(v) for v in si_uiwon_7th.values())
total_gu = sum(len(v) for v in gu_uiwon_7th.values())

print(f'\n✅ 변환 완료:')
print(f'   시의원: {len(si_uiwon_7th)}개 구, {total_si}명')
print(f'   구의원: {len(gu_uiwon_7th)}개 구, {total_gu}명')

# 저장
with open('insightforge-web/data/seoul_si_uiwon_7th.json', 'w', encoding='utf-8') as f:
    json.dump(si_uiwon_7th, f, ensure_ascii=False, indent=2)

with open('insightforge-web/data/seoul_gu_uiwon_7th.json', 'w', encoding='utf-8') as f:
    json.dump(gu_uiwon_7th, f, ensure_ascii=False, indent=2)

print(f'\n💾 저장 완료')
print(f'   insightforge-web/data/seoul_si_uiwon_7th.json')
print(f'   insightforge-web/data/seoul_gu_uiwon_7th.json')

