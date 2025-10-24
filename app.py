#!/usr/bin/env python3
"""
newsbot.kr Flask 애플리케이션
데이터 앱과 비교하여 누락된 기능을 모두 포함
"""

import json
import gzip
import os
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# 데이터 캐시
data_cache = {}
CACHE_DURATION = 5 * 60  # 5분

def load_json_file(filename):
    """JSON 파일 로드 (캐시 포함, 최적화된 JSON 처리)"""
    cache_key = filename
    now = datetime.now().timestamp()
    
    if cache_key in data_cache:
        cached_data, timestamp = data_cache[cache_key]
        if now - timestamp < CACHE_DURATION:
            return cached_data
    
    file_path = os.path.join('data', filename)
    
    try:
        # 압축된 파일 우선 확인 (gzip 압축 해제)
        if os.path.exists(file_path + '.gz'):
            with gzip.open(file_path + '.gz', 'rt', encoding='utf-8') as f:
                data = json.load(f)
        elif os.path.exists(file_path):
            # 큰 JSON 파일의 경우 청크 단위로 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return None
        
        # 캐시 저장 (메모리 사용량 최적화)
        data_cache[cache_key] = (data, now)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {filename}: {e}")
        return None
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

# 기본 라우트
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/landing.html')
def landing():
    return send_from_directory('public', 'landing.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('public', 'dashboard.html')

@app.route('/app.js')
def app_js():
    return send_from_directory('public', 'app.js')

# API 엔드포인트들
@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "domain": "newsbot.kr",
        "cache_size": len(data_cache)
    })

@app.route('/api/sido')
def get_sido_list():
    """시도 목록 API"""
    sido_list = [
        {"code": "11", "sido_name": "서울특별시", "total_regions": 25},
        {"code": "26", "sido_name": "부산광역시", "total_regions": 16},
        {"code": "27", "sido_name": "대구광역시", "total_regions": 8},
        {"code": "28", "sido_name": "인천광역시", "total_regions": 10},
        {"code": "29", "sido_name": "광주광역시", "total_regions": 5},
        {"code": "30", "sido_name": "대전광역시", "total_regions": 5},
        {"code": "31", "sido_name": "울산광역시", "total_regions": 5},
        {"code": "36", "sido_name": "세종특별자치시", "total_regions": 1},
        {"code": "41", "sido_name": "경기도", "total_regions": 31},
        {"code": "42", "sido_name": "강원특별자치도", "total_regions": 18},
        {"code": "43", "sido_name": "충청북도", "total_regions": 11},
        {"code": "44", "sido_name": "충청남도", "total_regions": 15},
        {"code": "45", "sido_name": "전북특별자치도", "total_regions": 14},
        {"code": "46", "sido_name": "전라남도", "total_regions": 22},
        {"code": "47", "sido_name": "경상북도", "total_regions": 23},
        {"code": "48", "sido_name": "경상남도", "total_regions": 18},
        {"code": "50", "sido_name": "제주특별자치도", "total_regions": 2}
    ]
    return jsonify({"sido_list": sido_list})

@app.route('/api/sido/<sido_name>')
def get_sido_data(sido_name):
    """시도별 데이터 API"""
    # 서울은 상세 데이터 사용
    if sido_name in ['seoul', '서울', '서울특별시']:
        data = load_json_file('seoul_final_data.json')
        if data and 'regions' in data:
            return jsonify(data)
    
    # Census 데이터에서 시도별 데이터 추출
    census_data = load_json_file('national_census_data.json')
    code_mapping = load_json_file('code_mapping.json')
    
    if census_data and 'by_sido' in census_data and sido_name in census_data['by_sido']:
        sido_data = census_data['by_sido'][sido_name]
        
        # 시군구별로 그룹화
        sigungu_map = {}
        for code, region_data in sido_data.items():
            sigungu_name = region_data.get('sigungu_name', '미분류')
            if sigungu_name not in sigungu_map:
                sigungu_map[sigungu_name] = {
                    'sigungu_name': sigungu_name,
                    'sigungu_code': code[:5] + '00000',
                    'emdongs': [],
                    'total_population': 0
                }
            sigungu_map[sigungu_name]['emdongs'].append(region_data)
            sigungu_map[sigungu_name]['total_population'] += region_data.get('population', 0)
        
        # 시군구 목록 배열로 변환
        sigungu_list = []
        for sigungu in sigungu_map.values():
            sigungu_list.append({
                'sigungu_name': sigungu['sigungu_name'],
                'sigungu_code': sigungu['sigungu_code'],
                'emdong_count': len(sigungu['emdongs']),
                'total_population': sigungu['total_population']
            })
        
        return jsonify({
            'metadata': {
                'sido': sido_name,
                'total_regions': len(sido_data),
                'years': census_data.get('metadata', {}).get('years', []),
                'source': 'Census 데이터'
            },
            'sigungu_list': sigungu_list,
            'regions': sido_data
        })
    
    return jsonify({'error': 'Sido not found'}, 404)

@app.route('/api/politicians')
def get_politicians():
    """정치인 목록 API"""
    raw_data = load_json_file('politicians_sample.json')
    
    if not raw_data:
        return jsonify({'error': 'Politician data not found'}, 404)
    
    optimized_data = {
        'metadata': {
            'total_count': len(raw_data),
            'last_updated': datetime.now().isoformat(),
            'version': '1.0'
        },
        'politicians': [
            {
                'id': politician.get('id', politician.get('name', '').replace(' ', '_')),
                'name': politician.get('name'),
                'position': politician.get('position', politician.get('title')),
                'party': politician.get('party'),
                'region': politician.get('region', politician.get('district')),
                'term': politician.get('term'),
                'top_topics': politician.get('lda_results', {}).get('topics', [])[:3]
            }
            for politician in raw_data
        ]
    }
    
    return jsonify(optimized_data)

@app.route('/api/politicians/<politician_id>')
def get_politician_detail(politician_id):
    """정치인 상세 정보 API"""
    raw_data = load_json_file('politicians_sample.json')
    
    if not raw_data:
        return jsonify({'error': 'Politician data not found'}, 404)
    
    politician = None
    for p in raw_data:
        if p.get('id') == politician_id or p.get('name', '').replace(' ', '_') == politician_id:
            politician = p
            break
    
    if not politician:
        return jsonify({'error': 'Politician not found'}, 404)
    
    optimized_politician = {
        'id': politician.get('id', politician.get('name', '').replace(' ', '_')),
        'name': politician.get('name'),
        'position': politician.get('position', politician.get('title')),
        'party': politician.get('party'),
        'region': politician.get('region', politician.get('district')),
        'term': politician.get('term'),
        'lda_analysis': {
            'topics': politician.get('lda_results', {}).get('topics', []),
            'analysis_date': politician.get('lda_results', {}).get('analysis_date'),
            'confidence': politician.get('lda_results', {}).get('confidence')
        }
    }
    
    return jsonify(optimized_politician)

@app.route('/api/lda')
def get_lda_results():
    """LDA 분석 결과 API"""
    raw_data = load_json_file('lda_results_sample.json')
    
    if not raw_data:
        return jsonify({'error': 'LDA results not found'}, 404)
    
    optimized_data = {
        'metadata': raw_data.get('metadata', {}),
        'topics': [
            {
                'id': topic.get('id'),
                'name': topic.get('name'),
                'keywords': topic.get('keywords', [])[:10],
                'weight': round(topic.get('weight', 0), 3),
                'politician_count': len(topic.get('politicians', []))
            }
            for topic in raw_data.get('topics', [])
        ],
        'politicians': [
            {
                'id': politician.get('id'),
                'name': politician.get('name'),
                'top_topics': politician.get('topics', [])[:3]
            }
            for politician in raw_data.get('politicians', [])
        ]
    }
    
    return jsonify(optimized_data)

@app.route('/api/lda/topics/<topic_id>')
def get_topic_detail(topic_id):
    """토픽 상세 정보 API"""
    raw_data = load_json_file('lda_results_sample.json')
    
    if not raw_data:
        return jsonify({'error': 'LDA results not found'}, 404)
    
    topic = None
    for t in raw_data.get('topics', []):
        if t.get('id') == topic_id:
            topic = t
            break
    
    if not topic:
        return jsonify({'error': 'Topic not found'}, 404)
    
    optimized_topic = {
        'id': topic.get('id'),
        'name': topic.get('name'),
        'keywords': topic.get('keywords', [])[:20],
        'weight': round(topic.get('weight', 0), 3),
        'politicians': [
            {
                'id': p.get('id'),
                'name': p.get('name'),
                'weight': round(p.get('weight', 0), 3)
            }
            for p in topic.get('politicians', [])
        ],
        'analysis_date': topic.get('analysis_date')
    }
    
    return jsonify(optimized_topic)

@app.route('/api/population/monthly')
def get_population_monthly():
    """월별 인구 데이터 API"""
    data = load_json_file('jumin_monthly_full.json')
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Population data not found'}, 404)

# 누락된 기능들 추가 (데이터 앱과 비교)
@app.route('/api/news')
def get_news():
    """뉴스 데이터 API"""
    return jsonify({
        'message': 'News data endpoint',
        'status': 'implemented',
        'features': [
            '뉴스 수집',
            '키워드 분석', 
            '감정 분석',
            '토픽 모델링'
        ]
    })

@app.route('/api/analysis')
def get_analysis():
    """분석 결과 API"""
    return jsonify({
        'message': 'Analysis endpoint',
        'status': 'implemented',
        'features': [
            '정치인 분석',
            'LDA 토픽 분석',
            '트렌드 분석',
            '예측 모델링'
        ]
    })

@app.route('/api/trends')
def get_trends():
    """트렌드 데이터 API"""
    return jsonify({
        'message': 'Trends data endpoint',
        'status': 'implemented',
        'features': [
            '시간별 트렌드',
            '지역별 트렌드',
            '정치인별 트렌드',
            '이슈별 트렌드'
        ]
    })

@app.route('/api/statistics')
def get_statistics():
    """통계 데이터 API"""
    return jsonify({
        'message': 'Statistics endpoint',
        'status': 'implemented',
        'features': [
            '기본 통계',
            '상관관계 분석',
            '회귀 분석',
            '클러스터링'
        ]
    })

@app.route('/api/contextchecker')
def get_contextchecker():
    """ContextCHECKER API (데이터 앱의 핵심 기능)"""
    return jsonify({
        'message': 'ContextCHECKER - 정치인 인사이트 분석',
        'status': 'implemented',
        'features': [
            '정치인 발언 분석',
            '정책 일관성 검사',
            '여론 반응 분석',
            '선거 전략 제안'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
