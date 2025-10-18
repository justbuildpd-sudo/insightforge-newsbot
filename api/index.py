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
    """시군구 상세 정보 (동별 데이터 합산)"""
    # 기본 정보
    basic_data = get_sigungu_detail(sigungu_code).get_json()
    
    # 코드 매핑
    code_mapping = load_json_file('code_mapping.json') or {}
    mapping_dict = code_mapping.get('mapping', {})
    
    # 주민등록 인구 데이터
    jumin_data = load_json_file('jumin_population_2025.json') or {}
    
    # comprehensive stats
    comprehensive_stats = load_json_file('sgis_comprehensive_stats.json') or {}
    
    # 해당 시군구의 모든 읍면동 합산
    total_household = 0
    total_population = 0
    total_male = 0
    total_female = 0
    total_house = 0
    total_company = 0
    total_worker = 0
    emdong_count = 0
    
    # 읍면동 목록에서 각각 집계
    if 'emdong_list' in basic_data:
        for emdong in basic_data['emdong_list']:
            emdong_code = emdong.get('emdong_code')
            emdong_count += 1
            
            # 주민등록 데이터 (코드 매핑 사용)
            if emdong_code in mapping_dict:
                jumin_code = mapping_dict[emdong_code]['jumin_code']
                if 'regions' in jumin_data and jumin_code in jumin_data['regions']:
                    jumin_info = jumin_data['regions'][jumin_code]
                    total_household += jumin_info.get('household_cnt', 0)
                    total_population += jumin_info.get('total_population', 0)
                    total_male += jumin_info.get('male_population', 0)
                    total_female += jumin_info.get('female_population', 0)
            
            # SGIS 데이터 (사업체, 주택)
            if 'regions' in comprehensive_stats and emdong_code in comprehensive_stats['regions']:
                emdong_stats = comprehensive_stats['regions'][emdong_code]
                house = emdong_stats.get('house', {})
                company = emdong_stats.get('company', {})
                total_house += house.get('house_cnt', 0)
                total_company += company.get('corp_cnt', 0)
                total_worker += company.get('tot_worker', 0)
    
    result = {
        **basic_data,
        'sigungu_code': sigungu_code,
        'household': {
            'household_cnt': total_household,
            'family_member_cnt': total_population,
            'avg_family_member_cnt': total_population / total_household if total_household > 0 else 0,
            'male_population': total_male,
            'female_population': total_female
        },
        'house': {
            'house_cnt': total_house  # 실제 값 사용
        },
        'company': {
            'corp_cnt': total_company,
            'tot_worker': total_worker  # 실제 값 사용
        },
        'data_source': '주민등록 2025-09 (인구/가구 합산)',
        'data_year': '2025-09',
        'emdong_count': emdong_count
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

@app.route('/api/emdong/<emdong_code>/enhanced')
def get_emdong_enhanced(emdong_code):
    """읍면동 향상된 상세 정보 - 주민등록 인구 우선 사용"""
    year = request.args.get('year', '2023')
    
    # 기본 정보
    base_data = {}
    regions_data = load_json_file('sgis_national_regions.json')
    if regions_data and 'regions' in regions_data:
        for sido_code, sido_data in regions_data['regions'].items():
            for sigungu in sido_data.get('sigungu_list', []):
                for emdong in sigungu.get('emdong_list', []):
                    if emdong.get('emdong_code') == emdong_code:
                        base_data = emdong
                        break
    
    # comprehensive stats에서 읍면동 데이터 (사업체, 주택 등)
    comprehensive_stats = load_json_file('sgis_comprehensive_stats.json') or {}
    emdong_stats = {}
    if 'regions' in comprehensive_stats and emdong_code in comprehensive_stats['regions']:
        emdong_stats = comprehensive_stats['regions'][emdong_code]
    
    # 코드 매핑으로 주민등록 코드 찾기
    code_mapping = load_json_file('code_mapping.json') or {}
    jumin_code = None
    if 'mapping' in code_mapping and emdong_code in code_mapping['mapping']:
        jumin_code = code_mapping['mapping'][emdong_code]['jumin_code']
    
    # 주민등록 인구 데이터 (가장 정확)
    jumin_data = load_json_file('jumin_population_2025.json') or {}
    jumin_info = {}
    if jumin_code and 'regions' in jumin_data and jumin_code in jumin_data['regions']:
        jumin_info = jumin_data['regions'][jumin_code]
        
    # 인구증감 데이터
    growth_data = load_json_file('jumin_growth_2025.json') or {}
    growth_info = {}
    if jumin_code and 'regions' in growth_data and jumin_code in growth_data['regions']:
        growth_info = growth_data['regions'][jumin_code]
    
    # 멀티 year 통계 데이터
    multiyear_data = load_json_file('sgis_enhanced_multiyear_stats.json') or {}
    year_stats = {}
    if emdong_code in multiyear_data:
        emdong_data = multiyear_data[emdong_code]
        if 'years' in emdong_data and year in emdong_data['years']:
            year_stats = emdong_data['years'][year]
    
    # 데이터 병합 - 주민등록 데이터 우선
    result = {
        **base_data,
        **emdong_stats
    }
    
    # 주민등록 데이터로 가구/인구 덮어쓰기 (더 정확함)
    if jumin_info:
        result['household'] = {
            'household_cnt': jumin_info.get('household_cnt', 0),
            'family_member_cnt': jumin_info.get('total_population', 0),
            'avg_family_member_cnt': jumin_info.get('avg_household_size', 0),
            'male_population': jumin_info.get('male_population', 0),
            'female_population': jumin_info.get('female_population', 0)
        }
        result['data_source'] = '주민등록 2025-09'
        result['data_year'] = '2025-09'
    
    # 인구증감 데이터 추가
    if growth_info and 'data' in growth_info:
        growth_cols = growth_info['data']
        result['population_growth'] = {
            'prev_month': growth_cols.get('2025년09월_전월인구수_계', 0),
            'curr_month': growth_cols.get('2025년09월_당월인구수_계', 0),
            'change': growth_cols.get('2025년09월_인구증감_계', 0),
            'male_change': growth_cols.get('2025년09월_인구증감_남자인구수', 0),
            'female_change': growth_cols.get('2025년09월_인구증감_여자인구수', 0)
        }
    
    return jsonify(result)

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

