#!/usr/bin/env python3
"""
샘플 뉴스만 수집 (LDA 없이)
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'
OUTPUT_DIR = BASE_DIR / 'output' / 'lda_results'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def search_news(politician_name, client_id, client_secret, max_results=50):
    """네이버 뉴스 검색"""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    params = {
        "query": politician_name,
        "display": min(max_results, 100),
        "sort": "date"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('items', [])
            print(f"  ✅ {len(articles)}개 기사 수집")
            return articles
        else:
            print(f"  ❌ API 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return []

def main():
    print("=== 샘플 뉴스 수집 (LDA 없이) ===\n")
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    naver = config['naver_api']
    
    # 테스트 정치인
    politicians = [
        {'name': '이재명', 'party': '더불어민주당', 'district': '경기', 'position': '국회의원'},
        {'name': '한동훈', 'party': '국민의힘', 'district': '서울', 'position': '국회의원'},
        {'name': '오세훈', 'party': '국민의힘', 'district': '서울', 'position': '시장'},
    ]
    
    results = {}
    
    for i, pol in enumerate(politicians, 1):
        name = pol['name']
        print(f"[{i}/3] {name}")
        
        articles = search_news(name, naver['client_id'], naver['client_secret'], 50)
        
        if articles:
            # 키워드 간단 추출 (공백 분리)
            all_words = []
            for article in articles:
                title = article.get('title', '').replace('<b>', '').replace('</b>', '')
                desc = article.get('description', '').replace('<b>', '').replace('</b>', '')
                words = title.split() + desc.split()
                all_words.extend([w for w in words if len(w) > 1])
            
            from collections import Counter
            top_keywords = Counter(all_words).most_common(20)
            
            results[name] = {
                'member_info': pol,
                'total_count': len(articles),
                'last_updated': datetime.now().isoformat(),
                'articles': articles[:10],  # 상위 10개만
                'top_keywords': top_keywords,
                'issues': [{
                    'category': '전체',
                    'count': len(articles),
                    'top_keywords': top_keywords[:15]
                }]
            }
            
            print(f"  📊 키워드: {', '.join([kw[0] for kw in top_keywords[:5]])}")
        
        print()
        time.sleep(0.5)
    
    # 저장
    output_file = OUTPUT_DIR / 'sample_news_only.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 완료!")
    print(f"💾 저장: {output_file}")
    print(f"📊 총 {len(results)}명, {sum(r['total_count'] for r in results.values())}개 기사")
    
    # InsightForge에 복사
    target = BASE_DIR.parent / 'insightforge-web' / 'data' / 'sample_lda_analysis.json'
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ InsightForge 복사: {target}")
    print(f"\n🌐 Git 푸시 후 웹에서 확인:")
    print(f"  https://newsbot.kr/api/politician/이재명/lda")
    
    return results

if __name__ == '__main__':
    main()

