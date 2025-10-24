#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주민등록 코드 <-> SGIS 코드 매핑 생성
"""
import json

# 주민등록 데이터
with open('insightforge-web/data/jumin_population_2025.json', 'r') as f:
    jumin = json.load(f)

# SGIS 데이터
with open('insightforge-web/data/sgis_comprehensive_stats.json', 'r') as f:
    sgis = json.load(f)

# 이름으로 매핑
mapping = {}
jumin_by_name = {}

# 주민등록 데이터를 이름으로 인덱싱
for code, data in jumin['regions'].items():
    name = data['full_name']
    # "서울특별시 강남구 개포1동" 형식
    jumin_by_name[name] = {
        'jumin_code': code,
        **data
    }

# SGIS 데이터와 매칭
matched = 0
unmatched_sgis = []
unmatched_jumin = []

for sgis_code, sgis_data in sgis['regions'].items():
    # SGIS full_address 생성
    sgis_address = sgis_data.get('full_address', '')
    
    if sgis_address in jumin_by_name:
        mapping[sgis_code] = {
            'sgis_code': sgis_code,
            'jumin_code': jumin_by_name[sgis_address]['jumin_code'],
            'full_address': sgis_address
        }
        matched += 1
    else:
        unmatched_sgis.append(f"{sgis_code}: {sgis_address}")

print(f"✅ 매칭 성공: {matched}개")
print(f"⚠️  매칭 실패 (SGIS): {len(unmatched_sgis)}개")

# 샘플 출력
print("\n📋 매칭 샘플:")
for sgis_code, info in list(mapping.items())[:5]:
    print(f"  SGIS: {sgis_code} ↔ 주민등록: {info['jumin_code']}")
    print(f"    {info['full_address']}")

# 저장
output_file = 'insightforge-web/data/code_mapping.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'total_matched': matched,
            'sgis_codes': len(sgis['regions']),
            'jumin_codes': len(jumin['regions'])
        },
        'mapping': mapping
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 저장 완료: {output_file}")

# 개포1동 확인
if '11230680' in mapping:
    print(f"\n📍 개포1동 매핑 확인:")
    print(f"  SGIS: 11230680")
    print(f"  주민등록: {mapping['11230680']['jumin_code']}")

