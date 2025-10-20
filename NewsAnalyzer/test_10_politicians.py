#!/usr/bin/env python3
"""
10명의 정치인으로 전체 파이프라인 테스트
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# scripts 경로 추가
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

def test_pipeline():
    """10명으로 빠른 테스트"""
    print("=== NewsAnalyzer 10명 테스트 실행 ===\n")
    
    from collector import search_news, load_config
    from lda_analyzer import analyze_politician_lda, categorize_articles, extract_keywords, clean_text
    from collections import defaultdict
    
    config = load_config()
    naver_config = config['naver_api']
    
    # 정치인 목록 로드
    politicians_file = Path(__file__).parent / 'data' / 'politicians.json'
    with open(politicians_file, 'r', encoding='utf-8') as f:
        all_politicians = json.load(f)
    
    # 처음 10명만 선택
    test_politicians = all_politicians[:10]
    
    print(f"📊 총 {len(test_politicians)}명 테스트\n")
    
    assembly_results = {}
    local_results = {}
    
    for i, pol in enumerate(test_politicians, 1):
        name = pol['name']
        print(f"[{i}/{len(test_politicians)}] 🔍 {name} ({pol.get('party', '')}) 분석 중...")
        
        # 1. 뉴스 수집
        print(f"  📡 뉴스 검색...")
        articles = search_news(name, naver_config['client_id'], naver_config['client_secret'], max_results=50)
        
        if not articles:
            print(f"  ❌ 기사 없음\n")
            continue
        
        print(f"  ✅ {len(articles)}개 기사 수집")
        
        # 2. 카테고리 분류
        print(f"  🏷️ 카테고리 분류...")
        categories = categorize_articles(articles)
        
        # 3. LDA 분석
        print(f"  🤖 LDA 분석 중...")
        lda_result = analyze_politician_lda(name, articles, config)
        
        if not lda_result:
            print(f"  ❌ LDA 분석 실패\n")
            continue
        
        # 4. 결과 구성
        result = {
            'member_info': {
                'name': name,
                'party': pol.get('party', ''),
                'district': pol.get('district', ''),
                'position': pol.get('position', '')
            },
            'total_count': len(articles),
            'last_updated': datetime.now().isoformat(),
            'collected_date': datetime.now().strftime('%Y%m%d'),
            'issues': []
        }
        
        # 카테고리별 통계
        for category, cat_articles in categories.items():
            if cat_articles:
                cat_keywords = []
                for article in cat_articles:
                    text = clean_text(article.get('title', '') + ' ' + article.get('description', ''))
                    keywords = extract_keywords(text)
                    cat_keywords.extend(keywords)
                
                keyword_freq = defaultdict(int)
                for kw in cat_keywords:
                    keyword_freq[kw] += 1
                
                top_kw = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:15]
                
                result['issues'].append({
                    'category': category,
                    'count': len(cat_articles),
                    'top_keywords': top_kw
                })
        
        # LDA 토픽 추가
        result['lda_topics'] = lda_result['topics']
        result['top_keywords_overall'] = lda_result['top_keywords']
        
        # 구분
        if pol.get('type') == '국회의원' or '국회의원' in pol.get('position', ''):
            assembly_results[name] = result
        else:
            local_results[name] = result
        
        print(f"  ✅ 완료: {len(result['issues'])}개 카테고리, {len(lda_result['topics'])}개 토픽")
        print(f"  📊 상위 키워드: {', '.join([kw[0] for kw in lda_result['top_keywords'][:5]])}")
        print()
    
    # 저장
    output_dir = Path(__file__).parent / 'output' / 'lda_results'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if assembly_results:
        assembly_file = output_dir / 'assembly_lda_test10.json'
        with open(assembly_file, 'w', encoding='utf-8') as f:
            json.dump(assembly_results, f, ensure_ascii=False, indent=2)
        print(f"💾 국회의원 저장: {assembly_file}")
    
    if local_results:
        local_file = output_dir / 'local_lda_test10.json'
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(local_results, f, ensure_ascii=False, indent=2)
        print(f"💾 지방정치인 저장: {local_file}")
    
    print(f"\n✅ 테스트 완료!")
    print(f"📊 국회의원: {len(assembly_results)}명")
    print(f"📊 지방정치인: {len(local_results)}명")

if __name__ == '__main__':
    try:
        test_pipeline()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

