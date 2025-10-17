#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지방 정치인 뉴스 LDA 분석 스크립트
"""

import json
import os
from collections import Counter
from datetime import datetime

INPUT_FILE = "news_data/local_politicians_news.json"
OUTPUT_FILE = "InsightForge/Resources/local_politicians_lda_analysis.json"


def extract_nouns_simple(text):
    """간단한 명사 추출"""
    stopwords = set([
        "이", "가", "을", "를", "의", "에", "에서", "으로", "로", "은", "는", "과", "와", "도", "만",
        "하다", "되다", "이다", "있다", "없다", "한다", "된다", "했다", "됐다", "하는", "되는",
        "등", "및", "위해", "통해", "대한", "위한", "관련", "따른", "것", "수", "중", "때"
    ])
    
    verb_endings = ["하다", "되다", "이다", "있다", "없다", "했다", "됐다", "한다", "된다", "하는", "되는", "있는"]
    
    words = text.split()
    nouns = []
    
    for word in words:
        cleaned = word.strip('.,!?()[]"\':;')
        
        if len(cleaned) >= 2 and cleaned not in stopwords:
            is_verb = any(cleaned.endswith(ending) for ending in verb_endings)
            if not is_verb and not cleaned.isdigit():
                nouns.append(cleaned)
    
    return nouns


def classify_articles_by_keywords(articles):
    """키워드 기반 기사 분류"""
    
    categories = {
        "행정사무감사": ["행정사무감사", "시정감사", "구정감사", "감사", "질의", "답변", "지적"],
        "예산·재정": ["예산", "예산안", "재정", "세금", "세출", "세입", "결산"],
        "조례·입법": ["조례", "개정", "제정", "의결", "심의", "발의"],
        "지역개발": ["개발", "재개발", "재건축", "신축", "건설", "조성"],
        "교통·인프라": ["교통", "도로", "지하철", "버스", "주차", "철도"],
        "주택·부동산": ["주택", "아파트", "부동산", "임대", "분양"],
        "복지·의료": ["복지", "의료", "건강", "병원", "보건", "돌봄"],
        "일자리·경제": ["일자리", "고용", "청년", "취업", "경제", "소상공인"],
        "교육·보육": ["교육", "학교", "학생", "어린이집", "유치원", "보육"],
        "문화·체육": ["문화", "체육", "예술", "축제", "공연", "도서관"],
        "환경·기후": ["환경", "기후", "쓰레기", "재활용", "대기", "녹지"],
        "안전·재난": ["안전", "재난", "방역", "소방", "범죄", "치안"],
        "정책발표": ["정책", "공약", "발표", "계획", "방안", "추진"],
        "민원·주민": ["민원", "주민", "청원", "간담회", "설명회", "토론회"],
        "기타": []
    }
    
    classified = {cat: [] for cat in categories.keys()}
    categorized_links = set()
    
    for category, keywords in categories.items():
        if category == "기타":
            continue
            
        for article in articles:
            if article['link'] in categorized_links:
                continue
                
            text = article['title'] + " " + article.get('description', '')
            
            if any(keyword in text for keyword in keywords):
                classified[category].append(article)
                categorized_links.add(article['link'])
    
    # 기타
    for article in articles:
        if article['link'] not in categorized_links:
            classified["기타"].append(article)
    
    return classified


def extract_top_keywords_from_articles(articles, top_n=10):
    """기사에서 상위 키워드 추출"""
    all_nouns = []
    
    for article in articles:
        text = article['title'] + " " + article.get('description', '')
        nouns = extract_nouns_simple(text)
        all_nouns.extend(nouns)
    
    word_freq = Counter(all_nouns)
    top_keywords = word_freq.most_common(top_n)
    
    return [(word, count) for word, count in top_keywords]


def analyze_politician_news(name, news_data):
    """정치인 뉴스 분석"""
    articles = news_data.get('news', [])
    
    if not articles:
        return None
    
    print(f"\n📊 분석 중: {name} ({news_data['politician_info']['position']}, {len(articles)}건)")
    
    # 이슈별 분류
    classified = classify_articles_by_keywords(articles)
    
    # 각 이슈별 키워드 추출
    issues = []
    for category, cat_articles in classified.items():
        if not cat_articles:
            continue
        
        top_keywords = extract_top_keywords_from_articles(cat_articles, top_n=10)
        
        # 날짜별 정렬 (최신순)
        sorted_articles = sorted(cat_articles, key=lambda x: x.get('pubDate', ''), reverse=True)
        
        issue = {
            'category': category,
            'count': len(cat_articles),
            'top_keywords': top_keywords,
            'articles': sorted_articles[:10]  # 최신 10건
        }
        issues.append(issue)
        
        print(f"  ✅ {category}: {len(cat_articles)}건")
    
    return {
        'politician_info': news_data['politician_info'],
        'total_count': len(articles),
        'last_updated': news_data.get('last_updated', ''),
        'collected_date': news_data.get('collected_date', ''),
        'issues': issues
    }


def main():
    """메인 분석 프로세스"""
    print("\n" + "="*60)
    print("📊 지방 정치인 뉴스 LDA 분석 시작")
    print("="*60 + "\n")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 파일을 찾을 수 없습니다: {INPUT_FILE}")
        print("💡 먼저 collect_local_politicians_news.py를 실행하세요.")
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"✅ 데이터 로드 완료: {len(raw_data)}명")
    
    # 각 정치인별 분석
    analyzed_data = {}
    
    for name, news_data in raw_data.items():
        result = analyze_politician_news(name, news_data)
        if result:
            analyzed_data[name] = result
    
    # 결과 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 분석 완료: {OUTPUT_FILE}")
    print(f"📊 총 {len(analyzed_data)}명의 정치인 데이터 생성")
    
    total_articles = sum(d['total_count'] for d in analyzed_data.values())
    total_issues = sum(len(d['issues']) for d in analyzed_data.values())
    
    print(f"📰 전체 기사: {total_articles}건")
    print(f"🏷️  전체 이슈: {total_issues}개")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

