#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지방 정치인 행정사무감사 뉴스 수집 스크립트
- 시장, 시의원, 구청장, 구의원 대상
- 네이버 뉴스 검색 API 사용
"""

import requests
import json
import time
from datetime import datetime
import os
import schedule

# 네이버 API 인증 정보 (지방 정치인용)
CLIENT_ID = "ULDLTGiPvrrPBgbuydSm"
CLIENT_SECRET = "uO5mu7UQBg"

# API 엔드포인트
NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"

# 데이터 저장 경로
OUTPUT_DIR = "news_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "local_politicians_news.json")

# 데이터 파일 경로
MAYOR_FILE = "seoul_mayor_8th_real.json"
SI_UIWON_FILE = "seoul_si_uiwon_8th_real.json"
GU_MAYOR_FILE = "seoul_gu_mayor_8th.json"
GU_UIWON_FILE = "seoul_gu_uiwon_8th_real.json"


def check_internet_connection():
    """인터넷 연결 확인"""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False


def search_naver_news(query, display=10, start=1, retry_count=3):
    """네이버 뉴스 검색 (재시도 로직 포함)"""
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": "date"  # 최신순 정렬
    }
    
    for attempt in range(retry_count):
        try:
            response = requests.get(NAVER_NEWS_API_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"  ⚠️  타임아웃 (시도 {attempt + 1}/{retry_count})")
            if attempt < retry_count - 1:
                time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  네트워크 연결 오류 (시도 {attempt + 1}/{retry_count})")
            if attempt < retry_count - 1:
                time.sleep(5)
        except requests.exceptions.HTTPError as e:
            print(f"  ❌ HTTP 오류: {e.response.status_code}")
            if e.response.status_code == 429:
                print(f"  ⏳ API 호출 한도 초과, 60초 대기...")
                time.sleep(60)
            break
        except requests.exceptions.RequestException as e:
            print(f"  ❌ API 요청 실패: {e}")
            break
    
    return None


def load_mayor_data():
    """시장 데이터 로드"""
    # 서울시장은 고정 (오세훈)
    return [{
        'name': '오세훈',
        'position': '시장',
        'district': '서울특별시',
        'party': '국민의힘'
    }]


def load_si_uiwon_data():
    """시의원 데이터 로드"""
    if not os.path.exists(SI_UIWON_FILE):
        return []
    
    with open(SI_UIWON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    politicians = []
    for district_data in data.values():
        if isinstance(district_data, list):
            for member in district_data:
                if isinstance(member, dict):
                    name = member.get('name', '').split('\n')[0]
                    if name:
                        politicians.append({
                            'name': name,
                            'position': '시의원',
                            'district': member.get('district', ''),
                            'party': member.get('party', '')
                        })
    
    return politicians


def load_gu_mayor_data():
    """구청장 데이터 로드"""
    if not os.path.exists(GU_MAYOR_FILE):
        return []
    
    with open(GU_MAYOR_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    politicians = []
    for gu_name, member_data in data.items():
        if isinstance(member_data, dict):
            raw_name = member_data.get('name', '')
            # 한자 제거: "정문헌 (鄭文憲)" → "정문헌" 또는 "정문헌\n(鄭文憲)" → "정문헌"
            if '(' in raw_name:
                name = raw_name.split('(')[0].split('\n')[0].strip()
            else:
                name = raw_name.split('\n')[0].strip()
            
            if name:
                politicians.append({
                    'name': name,
                    'position': '구청장',
                    'district': gu_name,
                    'party': member_data.get('party', '')
                })
    
    return politicians


def load_gu_uiwon_data():
    """구의원 데이터 로드"""
    if not os.path.exists(GU_UIWON_FILE):
        return []
    
    with open(GU_UIWON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    politicians = []
    for gu_name, members_list in data.items():
        if isinstance(members_list, list):
            for member in members_list:
                if isinstance(member, dict):
                    name = member.get('name', '').split('\n')[0]
                    if name:
                        politicians.append({
                            'name': name,
                            'position': '구의원',
                            'district': member.get('district', gu_name),
                            'party': member.get('party', '')
                        })
    
    return politicians


def collect_politician_news(politician):
    """정치인 뉴스 수집"""
    name = politician['name']
    position = politician['position']
    
    articles = []
    
    # 시장은 국정감사 + 행정사무감사 (각 50건, 5페이지)
    if position == '시장':
        # 국정감사
        query1 = f"{name} 국정감사"
        print(f"  🔍 검색 1: {query1} (5페이지)")
        for page in range(1, 6):  # 1~5페이지
            result1 = search_naver_news(query1, display=10, start=(page-1)*10+1)
            if result1 and 'items' in result1:
                for item in result1['items']:
                    articles.append({
                        'title': item['title'].replace('<b>', '').replace('</b>', ''),
                        'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
                        'link': item['link'],
                        'pubDate': item['pubDate'],
                        'originallink': item.get('originallink', ''),
                        'search_type': '국정감사'
                    })
            time.sleep(0.1)
        
        # 행정사무감사
        query2 = f"{name} 행정사무감사"
        print(f"  🔍 검색 2: {query2} (5페이지)")
        for page in range(1, 6):  # 1~5페이지
            result2 = search_naver_news(query2, display=10, start=(page-1)*10+1)
            if result2 and 'items' in result2:
                for item in result2['items']:
                    articles.append({
                        'title': item['title'].replace('<b>', '').replace('</b>', ''),
                        'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
                        'link': item['link'],
                        'pubDate': item['pubDate'],
                        'originallink': item.get('originallink', ''),
                        'search_type': '행정사무감사'
                    })
            time.sleep(0.1)
    
    # 구청장은 행정사무감사만 (50건, 5페이지)
    elif position == '구청장':
        query = f"{name} 구청장 행정사무감사"
        print(f"  🔍 검색: {query} (5페이지)")
        for page in range(1, 6):  # 1~5페이지
            result = search_naver_news(query, display=10, start=(page-1)*10+1)
            if result and 'items' in result:
                for item in result['items']:
                    articles.append({
                        'title': item['title'].replace('<b>', '').replace('</b>', ''),
                        'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
                        'link': item['link'],
                        'pubDate': item['pubDate'],
                        'originallink': item.get('originallink', ''),
                        'search_type': '행정사무감사'
                    })
            time.sleep(0.1)
    
    # 시의원, 구의원은 행정사무감사만 (30건, 3페이지)
    else:
        query = f"{name} {position} 행정사무감사"
        print(f"  🔍 검색: {query} (3페이지)")
        for page in range(1, 4):  # 1~3페이지
            result = search_naver_news(query, display=10, start=(page-1)*10+1)
            if result and 'items' in result:
                for item in result['items']:
                    articles.append({
                        'title': item['title'].replace('<b>', '').replace('</b>', ''),
                        'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
                        'link': item['link'],
                        'pubDate': item['pubDate'],
                        'originallink': item.get('originallink', ''),
                        'search_type': '행정사무감사'
                    })
            time.sleep(0.1)
    
    print(f"  ✅ {len(articles)}건 수집")
    return articles


def load_existing_data():
    """기존 수집 데이터 로드"""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    """데이터 저장"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 데이터 저장 완료: {OUTPUT_FILE}")


def collect_all_news():
    """모든 지방 정치인의 뉴스 수집"""
    print("\n" + "="*60)
    print(f"🕐 지방 정치인 뉴스 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # 인터넷 연결 확인
    if not check_internet_connection():
        print("❌ 인터넷 연결이 없습니다.")
        print("💡 오프라인 모드: 기존 데이터를 유지합니다.")
        
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"✅ 기존 데이터 유지: {len(existing_data)}명")
        
        return
    
    print("✅ 인터넷 연결 확인 완료\n")
    
    # 정치인 데이터 로드
    print("📂 정치인 데이터 로딩 중...")
    mayors = load_mayor_data()
    si_uiwons = load_si_uiwon_data()
    gu_mayors = load_gu_mayor_data()
    gu_uiwons = load_gu_uiwon_data()
    
    all_politicians = mayors + si_uiwons + gu_mayors + gu_uiwons
    
    print(f"✅ 로드 완료:")
    print(f"  - 시장: {len(mayors)}명")
    print(f"  - 시의원: {len(si_uiwons)}명")
    print(f"  - 구청장: {len(gu_mayors)}명")
    print(f"  - 구의원: {len(gu_uiwons)}명")
    print(f"  - 총계: {len(all_politicians)}명\n")
    
    # 기존 데이터 로드
    all_data = load_existing_data()
    
    # 각 정치인별로 뉴스 수집
    collected_count = 0
    failed_count = 0
    
    for i, politician in enumerate(all_politicians, 1):
        name = politician['name']
        position = politician['position']
        
        print(f"[{i}/{len(all_politicians)}] {name} ({position}, {politician['district']})")
        
        # 뉴스 수집
        articles = collect_politician_news(politician)
        
        if articles:
            # 기존 데이터에 추가 (중복 제거)
            if name not in all_data:
                all_data[name] = {
                    'politician_info': politician,
                    'collected_date': datetime.now().strftime('%Y%m%d'),
                    'total_count': 0,
                    'news': []
                }
            
            # 중복 체크 (링크 기준)
            existing_links = {article['link'] for article in all_data[name]['news']}
            new_articles = [a for a in articles if a['link'] not in existing_links]
            
            all_data[name]['news'].extend(new_articles)
            all_data[name]['total_count'] = len(all_data[name]['news'])
            all_data[name]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            collected_count += len(new_articles)
            print(f"  📰 신규 기사: {len(new_articles)}건 (전체: {all_data[name]['total_count']}건)")
        else:
            failed_count += 1
            print(f"  ❌ 수집 실패")
        
        # API 호출 제한 - 0.1초 대기
        time.sleep(0.1)
        
        # 50명마다 중간 저장
        if i % 50 == 0:
            save_data(all_data)
            print(f"\n💾 중간 저장 완료 ({i}/{len(all_politicians)})\n")
    
    # 최종 저장
    save_data(all_data)
    
    print("\n" + "="*60)
    print(f"✅ 수집 완료: 총 {collected_count}건의 신규 기사")
    if failed_count > 0:
        print(f"⚠️  수집 실패: {failed_count}명")
    print(f"📊 전체 데이터: {len(all_data)}명의 정치인, {sum(d['total_count'] for d in all_data.values())}건의 기사")
    print(f"🕐 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


def schedule_daily_collection():
    """매일 3회 수집 스케줄 설정"""
    schedule.every().day.at("09:00").do(collect_all_news)
    schedule.every().day.at("15:00").do(collect_all_news)
    schedule.every().day.at("21:00").do(collect_all_news)
    
    print("⏰ 지방 정치인 뉴스 스케줄러 시작")
    print("📅 수집 시간: 매일 09:00, 15:00, 21:00")
    print("💡 종료하려면 Ctrl+C를 누르세요\n")
    
    # 첫 실행
    collect_all_news()
    
    # 스케줄 실행
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        collect_all_news()
    elif len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        try:
            schedule_daily_collection()
        except KeyboardInterrupt:
            print("\n\n⏹️  스케줄러 종료")
    else:
        print("사용법:")
        print("  python3 collect_local_politicians_news.py --once      # 1회 실행")
        print("  python3 collect_local_politicians_news.py --schedule  # 스케줄러 실행 (매일 3회)")

