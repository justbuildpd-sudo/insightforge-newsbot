#!/usr/bin/env python3
"""
모든 선거 데이터 변환
- 지방선거: 제5회(2010-2014), 제6회(2014-2018), 제7회(2018-2022), 제8회(2022-2026)
- 국회의원: 제16대(2000-2004), 제17대(2004-2008), 제18대(2008-2012), 
           제19대(2012-2016), 제20대(2016-2020), 제21대(2020-2024), 제22대(2024-2028)
"""

import pandas as pd
import json
import os
import re

# 선거 임기 정보
LOCAL_ELECTIONS = {
    '5': {'start': '2010-07-01', 'end': '2014-06-30'},
    '6': {'start': '2014-07-01', 'end': '2018-06-30'},
    '7': {'start': '2018-07-01', 'end': '2022-06-30'},
    '8': {'start': '2022-07-01', 'end': '2026-06-30'}
}

NATIONAL_ELECTIONS = {
    '16': {'start': '2000-05-30', 'end': '2004-05-29'},
    '17': {'start': '2004-05-30', 'end': '2008-05-29'},
    '18': {'start': '2008-05-30', 'end': '2012-05-29'},
    '19': {'start': '2012-05-30', 'end': '2016-05-29'},
    '20': {'start': '2016-05-30', 'end': '2020-05-29'},
    '21': {'start': '2020-05-30', 'end': '2024-05-29'},
    '22': {'start': '2024-05-30', 'end': '2028-05-29'}
}

result = {
    'local_elections': {},  # 회차별 지방선거
    'national_elections': {}  # 대수별 국회의원
}

print("📊 선거 데이터 변환 시작\n")

# 1. 지방선거 - 시의원
print("=== 지방선거 시의원 ===")
si_files = [f for f in os.listdir('election/시의원') if f.endswith('.xlsx') and '비례' not in f]

for filename in sorted(si_files):
    # 회차 추출
    match = re.search(r'제(\d+)회', filename)
    if not match:
        continue
    
    round_num = match.group(1)
    if round_num not in LOCAL_ELECTIONS:
        continue
    
    # 구 이름 추출
    gu_match = re.search(r'\[([^\]]+구)\]', filename)
    if not gu_match:
        continue
    
    gu_name = gu_match.group(1)
    
    print(f"제{round_num}회 {gu_name} 처리 중...")
    
    try:
        file_path = os.path.join('election/시의원', filename)
        df = pd.read_excel(file_path)
        
        # 데이터 파싱
        politicians = []
        for idx, row in df.iterrows():
            # 첫 몇 행은 헤더일 수 있으므로 스킵
            if idx < 5:
                continue
            
            # 성명, 정당, 선거구 찾기
            row_str = ' '.join([str(v) for v in row.values if pd.notna(v)])
            if not row_str or len(row_str.strip()) < 3:
                continue
            
            # 간단한 파싱 (실제 데이터 구조에 맞게 조정 필요)
            values = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip()]
            if len(values) >= 2:
                politicians.append({
                    'name': values[0] if len(values[0]) <= 5 else None,
                    'party': values[1] if len(values) > 1 else None,
                    'district': gu_name,
                    'position': '시의원'
                })
        
        # 유효한 데이터만 저장
        valid_politicians = [p for p in politicians if p['name'] and len(p['name']) <= 5]
        
        if valid_politicians:
            if round_num not in result['local_elections']:
                result['local_elections'][round_num] = {
                    'term': LOCAL_ELECTIONS[round_num],
                    'si_uiwon': {},
                    'gu_uiwon': {},
                    'mayors': {}
                }
            
            result['local_elections'][round_num]['si_uiwon'][gu_name] = valid_politicians
            print(f"   ✅ {len(valid_politicians)}명")
        
    except Exception as e:
        print(f"   ❌ 에러: {e}")

# 2. 지방선거 - 구의원
print("\n=== 지방선거 구의원 ===")
gu_files = [f for f in os.listdir('election/구의원') if f.endswith('.xlsx') and '비례' not in f]

for filename in sorted(gu_files):
    match = re.search(r'제(\d+)회', filename)
    if not match:
        continue
    
    round_num = match.group(1)
    if round_num not in LOCAL_ELECTIONS:
        continue
    
    gu_match = re.search(r'\[([^\]]+구)\]', filename)
    if not gu_match:
        continue
    
    gu_name = gu_match.group(1)
    
    print(f"제{round_num}회 {gu_name} 처리 중...")
    
    try:
        file_path = os.path.join('election/구의원', filename)
        df = pd.read_excel(file_path)
        
        politicians = []
        for idx, row in df.iterrows():
            if idx < 5:
                continue
            
            row_str = ' '.join([str(v) for v in row.values if pd.notna(v)])
            if not row_str or len(row_str.strip()) < 3:
                continue
            
            values = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip()]
            if len(values) >= 2:
                politicians.append({
                    'name': values[0] if len(values[0]) <= 5 else None,
                    'party': values[1] if len(values) > 1 else None,
                    'district': gu_name,
                    'position': '구의원'
                })
        
        valid_politicians = [p for p in politicians if p['name'] and len(p['name']) <= 5]
        
        if valid_politicians:
            if round_num not in result['local_elections']:
                result['local_elections'][round_num] = {
                    'term': LOCAL_ELECTIONS[round_num],
                    'si_uiwon': {},
                    'gu_uiwon': {},
                    'mayors': {}
                }
            
            result['local_elections'][round_num]['gu_uiwon'][gu_name] = valid_politicians
            print(f"   ✅ {len(valid_politicians)}명")
        
    except Exception as e:
        print(f"   ❌ 에러: {e}")

# 3. 국회의원 선거
print("\n=== 국회의원 선거 ===")
na_files = [f for f in os.listdir('election/국회의원') if f.endswith('.xlsx')]

for filename in sorted(na_files):
    match = re.search(r'제(\d+)대', filename)
    if not match:
        continue
    
    term_num = match.group(1)
    if term_num not in NATIONAL_ELECTIONS:
        continue
    
    print(f"제{term_num}대 처리 중...")
    
    try:
        file_path = os.path.join('election/국회의원', filename)
        df = pd.read_excel(file_path)
        
        politicians = []
        for idx, row in df.iterrows():
            if idx < 5:
                continue
            
            row_str = ' '.join([str(v) for v in row.values if pd.notna(v)])
            if not row_str or len(row_str.strip()) < 3:
                continue
            
            values = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip()]
            if len(values) >= 3:
                politicians.append({
                    'name': values[0] if len(values[0]) <= 5 else None,
                    'party': values[1] if len(values) > 1 else None,
                    'district': values[2] if len(values) > 2 else '서울',
                    'position': '국회의원'
                })
        
        valid_politicians = [p for p in politicians if p['name'] and len(p['name']) <= 5]
        
        if valid_politicians:
            result['national_elections'][term_num] = {
                'term': NATIONAL_ELECTIONS[term_num],
                'politicians': valid_politicians
            }
            print(f"   ✅ {len(valid_politicians)}명")
        
    except Exception as e:
        print(f"   ❌ 에러: {e}")

# 통계
print("\n📊 변환 완료!")
print(f"\n지방선거:")
for round_num in sorted(result['local_elections'].keys()):
    data = result['local_elections'][round_num]
    si_count = sum(len(v) for v in data['si_uiwon'].values())
    gu_count = sum(len(v) for v in data['gu_uiwon'].values())
    term = data['term']
    print(f"  제{round_num}회 ({term['start']} ~ {term['end']})")
    print(f"    시의원: {si_count}명, 구의원: {gu_count}명")

print(f"\n국회의원:")
for term_num in sorted(result['national_elections'].keys()):
    data = result['national_elections'][term_num]
    count = len(data['politicians'])
    term = data['term']
    print(f"  제{term_num}대 ({term['start']} ~ {term['end']}): {count}명")

# 저장
output_file = 'insightforge-web/data/all_elections_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n💾 저장: {output_file}")

