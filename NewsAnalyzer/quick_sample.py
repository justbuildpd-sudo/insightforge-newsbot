#!/usr/bin/env python3
"""
빠른 샘플 수집 및 LDA 분석 - Java 설치 후 실행
"""

import json
import sys
from pathlib import Path

# scripts 경로 추가
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

def quick_sample():
    """3명만 빠르게 수집 및 분석"""
    print("=== NewsAnalyzer 빠른 샘플 실행 ===\n")
    
    from collector import search_news, load_config
    from lda_analyzer import analyze_politician_lda, categorize_articles
    from datetime import datetime
    
    config = load_config()
    naver_config = config['naver_api']
    
    # 테스트 정치인 3명
    test_politicians = [
        {'name': '이재명', 'party': '더불어민주당', 'district': '경기', 'position': '국회의원'},
        {'name': '한동훈', 'party': '국민의힘', 'district': '서울', 'position': '국회의원'},
        {'name': '오세훈', 'party': '국민의힘', 'district': '서울', 'position': '시장'},
    ]
    
    assembly_results = {}
    local_results = {}
    
    for i, pol in enumerate(test_politicians, 1):
        name = pol['name']
        print(f"[{i}/3] 🔍 {name} 분석 중...")
        
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
                'party': pol['party'],
                'district': pol['district'],
                'position': pol['position']
            },
            'total_count': len(articles),
            'last_updated': datetime.now().isoformat(),
            'collected_date': datetime.now().strftime('%Y%m%d'),
            'issues': []
        }
        
        # 카테고리별 통계
        from lda_analyzer import extract_keywords, clean_text
        from collections import defaultdict
        
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
        if pol['position'] == '국회의원':
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
        assembly_file = output_dir / 'assembly_lda_sample.json'
        with open(assembly_file, 'w', encoding='utf-8') as f:
            json.dump(assembly_results, f, ensure_ascii=False, indent=2)
        print(f"💾 국회의원 저장: {assembly_file}")
    
    if local_results:
        local_file = output_dir / 'local_lda_sample.json'
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(local_results, f, ensure_ascii=False, indent=2)
        print(f"💾 지방정치인 저장: {local_file}")
    
    # InsightForge에 복사
    insightforge_dir = Path(__file__).parent.parent / 'insightforge-web' / 'data'
    
    if assembly_results:
        target = insightforge_dir / 'assembly_member_lda_sample.json'
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(assembly_results, f, ensure_ascii=False, indent=2)
        print(f"✅ InsightForge 복사: {target}")
    
    print(f"\n✅ 샘플 생성 완료!")
    print(f"📊 국회의원: {len(assembly_results)}명")
    print(f"📊 지방정치인: {len(local_results)}명")
    print(f"\n🌐 웹에서 확인:")
    print(f"  https://newsbot.kr/api/politician/이재명/lda")
    print(f"  https://newsbot.kr/api/politician/한동훈/lda")
    print(f"  https://newsbot.kr/api/politician/오세훈/lda")

if __name__ == '__main__':
    try:
        quick_sample()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
        if "JVMNotFoundException" in str(e) or "No module named" in str(e):
            print("\n📋 Java 설치 가이드:")
            print("  1. https://www.oracle.com/java/technologies/downloads/ 접속")
            print("  2. macOS ARM64 (Apple Silicon) 버전 다운로드")
            print("  3. dmg 파일 설치")
            print("  4. 터미널 재시작 후 다시 실행")
        
        sys.exit(1)

