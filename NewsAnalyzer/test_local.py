#!/usr/bin/env python3
"""
로컬 테스트 - 소수 정치인으로 전체 파이프라인 테스트
"""

import json
import sys
from pathlib import Path

# scripts 경로 추가
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from collector import search_news, load_config
from lda_analyzer import analyze_politician_lda, categorize_articles, clean_text, extract_keywords

def test_pipeline():
    """파이프라인 테스트"""
    print("=== NewsAnalyzer 로컬 테스트 ===\n")
    
    # 설정 로드
    config = load_config()
    
    # 테스트 정치인 (5명)
    test_politicians = [
        {'name': '오세훈', 'party': '국민의힘', 'district': '서울', 'position': '시장'},
        {'name': '윤종복', 'party': '국민의힘', 'district': '종로구제1선거구', 'position': '서울시의원'},
        {'name': '강동오', 'party': '더불어민주당', 'district': '강남갑', 'position': '국회의원'},
    ]
    
    naver_config = config['naver_api']
    results = {}
    
    for pol in test_politicians:
        name = pol['name']
        print(f"🔍 {name} 테스트 중...")
        
        # 1. 뉴스 수집
        articles = search_news(name, naver_config['client_id'], naver_config['client_secret'], max_results=20)
        
        if not articles:
            print(f"  ❌ 기사 없음\n")
            continue
        
        print(f"  ✅ {len(articles)}개 기사 수집")
        
        # 2. LDA 분석
        lda_result = analyze_politician_lda(name, articles, config)
        
        if not lda_result:
            print(f"  ❌ LDA 분석 실패\n")
            continue
        
        print(f"  ✅ LDA 분석 완료: {len(lda_result['topics'])}개 토픽")
        
        # 3. 카테고리 분류
        categories = categorize_articles(articles)
        cat_count = sum(1 for cat, arts in categories.items() if arts)
        print(f"  ✅ 카테고리 분류: {cat_count}개")
        
        # 4. 상위 키워드 출력
        print(f"  📊 상위 키워드:")
        for keyword, count in lda_result['top_keywords'][:5]:
            print(f"     {keyword}: {count}회")
        
        results[name] = {
            'articles': len(articles),
            'topics': len(lda_result['topics']),
            'categories': cat_count,
            'top_keyword': lda_result['top_keywords'][0] if lda_result['top_keywords'] else None
        }
        
        print()
    
    # 결과 요약
    print("=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    for name, data in results.items():
        print(f"{name}:")
        print(f"  기사: {data['articles']}개")
        print(f"  토픽: {data['topics']}개")
        print(f"  카테고리: {data['categories']}개")
        if data['top_keyword']:
            print(f"  최다 키워드: {data['top_keyword'][0]} ({data['top_keyword'][1]}회)")
        print()
    
    print("✅ 로컬 테스트 완료!")
    print("\n📋 다음 단계:")
    print("  1. ./deploy_to_synology.sh 실행 (배포 패키지 생성)")
    print("  2. 시놀로지로 파일 전송")
    print("  3. Docker 빌드 및 실행")
    print("  4. 로그 모니터링")

if __name__ == '__main__':
    try:
        test_pipeline()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

