#!/usr/bin/env python3
"""
과거 정치인 목록 생성 (2008-2025)
- 국회의원 (16대-22대)
- 광역단체장 (시도지사)
- 기초단체장 (시장/군수/구청장)
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR.parent / 'insightforge-web' / 'data'
OUTPUT_FILE = BASE_DIR / 'data' / 'historical_politicians.json'

def load_assembly_members():
    """국회의원 전체 (역대)"""
    file_path = DATA_DIR / 'national_assembly_members_latest.json'
    
    if not file_path.exists():
        print("❌ 국회의원 데이터 없음")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        all_members = json.load(f)
    
    politicians = []
    
    for name, data in all_members.items():
        member_info = data.get('member_info', {})
        term = member_info.get('term', '')
        
        # 16대-22대 필터링
        if any(f'제{i}대' in str(term) for i in range(16, 23)):
            # 기간 추정
            term_periods = {
                '16': ('2000-05-30', '2004-05-29'),
                '17': ('2004-05-30', '2008-05-29'),
                '18': ('2008-05-30', '2012-05-29'),
                '19': ('2012-05-30', '2016-05-29'),
                '20': ('2016-05-30', '2020-05-29'),
                '21': ('2020-05-30', '2024-05-29'),
                '22': ('2024-05-30', '2028-05-29'),
            }
            
            # 해당하는 모든 기수 추출
            for term_num in range(16, 23):
                if f'제{term_num}대' in str(term):
                    start_date, end_date = term_periods[str(term_num)]
                    
                    politicians.append({
                        'name': name,
                        'party': member_info.get('party', ''),
                        'district': member_info.get('district', ''),
                        'position': '국회의원',
                        'type': '국회의원',
                        'level': 'national',
                        'term': f'제{term_num}대',
                        'start_date': start_date,
                        'end_date': end_date,
                        'priority': 1  # 국회의원 우선순위 높음
                    })
    
    print(f"✅ 국회의원: {len(politicians)}명")
    return politicians

def load_local_politicians():
    """지방정치인 (현직)"""
    file_path = BASE_DIR / 'data' / 'politicians.json'
    
    if not file_path.exists():
        print("❌ 지방정치인 데이터 없음")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        current_local = json.load(f)
    
    politicians = []
    
    for pol in current_local:
        # 8회 지방선거 (2022-2026)
        politicians.append({
            'name': pol['name'],
            'party': pol.get('party', ''),
            'district': pol.get('district', ''),
            'position': pol.get('position', ''),
            'type': pol.get('type', ''),
            'level': pol.get('level', 'local'),
            'term': '8회',
            'start_date': '2022-07-01',
            'end_date': '2026-06-30',
            'priority': 2
        })
        
        # 7회 지방선거 (2018-2022) - 같은 사람으로 가정
        politicians.append({
            'name': pol['name'],
            'party': pol.get('party', ''),
            'district': pol.get('district', ''),
            'position': pol.get('position', ''),
            'type': pol.get('type', ''),
            'level': pol.get('level', 'local'),
            'term': '7회',
            'start_date': '2018-07-01',
            'end_date': '2022-06-30',
            'priority': 3
        })
        
        # 6회 지방선거 (2014-2018)
        politicians.append({
            'name': pol['name'],
            'party': pol.get('party', ''),
            'district': pol.get('district', ''),
            'position': pol.get('position', ''),
            'type': pol.get('type', ''),
            'level': pol.get('level', 'local'),
            'term': '6회',
            'start_date': '2014-07-01',
            'end_date': '2018-06-30',
            'priority': 4
        })
        
        # 5회 지방선거 (2010-2014)
        politicians.append({
            'name': pol['name'],
            'party': pol.get('party', ''),
            'district': pol.get('district', ''),
            'position': pol.get('position', ''),
            'type': pol.get('type', ''),
            'level': pol.get('level', 'local'),
            'term': '5회',
            'start_date': '2010-07-01',
            'end_date': '2014-06-30',
            'priority': 5
        })
    
    print(f"✅ 지방정치인: {len(politicians)}명")
    return politicians

def add_mayors_and_governors():
    """시도지사, 시장/군수 추가 (주요 인물만)"""
    # 서울시장
    seoul_mayors = [
        {'name': '오세훈', 'period': ('2022-01-01', '2025-10-20'), 'term': '8회'},
        {'name': '박원순', 'period': ('2011-10-27', '2020-07-09'), 'term': '5-7회'},
        {'name': '오세훈', 'period': ('2006-07-01', '2011-08-26'), 'term': '3-4회'},
    ]
    
    # 구청장 (서울 25개 자치구 - 대표만)
    district_heads = [
        # 강남구
        {'name': '조성명', 'district': '강남구', 'period': ('2022-07-01', '2026-06-30'), 'term': '8회'},
        {'name': '정순균', 'district': '강남구', 'period': ('2018-07-01', '2022-06-30'), 'term': '7회'},
        {'name': '신연희', 'district': '강남구', 'period': ('2014-07-01', '2018-06-30'), 'term': '6회'},
        
        # 서초구
        {'name': '전성수', 'district': '서초구', 'period': ('2022-07-01', '2026-06-30'), 'term': '8회'},
        {'name': '조은희', 'district': '서초구', 'period': ('2014-07-01', '2022-06-30'), 'term': '6-7회'},
        
        # 송파구
        {'name': '서강석', 'district': '송파구', 'period': ('2022-07-01', '2026-06-30'), 'term': '8회'},
        {'name': '박성수', 'district': '송파구', 'period': ('2018-07-01', '2022-06-30'), 'term': '7회'},
        
        # 종로구
        {'name': '정문헌', 'district': '종로구', 'period': ('2022-07-01', '2026-06-30'), 'term': '8회'},
        {'name': '김영종', 'district': '종로구', 'period': ('2010-07-01', '2022-06-30'), 'term': '5-7회'},
    ]
    
    politicians = []
    
    # 서울시장
    for mayor in seoul_mayors:
        start, end = mayor['period']
        politicians.append({
            'name': mayor['name'],
            'party': '',
            'district': '서울',
            'position': '서울특별시장',
            'type': '시장',
            'level': 'mayor',
            'term': mayor['term'],
            'start_date': start,
            'end_date': end,
            'priority': 1  # 시장 우선순위 높음
        })
    
    # 구청장
    for head in district_heads:
        start, end = head['period']
        politicians.append({
            'name': head['name'],
            'party': '',
            'district': head['district'],
            'position': f"{head['district']}청장",
            'type': '구청장',
            'level': 'district_head',
            'term': head['term'],
            'start_date': start,
            'end_date': end,
            'priority': 2
        })
    
    print(f"✅ 단체장: {len(politicians)}명")
    return politicians

def main():
    """메인 실행"""
    print("=== 역사적 정치인 목록 생성 ===\n")
    
    all_politicians = []
    
    # 1. 국회의원
    assembly = load_assembly_members()
    all_politicians.extend(assembly)
    
    # 2. 지방정치인
    local = load_local_politicians()
    all_politicians.extend(local)
    
    # 3. 시장/구청장
    mayors = add_mayors_and_governors()
    all_politicians.extend(mayors)
    
    print(f"\n총 정치인: {len(all_politicians)}명")
    
    # 우선순위별 통계
    by_priority = {}
    for pol in all_politicians:
        priority = pol.get('priority', 99)
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    print("\n우선순위별:")
    for priority in sorted(by_priority.keys()):
        print(f"  Priority {priority}: {by_priority[priority]}명")
    
    # 유형별 통계
    by_type = {}
    for pol in all_politicians:
        ptype = pol.get('type', '기타')
        by_type[ptype] = by_type.get(ptype, 0) + 1
    
    print("\n유형별:")
    for ptype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ptype}: {count}명")
    
    # 저장
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_politicians, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 저장: {OUTPUT_FILE}")
    print(f"📊 총 {len(all_politicians)}명")
    
    # Phase별 분할
    phases = {
        'phase1': {'start': '2020-01-01', 'end': '2025-10-20', 'priority': [1, 2]},
        'phase2': {'start': '2016-01-01', 'end': '2019-12-31', 'priority': [1, 3]},
        'phase3': {'start': '2012-01-01', 'end': '2015-12-31', 'priority': [1, 4]},
        'phase4': {'start': '2008-01-01', 'end': '2011-12-31', 'priority': [1, 5]},
    }
    
    for phase_name, config in phases.items():
        phase_politicians = [
            p for p in all_politicians
            if p.get('priority', 99) in config['priority']
            and p.get('start_date', '') <= config['end']
            and p.get('end_date', '') >= config['start']
        ]
        
        phase_file = OUTPUT_FILE.parent / f'{phase_name}_politicians.json'
        with open(phase_file, 'w', encoding='utf-8') as f:
            json.dump(phase_politicians, f, ensure_ascii=False, indent=2)
        
        print(f"\n{phase_name.upper()}: {len(phase_politicians)}명 → {phase_file.name}")
        print(f"  기간: {config['start']} ~ {config['end']}")
        print(f"  우선순위: {config['priority']}")

if __name__ == '__main__':
    main()

