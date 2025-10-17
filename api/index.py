from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 데이터 디렉토리 - Vercel 환경 고려
import sys
# Vercel에서는 현재 작업 디렉토리가 프로젝트 루트
DATA_DIR = Path.cwd() / "insightforge-web" / "data"
if not DATA_DIR.exists():
    # 대안 경로들 시도
    DATA_DIR = Path(__file__).parent.parent / "insightforge-web" / "data"
    if not DATA_DIR.exists():
        DATA_DIR = Path("/var/task/insightforge-web/data")

print(f"📁 데이터 디렉토리: {DATA_DIR}", file=sys.stderr)
print(f"📁 존재 여부: {DATA_DIR.exists()}", file=sys.stderr)
if DATA_DIR.exists():
    print(f"📁 파일 목록: {list(DATA_DIR.glob('*.json'))[:5]}", file=sys.stderr)

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
    if data and 'regions' in data:
        # regions 객체를 배열로 변환
        sido_list = []
        for sido_code, sido_data in data['regions'].items():
            sido_list.append({
                'sido_cd': sido_code,
                'sido_nm': sido_data.get('sido_name', ''),
                'sigungu_count': len(sido_data.get('sigungu_list', []))
            })
        return jsonify(sido_list)
    return jsonify([])

@app.route('/api/national/sido/<sido_code>')
def get_sido_detail(sido_code):
    """시도 상세 정보"""
    data = load_json_file('sgis_national_regions.json')
    if data and 'regions' in data and sido_code in data['regions']:
        return jsonify(data['regions'][sido_code])
    return jsonify({})

@app.route('/api/national/sigungu/<sigungu_code>')
def get_sigungu_detail(sigungu_code):
    """시군구 상세 정보"""
    data = load_json_file('sgis_national_regions.json')
    if data and 'regions' in data:
        # 모든 시도에서 시군구 찾기
        for sido_code, sido_data in data['regions'].items():
            for sigungu in sido_data.get('sigungu_list', []):
                if sigungu.get('sigungu_code') == sigungu_code:
                    return jsonify(sigungu)
    return jsonify({})

@app.route('/api/national/sigungu/<sigungu_code>/detail')
def get_sigungu_detail_with_stats(sigungu_code):
    """시군구 상세 정보 (통계 포함)"""
    # 기본 정보
    basic_data = get_sigungu_detail(sigungu_code).get_json()
    
    # 통계 데이터 추가 (있다면)
    stats_data = load_json_file('sgis_comprehensive_stats.json') or {}
    commercial_data = load_json_file('sgis_commercial_stats.json') or {}
    tech_data = load_json_file('sgis_tech_stats.json') or {}
    
    result = {
        **basic_data,
        'stats': stats_data.get(sigungu_code, {}),
        'commercial': commercial_data.get(sigungu_code, {}),
        'tech': tech_data.get(sigungu_code, {})
    }
    
    return jsonify(result)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

