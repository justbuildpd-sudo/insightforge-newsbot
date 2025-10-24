#!/usr/bin/env python3
"""
역사적 뉴스 수집기 - 날짜별 수집
Naver API 제한: 25,000건/일
"""

import json
import sys
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / 'config.json'
STATE_FILE = BASE_DIR / 'data' / 'collection_state.json'
OUTPUT_DIR = BASE_DIR / 'output' / 'historical'

# Naver API 제한
MAX_DAILY_CALLS = 25000
CALLS_PER_SECOND = 10
DELAY_BETWEEN_CALLS = 0.11  # 초당 9건 (여유있게)

def load_config():
    """설정 로드"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_state():
    """진행 상황 로드"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        'current_phase': 1,
        'current_date': '2020-01-01',
        'total_api_calls_today': 0,
        'completed_dates': [],
        'last_run_date': None,
        'politicians_completed': []
    }

def save_state(state):
    """진행 상황 저장"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_phase_politicians(phase_num):
    """특정 Phase 정치인 로드"""
    phase_file = BASE_DIR / 'data' / f'phase{phase_num}_politicians.json'
    
    if not phase_file.exists():
        print(f"❌ {phase_file.name} 없음")
        return []
    
    with open(phase_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_news_by_date(query, client_id, client_secret, target_date, max_results=10):
    """특정 날짜의 뉴스 검색"""
    url = "https://openapi.naver.com/v1/search/news.json"
    
    # 날짜 형식: YYYY-MM-DD
    start_date = target_date.replace('-', '')
    end_date = target_date.replace('-', '')
    
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    
    all_articles = []
    
    try:
        # 1페이지만 (10건)
        params = {
            'query': query,
            'display': min(max_results, 100),
            'start': 1,
            'sort': 'date'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        # 날짜 필터링 (API는 정확한 날짜 필터 미지원)
        for item in items:
            pub_date = item.get('pubDate', '')
            # "Mon, 01 Jan 2020 12:00:00 +0900" 형식
            if target_date.replace('-', '') in pub_date or start_date in pub_date:
                all_articles.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'description': item.get('description', ''),
                    'pub_date': pub_date,
                    'collected_date': datetime.now().isoformat(),
                    'target_date': target_date
                })
        
        return all_articles
        
    except Exception as e:
        print(f"    ❌ API 오류: {e}")
        return []

def collect_daily_batch(phase_num, target_date, max_calls=24000):
    """하루치 배치 수집"""
    print(f"\n{'='*80}")
    print(f"=== Phase {phase_num} | 날짜: {target_date} ===")
    print(f"{'='*80}\n")
    
    config = load_config()
    naver_config = config['naver_api']
    
    # 정치인 로드
    politicians = load_phase_politicians(phase_num)
    
    if not politicians:
        print("❌ 정치인 목록 없음")
        return 0
    
    print(f"📊 대상: {len(politicians)}명")
    print(f"🎯 최대 API 호출: {max_calls}건")
    
    # 출력 디렉토리
    phase_dir = OUTPUT_DIR / f'phase{phase_num}'
    date_dir = phase_dir / target_date[:7]  # YYYY-MM
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # 수집 결과
    results = {}
    api_calls = 0
    success_count = 0
    
    start_time = time.time()
    
    for i, pol in enumerate(politicians, 1):
        name = pol['name']
        
        # API 호출 제한 체크
        if api_calls >= max_calls:
            print(f"\n⚠️  일일 API 호출 제한 도달 ({api_calls}건)")
            break
        
        # 진행 상황 출력
        if i % 100 == 0:
            elapsed = time.time() - start_time
            remaining = len(politicians) - i
            eta = (elapsed / i) * remaining
            print(f"  [{i}/{len(politicians)}] 진행 중... (API: {api_calls}건, 성공: {success_count}명, ETA: {eta/60:.1f}분)")
        
        # 뉴스 검색
        articles = search_news_by_date(
            name,
            naver_config['client_id'],
            naver_config['client_secret'],
            target_date,
            max_results=10
        )
        
        api_calls += 1
        
        if articles:
            results[name] = {
                'politician_info': pol,
                'articles': articles,
                'count': len(articles)
            }
            success_count += 1
        
        # API 속도 제한
        time.sleep(DELAY_BETWEEN_CALLS)
    
    # 저장
    if results:
        output_file = date_dir / f'news_{target_date}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 저장: {output_file}")
        print(f"📊 정치인: {len(results)}명")
        print(f"📰 총 기사: {sum(r['count'] for r in results.values())}개")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  소요 시간: {elapsed/60:.1f}분")
    print(f"📞 API 호출: {api_calls}건")
    print(f"✅ 성공: {success_count}명")
    
    return api_calls

def run_daily_collection():
    """일일 수집 실행"""
    print("="*80)
    print("=== 역사적 뉴스 수집 시작 ===")
    print(f"⏰ 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 상태 로드
    state = load_state()
    
    # 오늘 이미 실행했는지 체크
    today = datetime.now().strftime('%Y-%m-%d')
    if state.get('last_run_date') == today:
        print(f"\n⚠️  오늘 이미 실행됨: {today}")
        print(f"📊 오늘 API 호출: {state.get('total_api_calls_today', 0)}건")
        return
    
    # 새로운 날짜면 API 카운터 리셋
    if state.get('last_run_date') != today:
        state['total_api_calls_today'] = 0
    
    phase_num = state['current_phase']
    target_date = state['current_date']
    
    print(f"\n📍 현재 Phase: {phase_num}")
    print(f"📅 수집 날짜: {target_date}")
    print(f"📊 남은 API 호출: {MAX_DAILY_CALLS - state['total_api_calls_today']:,}건")
    
    # 배치 수집
    calls_used = collect_daily_batch(
        phase_num,
        target_date,
        max_calls=MAX_DAILY_CALLS - state['total_api_calls_today']
    )
    
    # 상태 업데이트
    state['total_api_calls_today'] += calls_used
    state['last_run_date'] = today
    state['completed_dates'].append(target_date)
    
    # 다음 날짜로 이동
    next_date = datetime.strptime(target_date, '%Y-%m-%d') + timedelta(days=1)
    state['current_date'] = next_date.strftime('%Y-%m-%d')
    
    # Phase 완료 체크
    phase_configs = {
        1: '2025-10-20',
        2: '2019-12-31',
        3: '2015-12-31',
        4: '2011-12-31'
    }
    
    if target_date >= phase_configs.get(phase_num, '9999-12-31'):
        print(f"\n🎉 Phase {phase_num} 완료!")
        state['current_phase'] += 1
        
        # 다음 Phase 시작 날짜
        next_phase_starts = {
            2: '2016-01-01',
            3: '2012-01-01',
            4: '2008-01-01'
        }
        state['current_date'] = next_phase_starts.get(state['current_phase'], target_date)
    
    # 상태 저장
    save_state(state)
    
    print(f"\n💾 진행 상황 저장")
    print(f"📊 총 수집 일수: {len(state['completed_dates'])}일")
    print(f"📅 다음 수집 날짜: {state['current_date']}")
    print(f"🎯 다음 Phase: {state['current_phase']}")
    
    print(f"\n{'='*80}")
    print("=== 오늘 수집 완료 ===")
    print(f"⏰ 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📞 오늘 API 호출: {state['total_api_calls_today']:,}건 / {MAX_DAILY_CALLS:,}건")
    print("="*80)

if __name__ == '__main__':
    try:
        run_daily_collection()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자 중단")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

