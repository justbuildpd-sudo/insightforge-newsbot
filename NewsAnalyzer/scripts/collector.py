#!/usr/bin/env python3
"""
뉴스 수집기 - 네이버 API를 통해 정치인 관련 뉴스 수집
"""

import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / 'config.json'
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'data' / 'collected'
LOG_FILE = BASE_DIR / 'logs' / 'collector.log'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """설정 파일 로드"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_politicians():
    """정치인 목록 로드"""
    politicians_file = DATA_DIR / 'politicians.json'
    if not politicians_file.exists():
        print("❌ politicians.json 파일이 없습니다. InsightForge에서 생성하겠습니다.")
        return generate_politicians_list()
    
    with open(politicians_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_politicians_list():
    """InsightForge 데이터에서 정치인 목록 생성"""
    politicians = []
    
    # 국회의원 로드
    assembly_file = BASE_DIR.parent / 'insightforge-web' / 'data' / 'national_assembly_22nd_real.json'
    if assembly_file.exists():
        with open(assembly_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for region, pols in data.items():
                if isinstance(pols, list):
                    politicians.extend(pols)
    
    # 시의원 로드 (gzip)
    import gzip
    si_uiwon_file = BASE_DIR.parent / 'insightforge-web' / 'data' / 'seoul_si_uiwon_8th.json.gz'
    if si_uiwon_file.exists():
        with gzip.open(si_uiwon_file, 'rt', encoding='utf-8') as f:
            data = json.load(f)
            for gu, pols in data.items():
                if isinstance(pols, list):
                    politicians.extend(pols)
    
    # 구의원 로드 (gzip)
    gu_uiwon_file = BASE_DIR.parent / 'insightforge-web' / 'data' / 'seoul_gu_uiwon_8th.json.gz'
    if gu_uiwon_file.exists():
        with gzip.open(gu_uiwon_file, 'rt', encoding='utf-8') as f:
            data = json.load(f)
            for gu, pols in data.items():
                if isinstance(pols, list):
                    politicians.extend(pols)
    
    # 저장
    politicians_file = DATA_DIR / 'politicians.json'
    with open(politicians_file, 'w', encoding='utf-8') as f:
        json.dump(politicians, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 정치인 목록 생성: {len(politicians)}명")
    return politicians

def search_news(politician_name, client_id, client_secret, max_results=100):
    """네이버 뉴스 검색"""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    all_articles = []
    display = 100  # 한 번에 최대 100개
    
    params = {
        "query": politician_name,
        "display": display,
        "sort": "date"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            all_articles.extend(data.get('items', []))
            print(f"  ✅ {politician_name}: {len(all_articles)}개 기사")
        else:
            print(f"  ❌ {politician_name}: API 오류 {response.status_code}")
        
        time.sleep(0.1)  # API 제한 방지
        
    except Exception as e:
        print(f"  ❌ {politician_name}: {str(e)}")
    
    return all_articles[:max_results]

def collect_all_news():
    """모든 정치인 뉴스 수집"""
    print("=== 뉴스 수집 시작 ===")
    print(f"시작 시간: {datetime.now()}")
    
    config = load_config()
    politicians = load_politicians()
    
    naver_config = config['naver_api']
    max_articles = config['collection']['max_articles_per_politician']
    
    print(f"\n📊 수집 대상: {len(politicians)}명")
    print(f"📰 정치인당 최대: {max_articles}개 기사\n")
    
    results = {}
    total_articles = 0
    
    for i, politician in enumerate(politicians):
        name = politician.get('name', '')
        if not name:
            continue
        
        print(f"[{i+1}/{len(politicians)}] {name}")
        
        articles = search_news(
            name,
            naver_config['client_id'],
            naver_config['client_secret'],
            max_articles
        )
        
        if articles:
            results[name] = {
                'politician_info': politician,
                'articles': articles,
                'collected_at': datetime.now().isoformat(),
                'count': len(articles)
            }
            total_articles += len(articles)
    
    # 저장
    output_file = OUTPUT_DIR / f'news_collected_{datetime.now().strftime("%Y%m%d")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 수집 완료!")
    print(f"📊 총 {len(results)}명 정치인, {total_articles}개 기사")
    print(f"💾 저장: {output_file}")
    
    return results

if __name__ == '__main__':
    try:
        results = collect_all_news()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

