#!/usr/bin/env python3
"""
정치인 데이터에서 한자 제거 및 클린업
"""

import json
import re
import os
from pathlib import Path

DATA_DIR = Path('/Users/hopidad/Desktop/workspace/insightforge-web/data')

def clean_name(name):
    """이름에서 한자 및 불필요한 정보 제거"""
    if not name:
        return name
    
    # "정문헌 (鄭文憲)" -> "정문헌"
    # "정문헌\n(鄭文憲)" -> "정문헌"
    if '(' in name:
        name = name.split('(')[0]
    
    # 줄바꿈 제거
    name = name.split('\n')[0]
    
    # 공백 제거
    name = name.strip()
    
    return name

def clean_politician_data(data):
    """정치인 데이터 클린업"""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # 키가 이름인 경우 클린
            clean_key = clean_name(key)
            
            # 값 클린업
            if isinstance(value, dict):
                cleaned_value = clean_politician_data(value)
                # name 필드가 있으면 클린
                if 'name' in cleaned_value:
                    cleaned_value['name'] = clean_name(cleaned_value['name'])
            elif isinstance(value, list):
                cleaned_value = [clean_politician_data(item) for item in value]
            else:
                cleaned_value = value
            
            cleaned[clean_key] = cleaned_value
        return cleaned
    
    elif isinstance(data, list):
        return [clean_politician_data(item) for item in data]
    
    else:
        return data

# 클린업할 파일 목록
POLITICIAN_FILES = [
    'national_assembly_22nd.json',
    'national_assembly_22nd_enhanced.json',
    'national_assembly_22nd_fixed.json',
    'national_assembly_22nd_real.json',
    'seoul_si_uiwon_8th.json',
    'seoul_gu_uiwon_8th.json',
    'seoul_mayor_8th.json',
    'seoul_gu_mayor_8th.json',
    'assembly_by_region.json',
    'previous_election_data.json',
    'previous_election_data_complete.json',
    'real_election_data.json',
]

def clean_file(filename):
    """파일 클린업"""
    filepath = DATA_DIR / filename
    
    # .gz 파일도 체크
    if not filepath.exists():
        gz_path = DATA_DIR / (filename + '.gz')
        if gz_path.exists():
            print(f"⚠️  {filename}.gz는 압축 파일이라 스킵")
            return False
        print(f"⚠️  {filename} 파일 없음")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📖 {filename} 로딩...")
        
        # 클린업
        cleaned_data = clean_politician_data(data)
        
        # 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {filename} 클린업 완료")
        return True
    
    except Exception as e:
        print(f"❌ {filename} 처리 실패: {e}")
        return False

if __name__ == '__main__':
    print("=== 정치인 데이터 클린업 시작 ===\n")
    
    success_count = 0
    total_count = 0
    
    for filename in POLITICIAN_FILES:
        total_count += 1
        if clean_file(filename):
            success_count += 1
        print()
    
    print(f"=== 완료: {success_count}/{total_count} 파일 클린업 ===")

