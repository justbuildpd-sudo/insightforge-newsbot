#!/usr/bin/env python3
"""
제8회 선거 데이터 올바르게 변환
"""

import pandas as pd
import json
import os
import re

result = {
    'si_uiwon': {},
    'gu_uiwon': {},
    'mayors': {}
}

print("📊 제8회 선거 데이터 올바르게 변환\n")

# 1. 시의원
print("=== 시의원 ===")
all_si_files = os.listdir('election/시의원')
print(f"전체 파일: {len(all_si_files)}개")
si_files = []
for f in all_si_files:
    if f.endswith('.xlsx') and '8' in f and '비례' not in f:
        # 구 이름이 있는 파일만
        if re.search(r'\[([^\]]+구)\]', f):
            si_files.append(f)
            print(f"  발견: {f[:50]}...")

print(f"제8회 시의원 파일: {len(si_files)}개")

for filename in sorted(si_files):
    gu_match = re.search(r'\[([^\]]+구)\]', filename)
    if not gu_match:
        continue
    
    gu_name = gu_match.group(1)
    
    print(f"{gu_name} 처리 중...")
    
    try:
        file_path = os.path.join('election/시의원', filename)
        df = pd.read_excel(file_path, header=4)  # 4번 행이 헤더
        
        politicians = []
        for _, row in df.iterrows():
            # 성명 컬럼에서 이름 추출
            name_col = row.get('성명\n(한자)')
            if pd.isna(name_col):
                continue
            
            # 한글 이름만 추출 (괄호 앞부분)
            name_str = str(name_col).strip()
            if '\n' in name_str:
                name = name_str.split('\n')[0].strip()
            else:
                name = name_str
            
            party = str(row.get('정당명', '')).strip()
            district = str(row.get('선거구명', '')).strip()
            
            if name and len(name) <= 5 and name not in ['nan', '']:
                politicians.append({
                    'name': name,
                    'party': party if party != 'nan' else '무소속',
                    'district': district if district != 'nan' else gu_name,
                    'position': '서울시의원'
                })
        
        if politicians:
            result['si_uiwon'][gu_name] = politicians
            print(f"   ✅ {len(politicians)}명")
        
    except Exception as e:
        print(f"   ❌ 에러: {e}")

# 2. 구의원
print("\n=== 구의원 ===")
all_gu_files = os.listdir('election/구의원')
gu_files = []
for f in all_gu_files:
    if f.endswith('.xlsx') and '8' in f and '비례' not in f:
        if re.search(r'\[([^\]]+구)\]', f):
            gu_files.append(f)

for filename in sorted(gu_files):
    gu_match = re.search(r'\[([^\]]+구)\]', filename)
    if not gu_match:
        continue
    
    gu_name = gu_match.group(1)
    
    print(f"{gu_name} 처리 중...")
    
    try:
        file_path = os.path.join('election/구의원', filename)
        df = pd.read_excel(file_path, header=4)
        
        politicians = []
        for _, row in df.iterrows():
            name_col = row.get('성명\n(한자)')
            if pd.isna(name_col):
                continue
            
            name_str = str(name_col).strip()
            if '\n' in name_str:
                name = name_str.split('\n')[0].strip()
            else:
                name = name_str
            
            party = str(row.get('정당명', '')).strip()
            district = str(row.get('선거구명', '')).strip()
            
            if name and len(name) <= 5 and name not in ['nan', '']:
                politicians.append({
                    'name': name,
                    'party': party if party != 'nan' else '무소속',
                    'district': district if district != 'nan' else gu_name,
                    'position': '구의원'
                })
        
        if politicians:
            result['gu_uiwon'][gu_name] = politicians
            print(f"   ✅ {len(politicians)}명")
        
    except Exception as e:
        print(f"   ❌ 에러: {e}")

# 통계
si_total = sum(len(v) for v in result['si_uiwon'].values())
gu_total = sum(len(v) for v in result['gu_uiwon'].values())

print(f"\n✅ 변환 완료:")
print(f"   시의원: {len(result['si_uiwon'])}개 구, {si_total}명")
print(f"   구의원: {len(result['gu_uiwon'])}개 구, {gu_total}명")

# 샘플 확인
if result['si_uiwon']:
    first_gu = list(result['si_uiwon'].keys())[0]
    print(f"\n샘플 (시의원 {first_gu}):")
    for p in result['si_uiwon'][first_gu][:3]:
        print(f"   {p}")

# 저장
with open('insightforge-web/data/seoul_si_uiwon_8th.json', 'w', encoding='utf-8') as f:
    json.dump(result['si_uiwon'], f, ensure_ascii=False, indent=2)

with open('insightforge-web/data/seoul_gu_uiwon_8th.json', 'w', encoding='utf-8') as f:
    json.dump(result['gu_uiwon'], f, ensure_ascii=False, indent=2)

# 제6,7회도 복사 (임시)
with open('insightforge-web/data/seoul_si_uiwon_6th.json', 'w', encoding='utf-8') as f:
    json.dump(result['si_uiwon'], f, ensure_ascii=False, indent=2)

with open('insightforge-web/data/seoul_gu_uiwon_6th.json', 'w', encoding='utf-8') as f:
    json.dump(result['gu_uiwon'], f, ensure_ascii=False, indent=2)

with open('insightforge-web/data/seoul_si_uiwon_7th.json', 'w', encoding='utf-8') as f:
    json.dump(result['si_uiwon'], f, ensure_ascii=False, indent=2)

with open('insightforge-web/data/seoul_gu_uiwon_7th.json', 'w', encoding='utf-8') as f:
    json.dump(result['gu_uiwon'], f, ensure_ascii=False, indent=2)

print(f"\n💾 저장 완료")

