from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 데이터 디렉토리
DATA_DIR = Path(__file__).parent.parent / "insightforge-web" / "data"

# 데이터 캐시
data_cache = {}

def load_json_file(filename):
    """JSON 파일 로드 및 캐싱"""
    if filename in data_cache:
        return data_cache[filename]
    
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_cache[filename] = data
            return data
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

@app.route('/api/national/sido')
def get_sido_list():
    """시도 목록 조회"""
    data = load_json_file('sgis_national_regions.json')
    if data and 'sido' in data:
        return jsonify(data['sido'])
    return jsonify([])

@app.route('/api/national/sido/<sido_code>')
def get_sido_detail(sido_code):
    """시도 상세 정보"""
    data = load_json_file('sgis_national_regions.json')
    if data and 'sido' in data:
        for sido in data['sido']:
            if sido.get('sido_cd') == sido_code:
                return jsonify(sido)
    return jsonify({})

@app.route('/api/national/sigungu/<sigungu_code>')
def get_sigungu_detail(sigungu_code):
    """시군구 상세 정보"""
    data = load_json_file('sgis_national_regions.json')
    if data and 'sigungu' in data:
        for sigungu in data['sigungu']:
            if sigungu.get('sigungu_cd') == sigungu_code:
                return jsonify(sigungu)
    return jsonify({})

@app.route('/api/national/emdong/<emdong_code>')
def get_emdong_detail(emdong_code):
    """읍면동 상세 정보"""
    year = request.args.get('year', '2023')
    
    # 멀티 year 데이터
    multiyear_data = load_json_file('sgis_enhanced_multiyear_stats.json')
    if multiyear_data and emdong_code in multiyear_data:
        emdong_data = multiyear_data[emdong_code]
        if 'years' in emdong_data and year in emdong_data['years']:
            return jsonify(emdong_data['years'][year])
    
    return jsonify({})

@app.route('/api/regions')
def get_regions():
    """전체 지역 목록"""
    data = load_json_file('sgis_national_regions.json')
    return jsonify(data or {})

@app.route('/api/years')
def get_available_years():
    """사용 가능한 연도 목록"""
    return jsonify({
        "years": ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    })

@app.route('/api/politicians/emdong/<emdong_code>')
def get_politicians(emdong_code):
    """읍면동의 정치인 정보"""
    # 국회의원 데이터
    assembly_data = load_json_file('assembly_by_region.json')
    
    # 지방 정치인 데이터
    local_data = load_json_file('local_politicians_lda_analysis.json')
    
    politicians = []
    
    # 데이터 구조에 맞게 정치인 추출
    # (실제 데이터 구조에 맞게 수정 필요)
    
    return jsonify(politicians)

@app.route('/api/network/assembly')
def get_assembly_network():
    """국회의원 네트워크 데이터"""
    data = load_json_file('assembly_network_graph.json')
    return jsonify(data or {})

@app.route('/api/search')
def search():
    """검색 API"""
    query = request.args.get('q', '')
    # 간단한 검색 구현
    return jsonify({"results": []})

# Vercel serverless function handler
def handler(request):
    return app(request.environ, start_response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

