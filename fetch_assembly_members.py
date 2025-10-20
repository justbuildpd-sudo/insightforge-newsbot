#!/usr/bin/env python3
"""
국회 OpenAPI를 통해 현직 국회의원 정보 수집
"""

import requests
import json
from datetime import datetime
import time

# API 설정
API_KEY = 'f9725b9012a14a0ab286770ce5de5e71'
BASE_URL = 'https://open.assembly.go.kr/portal/openapi/ALLNAMEMBER'

def fetch_all_members():
    """모든 국회의원 정보 수집"""
    print("=== 국회의원 정보 수집 시작 ===\n")
    
    all_members = []
    page = 1
    page_size = 100
    
    while True:
        print(f"📄 페이지 {page} 요청 중...")
        
        params = {
            'KEY': API_KEY,
            'Type': 'json',
            'pIndex': page,
            'pSize': page_size
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 데이터 구조 확인
            if 'ALLNAMEMBER' not in data or not data['ALLNAMEMBER']:
                print(f"  ⚠️  데이터 없음")
                break
            
            members_data = data['ALLNAMEMBER'][1]
            
            if 'row' not in members_data:
                print(f"  ⚠️  row 데이터 없음")
                break
            
            members = members_data['row']
            
            if not members:
                print(f"  ✅ 마지막 페이지 도달")
                break
            
            all_members.extend(members)
            print(f"  ✅ {len(members)}명 수집 (누적: {len(all_members)}명)")
            
            # 다음 페이지가 없으면 종료
            if len(members) < page_size:
                print(f"  ✅ 모든 데이터 수집 완료")
                break
            
            page += 1
            time.sleep(0.5)  # API 부하 방지
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ API 요청 실패: {e}")
            break
        except (KeyError, IndexError) as e:
            print(f"  ❌ 데이터 파싱 실패: {e}")
            break
    
    return all_members

def process_members(members):
    """국회의원 데이터 처리 및 정제"""
    print(f"\n=== 데이터 처리 중 ===")
    
    processed = {}
    
    for member in members:
        name = member.get('NAAS_NM', '').strip()
        
        if not name:
            continue
        
        # 데이터 정제
        processed_member = {
            'member_info': {
                'code': member.get('NAAS_CD', ''),
                'name': name,
                'name_hanja': member.get('NAAS_CH_NM', ''),
                'name_en': member.get('NAAS_EN_NM', ''),
                'party': member.get('PLPT_NM', ''),
                'district': member.get('ELECD_NM', ''),
                'district_type': member.get('ELECD_DIV_NM', ''),
                'position': member.get('DTY_NM', ''),
                'committee': member.get('CMIT_NM', ''),
                'affiliated_committee': member.get('BLNG_CMIT_NM', ''),
                'reelection': member.get('RLCT_DIV_NM', ''),
                'term': member.get('GTELT_ERACO', ''),
                'gender': member.get('NTR_DIV', ''),
                'birthday': member.get('BIRDY_DT', ''),
                'birthday_type': member.get('BIRDY_DIV_CD', '')
            },
            'contact': {
                'tel': member.get('NAAS_TEL_NO', ''),
                'email': member.get('NAAS_EMAIL_ADDR', ''),
                'homepage': member.get('NAAS_HP_URL', ''),
                'office': member.get('OFFM_RNUM_NO', '')
            },
            'staff': {
                'aide': member.get('AIDE_NM', ''),
                'chief_secretary': member.get('CHF_SCRT_NM', ''),
                'secretary': member.get('SCRT_NM', '')
            },
            'profile': {
                'brief_history': member.get('BRF_HST', ''),
                'photo_url': member.get('NAAS_PIC', '')
            },
            'last_updated': datetime.now().isoformat(),
            'data_source': 'National Assembly OpenAPI'
        }
        
        processed[name] = processed_member
    
    print(f"✅ {len(processed)}명 처리 완료\n")
    return processed

def save_data(data, filename):
    """데이터 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 저장: {filename}")

def main():
    """메인 실행"""
    # 1. 데이터 수집
    members = fetch_all_members()
    
    if not members:
        print("❌ 수집된 데이터가 없습니다.")
        return
    
    print(f"\n📊 총 수집: {len(members)}명")
    
    # 2. 데이터 처리
    processed = process_members(members)
    
    # 3. 저장
    output_file = 'national_assembly_members_latest.json'
    save_data(processed, output_file)
    
    # 4. InsightForge로 복사
    insightforge_file = 'insightforge-web/data/national_assembly_members_latest.json'
    save_data(processed, insightforge_file)
    
    # 5. 통계
    print("\n=== 통계 ===")
    
    # 정당별 통계
    parties = {}
    for member in processed.values():
        party = member['member_info']['party']
        parties[party] = parties.get(party, 0) + 1
    
    print("\n📊 정당별 의원 수:")
    for party, count in sorted(parties.items(), key=lambda x: x[1], reverse=True):
        print(f"  {party}: {count}명")
    
    # 성별 통계
    gender_count = {}
    for member in processed.values():
        gender = member['member_info']['gender']
        gender_count[gender] = gender_count.get(gender, 0) + 1
    
    print("\n📊 성별 통계:")
    for gender, count in gender_count.items():
        print(f"  {gender}: {count}명")
    
    # 선거구 유형
    district_types = {}
    for member in processed.values():
        dtype = member['member_info']['district_type']
        district_types[dtype] = district_types.get(dtype, 0) + 1
    
    print("\n📊 선거구 유형:")
    for dtype, count in sorted(district_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dtype}: {count}명")
    
    print("\n✅ 모든 작업 완료!")
    print(f"📁 출력 파일:")
    print(f"  - {output_file}")
    print(f"  - {insightforge_file}")

if __name__ == '__main__':
    main()

