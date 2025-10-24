#!/usr/bin/env python3
"""
전체 496명 정치인 LDA 분석 실행
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import time

# scripts 경로 추가
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

def full_analysis():
    """전체 정치인 LDA 분석"""
    print("=" * 80)
    print("=== NewsAnalyzer 전체 분석 시작 ===")
    print("=" * 80)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    from collector import search_news, load_config
    from lda_analyzer import analyze_politician_lda, categorize_articles, extract_keywords, clean_text
    from collections import defaultdict
    
    config = load_config()
    naver_config = config['naver_api']
    
    # 정치인 목록 로드
    politicians_file = Path(__file__).parent / 'data' / 'politicians.json'
    with open(politicians_file, 'r', encoding='utf-8') as f:
        all_politicians = json.load(f)
    
    total = len(all_politicians)
    print(f"📊 총 {total}명 분석 예정")
    print(f"⏱️  예상 소요 시간: 약 {total * 0.5:.0f}분 ({total * 0.5 / 60:.1f}시간)\n")
    print("=" * 80)
    print()
    
    assembly_results = {}
    local_results = {}
    
    failed_count = 0
    no_articles_count = 0
    success_count = 0
    start_time = time.time()
    
    for i, pol in enumerate(all_politicians, 1):
        name = pol['name']
        elapsed = time.time() - start_time
        avg_time = elapsed / i if i > 0 else 0
        remaining = (total - i) * avg_time
        
        print(f"[{i}/{total}] 🔍 {name} ({pol.get('party', '')[:6]})")
        print(f"  ⏱️  경과: {elapsed/60:.1f}분 | 예상 남은 시간: {remaining/60:.1f}분")
        
        # 1. 뉴스 수집
        try:
            articles = search_news(name, naver_config['client_id'], naver_config['client_secret'], max_results=50)
            
            if not articles:
                print(f"  ⚠️  기사 없음")
                no_articles_count += 1
                continue
            
            print(f"  ✅ {len(articles)}개 기사")
            
            # 2. 카테고리 분류
            categories = categorize_articles(articles)
            
            # 3. LDA 분석
            lda_result = analyze_politician_lda(name, articles, config)
            
            if not lda_result:
                print(f"  ❌ LDA 실패")
                failed_count += 1
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
            
            success_count += 1
            print(f"  ✅ 완료 ({len(result['issues'])}개 카테고리, {len(lda_result['topics'])}개 토픽)")
            print(f"  📈 진행률: {success_count}/{total} ({success_count/total*100:.1f}%)")
            
            # 50명마다 중간 저장
            if i % 50 == 0:
                print(f"\n💾 중간 저장 (진행률 {i}/{total})...")
                output_dir = Path(__file__).parent / 'output' / 'lda_results'
                output_dir.mkdir(parents=True, exist_ok=True)
                
                if assembly_results:
                    with open(output_dir / 'assembly_lda_progress.json', 'w', encoding='utf-8') as f:
                        json.dump(assembly_results, f, ensure_ascii=False, indent=2)
                
                if local_results:
                    with open(output_dir / 'local_lda_progress.json', 'w', encoding='utf-8') as f:
                        json.dump(local_results, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 중간 저장 완료\n")
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            failed_count += 1
            continue
    
    # 최종 저장
    print("\n" + "=" * 80)
    print("=== 최종 결과 저장 ===")
    print("=" * 80)
    
    output_dir = Path(__file__).parent / 'output' / 'lda_results'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y%m%d')
    
    if assembly_results:
        assembly_file = output_dir / f'assembly_member_lda_analysis.json'
        with open(assembly_file, 'w', encoding='utf-8') as f:
            json.dump(assembly_results, f, ensure_ascii=False, indent=2)
        print(f"💾 국회의원: {assembly_file} ({len(assembly_results)}명)")
    
    if local_results:
        local_file = output_dir / f'local_politicians_lda_analysis.json'
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(local_results, f, ensure_ascii=False, indent=2)
        print(f"💾 지방정치인: {local_file} ({len(local_results)}명)")
    
    # InsightForge에 복사
    print("\n📦 InsightForge 배포 준비...")
    insightforge_dir = Path(__file__).parent.parent / 'insightforge-web' / 'data'
    
    if assembly_results:
        target = insightforge_dir / 'assembly_member_lda_analysis.json'
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(assembly_results, f, ensure_ascii=False, indent=2)
        print(f"✅ {target}")
    
    if local_results:
        target = insightforge_dir / 'local_politicians_lda_analysis.json'
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(local_results, f, ensure_ascii=False, indent=2)
        print(f"✅ {target}")
    
    # 통계 출력
    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("=== 분석 완료! ===")
    print("=" * 80)
    print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  총 소요 시간: {total_time/60:.1f}분 ({total_time/3600:.2f}시간)")
    print(f"📊 총 대상: {total}명")
    print(f"✅ 성공: {success_count}명 ({success_count/total*100:.1f}%)")
    print(f"⚠️  기사 없음: {no_articles_count}명")
    print(f"❌ 실패: {failed_count}명")
    print(f"📈 국회의원: {len(assembly_results)}명")
    print(f"📈 지방정치인: {len(local_results)}명")
    print("=" * 80)

if __name__ == '__main__':
    try:
        full_analysis()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        print("💾 중간 결과는 저장되어 있습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

