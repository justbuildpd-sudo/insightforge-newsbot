#!/usr/bin/env python3
"""
LDA 분석기 - 수집된 뉴스를 토픽 모델링
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import sys

try:
    from kiwipiepy import Kiwi
    from gensim import corpora, models
    import numpy as np
except ImportError as e:
    print(f"❌ 필수 패키지 없음: {e}")
    print("설치: pip install kiwipiepy gensim numpy")
    sys.exit(1)

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / 'config.json'
DATA_DIR = BASE_DIR / 'data' / 'collected'
OUTPUT_DIR = BASE_DIR / 'output' / 'lda_results'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 한국어 형태소 분석기 (Kiwi - Java 불필요)
kiwi = Kiwi()

# 불용어 리스트
STOPWORDS = set([
    '이', '그', '저', '것', '수', '등', '년', '월', '일', '및', '때', '후', '전', '중',
    '씨', '명', '개', '번', '차', '위', '곳', '대', '약', '간', '내', '외', '상', '하',
    '좌', '우', '내', '외', '전', '후', '상', '하', '최', '각', '제', '말', '점'
])

def load_config():
    """설정 파일 로드"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_latest_collection():
    """최신 수집 데이터 로드"""
    files = sorted(DATA_DIR.glob('news_collected_*.json'))
    if not files:
        print("❌ 수집된 뉴스 파일이 없습니다.")
        return None
    
    latest_file = files[-1]
    print(f"📂 로드: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_text(text):
    """텍스트 정제"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 특수문자 제거
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    # 연속 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_keywords(text, min_length=2):
    """키워드 추출 (명사 중심)"""
    if not text:
        return []
    
    # 형태소 분석 (Kiwi 사용)
    result = kiwi.analyze(text)
    nouns = []
    
    if result and len(result) > 0:
        for token, pos, _, _ in result[0][0]:
            # 명사만 추출 (NNG: 일반명사, NNP: 고유명사)
            if pos in ('NNG', 'NNP'):
                nouns.append(token)
    
    # 필터링
    keywords = [
        noun for noun in nouns
        if len(noun) >= min_length and noun not in STOPWORDS
    ]
    
    return keywords

def analyze_politician_lda(politician_name, articles, config):
    """정치인별 LDA 분석"""
    if not articles:
        return None
    
    # 텍스트 추출 및 정제
    texts = []
    for article in articles:
        title = clean_text(article.get('title', ''))
        description = clean_text(article.get('description', ''))
        combined = f"{title} {description}"
        texts.append(combined)
    
    # 키워드 추출
    all_keywords = []
    for text in texts:
        keywords = extract_keywords(text, config['lda']['min_word_length'])
        all_keywords.append(keywords)
    
    if not all_keywords or all(len(k) == 0 for k in all_keywords):
        return None
    
    try:
        # LDA 모델링
        dictionary = corpora.Dictionary(all_keywords)
        dictionary.filter_extremes(no_below=2, no_above=0.5)
        
        corpus = [dictionary.doc2bow(text) for text in all_keywords]
        
        lda_model = models.LdaModel(
            corpus,
            num_topics=config['lda']['num_topics'],
            id2word=dictionary,
            passes=config['lda']['passes'],
            iterations=config['lda']['iterations'],
            random_state=42
        )
        
        # 토픽별 상위 키워드 추출
        topics = []
        for topic_id in range(config['lda']['num_topics']):
            topic_words = lda_model.show_topic(topic_id, topn=config['lda']['top_keywords'])
            topics.append({
                'topic_id': topic_id,
                'keywords': [(word, float(weight)) for word, weight in topic_words]
            })
        
        # 전체 키워드 빈도
        keyword_freq = defaultdict(int)
        for keywords in all_keywords:
            for keyword in keywords:
                keyword_freq[keyword] += 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:config['lda']['top_keywords']]
        
        return {
            'topics': topics,
            'top_keywords': top_keywords,
            'total_articles': len(articles),
            'total_keywords': len(keyword_freq)
        }
        
    except Exception as e:
        print(f"  ❌ LDA 분석 실패: {e}")
        return None

def categorize_articles(articles):
    """기사를 카테고리별로 분류"""
    categories = {
        '국정감사·질의': [],
        '교육·보육': [],
        '교통·인프라': [],
        '경제·산업': [],
        '복지·환경': [],
        '문화·체육': [],
        '기타': []
    }
    
    keywords_map = {
        '국정감사·질의': ['국정감사', '국회', '질의', '질문', '답변', '의원'],
        '교육·보육': ['교육', '학교', '학생', '보육', '어린이집', '유치원'],
        '교통·인프라': ['교통', '도로', '지하철', '버스', '철도', '인프라'],
        '경제·산업': ['경제', '산업', '기업', '일자리', '고용', '투자'],
        '복지·환경': ['복지', '환경', '주거', '건강', '의료', '보건'],
        '문화·체육': ['문화', '체육', '관광', '축제', '공원', '예술']
    }
    
    for article in articles:
        text = article.get('title', '') + ' ' + article.get('description', '')
        matched = False
        
        for category, keywords in keywords_map.items():
            if any(kw in text for kw in keywords):
                categories[category].append(article)
                matched = True
                break
        
        if not matched:
            categories['기타'].append(article)
    
    return categories

def analyze_all():
    """전체 LDA 분석 실행"""
    print("=== LDA 분석 시작 ===")
    print(f"시작 시간: {datetime.now()}")
    
    config = load_config()
    news_data = load_latest_collection()
    
    if not news_data:
        return
    
    print(f"\n📊 분석 대상: {len(news_data)}명\n")
    
    assembly_results = {}  # 국회의원
    local_results = {}     # 지방정치인
    
    for i, (politician_name, data) in enumerate(news_data.items()):
        print(f"[{i+1}/{len(news_data)}] {politician_name}")
        
        politician_info = data.get('politician_info', {})
        articles = data.get('articles', [])
        
        if not articles:
            print(f"  ⚠️ 기사 없음")
            continue
        
        # LDA 분석
        lda_result = analyze_politician_lda(politician_name, articles, config)
        
        if not lda_result:
            print(f"  ⚠️ 분석 실패")
            continue
        
        # 카테고리 분류
        categories = categorize_articles(articles)
        
        # 결과 구성
        result = {
            'member_info': {
                'name': politician_name,
                'party': politician_info.get('party', ''),
                'district': politician_info.get('district', ''),
                'position': politician_info.get('position', '')
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
        
        # 국회의원 vs 지방정치인 구분
        position = politician_info.get('position', '')
        if '국회의원' in position or politician_info.get('district', '').endswith('구'):
            assembly_results[politician_name] = result
        else:
            local_results[politician_name] = result
        
        print(f"  ✅ 분석 완료: {len(result['issues'])}개 카테고리, LDA {len(lda_result['topics'])}개 토픽")
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    
    assembly_file = OUTPUT_DIR / f'assembly_lda_{today}.json'
    with open(assembly_file, 'w', encoding='utf-8') as f:
        json.dump(assembly_results, f, ensure_ascii=False, indent=2)
    
    local_file = OUTPUT_DIR / f'local_lda_{today}.json'
    with open(local_file, 'w', encoding='utf-8') as f:
        json.dump(local_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 분석 완료!")
    print(f"📊 국회의원: {len(assembly_results)}명")
    print(f"📊 지방정치인: {len(local_results)}명")
    print(f"💾 저장: {assembly_file}")
    print(f"💾 저장: {local_file}")

if __name__ == '__main__':
    try:
        analyze_all()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

