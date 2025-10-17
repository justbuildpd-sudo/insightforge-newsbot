#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국회의원 국정감사 뉴스 수집 스크립트
- 네이버 뉴스 검색 API 사용
- 각 국회의원별로 "이름 + 국정감사" 키워드로 검색
- 매일 50건씩 3회 수집 (총 150건/일)
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os
import schedule

# 네이버 API 인증 정보
CLIENT_ID = "kXwlSsFmb055ku9rWyx1"
CLIENT_SECRET = "JZqw_LTiq_"

# API 엔드포인트
NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"

# 데이터 저장 경로
OUTPUT_DIR = "news_data"
ASSEMBLY_DATA_FILE = "assembly_by_region.json"  # 전국 298명 데이터
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "assembly_member_news.json")


def load_assembly_members():
    """국회의원 명단 로드 (전국 298명)"""
    print("📂 국회의원 데이터 로딩 중...")
    
    if not os.path.exists(ASSEMBLY_DATA_FILE):
        print(f"❌ 파일을 찾을 수 없습니다: {ASSEMBLY_DATA_FILE}")
        return []
    
    with open(ASSEMBLY_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    members = []
    
    # 지역구 의원
    if 'regional' in data:
        for sido, member_list in data['regional'].items():
            for member_data in member_list:
                name = member_data.get('name', '')
                party = member_data.get('party', '')
                district = member_data.get('district', '')
                
                if name:
                    members.append({
                        'name': name,
                        'district': district,
                        'party': party
                    })
    
    # 비례대표 의원
    if 'proportional' in data:
        for party, member_list in data['proportional'].items():
            for member_data in member_list:
                name = member_data.get('name', '')
                
                if name:
                    members.append({
                        'name': name,
                        'district': '비례대표',
                        'party': party
                    })
    
    print(f"✅ {len(members)}명의 국회의원 로드 완료")
    return members


def search_naver_news(query, display=50, start=1, retry_count=3):
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
                time.sleep(2)  # 2초 대기 후 재시도
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  네트워크 연결 오류 (시도 {attempt + 1}/{retry_count})")
            if attempt < retry_count - 1:
                time.sleep(5)  # 5초 대기 후 재시도
        except requests.exceptions.HTTPError as e:
            print(f"  ❌ HTTP 오류: {e.response.status_code}")
            if e.response.status_code == 429:  # Too Many Requests
                print(f"  ⏳ API 호출 한도 초과, 60초 대기...")
                time.sleep(60)
            break  # HTTP 에러는 재시도 안함
        except requests.exceptions.RequestException as e:
            print(f"  ❌ API 요청 실패: {e}")
            break
    
    return None


def collect_member_news(member, max_articles=50):
    """특정 국회의원의 뉴스 수집"""
    name = member['name']
    query = f"{name} 국정감사"
    
    print(f"🔍 검색 중: {query}")
    
    result = search_naver_news(query, display=max_articles)
    
    if not result or 'items' not in result:
        print(f"  ⚠️  검색 결과 없음")
        return []
    
    articles = []
    for item in result['items']:
        article = {
            'title': item['title'].replace('<b>', '').replace('</b>', ''),
            'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
            'link': item['link'],
            'pubDate': item['pubDate'],
            'originallink': item.get('originallink', '')
        }
        articles.append(article)
    
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


def check_internet_connection():
    """인터넷 연결 확인"""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False


def collect_all_news():
    """모든 국회의원의 뉴스 수집 (1회 실행)"""
    print("\n" + "="*60)
    print(f"🕐 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # 인터넷 연결 확인
    if not check_internet_connection():
        print("❌ 인터넷 연결이 없습니다.")
        print("💡 오프라인 모드: 기존 데이터를 유지합니다.")
        print("📁 다음 수집 예정 시간에 자동으로 재시도됩니다.")
        
        # 기존 데이터가 있는지 확인
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"✅ 기존 데이터 유지: {len(existing_data)}명, {sum(d['total_count'] for d in existing_data.values())}건")
        else:
            print("⚠️  기존 데이터도 없습니다. 온라인 상태에서 실행하세요.")
        
        return
    
    print("✅ 인터넷 연결 확인 완료\n")
    
    members = load_assembly_members()
    if not members:
        print("❌ 국회의원 데이터가 없습니다.")
        return
    
    # 기존 데이터 로드
    all_data = load_existing_data()
    
    # 각 국회의원별로 뉴스 수집
    collected_count = 0
    failed_count = 0
    
    for i, member in enumerate(members, 1):
        name = member['name']
        
        print(f"\n[{i}/{len(members)}] {name} ({member['district']}, {member['party']})")
        
        # 뉴스 수집 (50건)
        articles = collect_member_news(member, max_articles=50)
        
        if articles:
            # 기존 데이터에 추가 (중복 제거)
            if name not in all_data:
                all_data[name] = {
                    'member_info': member,
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
        
        # API 호출 제한 (초당 10건) - 0.1초 대기
        time.sleep(0.1)
        
        # 10명마다 중간 저장
        if i % 10 == 0:
            save_data(all_data)
            print(f"\n💾 중간 저장 완료 ({i}/{len(members)})")
    
    # 최종 저장
    save_data(all_data)
    
    print("\n" + "="*60)
    print(f"✅ 수집 완료: 총 {collected_count}건의 신규 기사")
    if failed_count > 0:
        print(f"⚠️  수집 실패: {failed_count}명")
    print(f"📊 전체 데이터: {len(all_data)}명의 국회의원, {sum(d['total_count'] for d in all_data.values())}건의 기사")
    print(f"🕐 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


def schedule_daily_collection():
    """매일 3회 수집 스케줄 설정"""
    # 매일 오전 9시, 오후 3시, 오후 9시에 수집
    schedule.every().day.at("09:00").do(collect_all_news)
    schedule.every().day.at("15:00").do(collect_all_news)
    schedule.every().day.at("21:00").do(collect_all_news)
    
    print("⏰ 스케줄러 시작")
    print("📅 수집 시간: 매일 09:00, 15:00, 21:00")
    print("💡 종료하려면 Ctrl+C를 누르세요\n")
    
    # 첫 실행
    collect_all_news()
    
    # 스케줄 실행
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 1회만 실행
        collect_all_news()
    elif len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        # 스케줄러로 실행
        try:
            schedule_daily_collection()
        except KeyboardInterrupt:
            print("\n\n⏹️  스케줄러 종료")
    else:
        print("사용법:")
        print("  python collect_assembly_member_news.py --once      # 1회 실행")
        print("  python collect_assembly_member_news.py --schedule  # 스케줄러 실행 (매일 3회)")

