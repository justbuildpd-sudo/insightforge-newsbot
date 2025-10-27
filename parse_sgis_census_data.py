#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS 전국 동별 데이터 파서
census 폴더의 SGIS 데이터를 파싱하여 대시보드용 데이터로 변환
"""

import os
import json
from pathlib import Path
import re

class SGISCensusParser:
    def __init__(self, census_dir="/Users/hopidad/Desktop/workspace/census"):
        self.census_dir = Path(census_dir)
        self.data = {}
        
    def parse_population_data(self):
        """인구 데이터 파싱"""
        print("📊 SGIS 전국 동별 인구 데이터 파싱 중...")
        
        # 2023년 총인구 데이터 파싱
        population_file = self.census_dir / "(행정구역)2024년기준_2023년_인구총괄(총인구).txt"
        if population_file.exists():
            population_data = {}
            
            with open(population_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('^')
                    if len(parts) >= 4:
                        year = parts[0]
                        region_code = parts[1]
                        data_type = parts[2]
                        population = int(parts[3])
                        
                        # 행정구역 코드를 지역명으로 변환
                        region_name = self.convert_region_code_to_name(region_code)
                        if region_name:
                            population_data[region_name] = {
                                'population': population,
                                'year': year,
                                'region_code': region_code
                            }
            
            self.data['population'] = population_data
            print(f"✅ 인구 데이터 파싱 완료: {len(population_data)}개 지역")
        
        return self.data.get('population', {})
    
    def parse_density_data(self):
        """인구밀도 데이터 파싱"""
        print("📊 SGIS 전국 동별 인구밀도 데이터 파싱 중...")
        
        density_file = self.census_dir / "(행정구역)2024년기준_2023년_인구총괄(인구밀도).txt"
        if density_file.exists():
            density_data = {}
            
            with open(density_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('^')
                    if len(parts) >= 4:
                        year = parts[0]
                        region_code = parts[1]
                        data_type = parts[2]
                        density = float(parts[3])
                        
                        region_name = self.convert_region_code_to_name(region_code)
                        if region_name:
                            if region_name not in self.data:
                                self.data[region_name] = {}
                            self.data[region_name]['density'] = density
            
            print(f"✅ 인구밀도 데이터 파싱 완료")
        
        return self.data
    
    def parse_age_data(self):
        """평균나이 데이터 파싱"""
        print("📊 SGIS 전국 동별 평균나이 데이터 파싱 중...")
        
        age_file = self.census_dir / "(행정구역)2024년기준_2023년_인구총괄(평균나이).txt"
        if age_file.exists():
            with open(age_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('^')
                    if len(parts) >= 4:
                        year = parts[0]
                        region_code = parts[1]
                        data_type = parts[2]
                        avg_age = float(parts[3])
                        
                        region_name = self.convert_region_code_to_name(region_code)
                        if region_name:
                            if region_name not in self.data:
                                self.data[region_name] = {}
                            self.data[region_name]['avg_age'] = avg_age
            
            print(f"✅ 평균나이 데이터 파싱 완료")
        
        return self.data
    
    def convert_region_code_to_name(self, region_code):
        """행정구역 코드를 지역명으로 변환"""
        # 행정구역 코드 매핑 (일부 주요 코드)
        region_mapping = {
            # 서울특별시
            '11010530': '종로구 청운효자동',
            '11010540': '종로구 사직동',
            '11010550': '종로구 삼청동',
            '11010560': '종로구 부암동',
            '11010570': '종로구 평창동',
            '11010580': '종로구 무악동',
            '11010600': '종로구 교남동',
            '11010610': '종로구 가회동',
            '11010630': '종로구 종로1.2.3.4가동',
            '11010640': '종로구 종로5.6가동',
            '11010670': '종로구 이화동',
            '11010680': '종로구 혜화동',
            '11010690': '종로구 명륜3가동',
            '11010700': '종로구 창신동',
            '11010710': '종로구 숭인동',
            '11010720': '종로구 숭인2동',
            '11010730': '종로구 이화동',
            
            # 중구
            '11020520': '중구 소공동',
            '11020540': '중구 회현동',
            '11020550': '중구 명동',
            '11020560': '중구 필동',
            '11020570': '중구 장충동',
            '11020580': '중구 광희동',
            '11020600': '중구 을지로동',
            '11020610': '중구 신당동',
            '11020620': '중구 다산동',
            '11020630': '중구 약수동',
            '11020640': '중구 청구동',
            '11020650': '중구 신당5동',
            '11020660': '중구 동화동',
            '11020670': '중구 황학동',
            '11020680': '중구 중림동',
            
            # 용산구
            '11030510': '용산구 후암동',
            '11030520': '용산구 용산2가동',
            '11030530': '용산구 남영동',
            '11030540': '용산구 청파동',
            '11030550': '용산구 원효로1동',
            '11030560': '용산구 원효로2동',
            '11030570': '용산구 효창동',
            '11030580': '용산구 용문동',
            '11030590': '용산구 한강로동',
            '11030600': '용산구 이촌1동',
            '11030610': '용산구 이촌2동',
            '11030620': '용산구 이태원1동',
            '11030630': '용산구 이태원2동',
            '11030640': '용산구 한남동',
            '11030650': '용산구 서빙고동',
            '11030660': '용산구 보광동',
            
            # 성동구
            '11040510': '성동구 왕십리도선동',
            '11040520': '성동구 마장동',
            '11040530': '성동구 사근동',
            '11040540': '성동구 행당1동',
            '11040550': '성동구 행당2동',
            '11040560': '성동구 응봉동',
            '11040570': '성동구 금호1가동',
            '11040580': '성동구 금호2.3가동',
            '11040590': '성동구 금호4가동',
            '11040600': '성동구 옥수동',
            '11040610': '성동구 성수1가1동',
            '11040620': '성동구 성수1가2동',
            '11040630': '성동구 성수2가1동',
            '11040640': '성동구 성수2가3동',
            '11040650': '성동구 송정동',
            '11040660': '성동구 용답동',
            
            # 광진구
            '11050510': '광진구 중곡1동',
            '11050520': '광진구 중곡2동',
            '11050530': '광진구 중곡3동',
            '11050540': '광진구 중곡4동',
            '11050550': '광진구 능동',
            '11050560': '광진구 구의1동',
            '11050570': '광진구 구의2동',
            '11050580': '광진구 구의3동',
            '11050590': '광진구 광장동',
            '11050600': '광진구 자양1동',
            '11050610': '광진구 자양2동',
            '11050620': '광진구 자양3동',
            '11050630': '광진구 자양4동',
            '11050640': '광진구 화양동',
            
            # 강남구
            '11060510': '강남구 신사동',
            '11060520': '강남구 논현1동',
            '11060530': '강남구 논현2동',
            '11060540': '강남구 압구정동',
            '11060550': '강남구 청담동',
            '11060560': '강남구 삼성1동',
            '11060570': '강남구 삼성2동',
            '11060580': '강남구 대치1동',
            '11060590': '강남구 대치2동',
            '11060600': '강남구 대치4동',
            '11060610': '강남구 역삼1동',
            '11060620': '강남구 역삼2동',
            '11060630': '강남구 도곡1동',
            '11060640': '강남구 도곡2동',
            '11060650': '강남구 개포1동',
            '11060660': '강남구 개포2동',
            '11060670': '강남구 개포4동',
            '11060680': '강남구 일원1동',
            '11060690': '강남구 일원본동',
            '11060700': '강남구 수서동',
            '11060710': '강남구 세곡동',
        }
        
        return region_mapping.get(region_code, None)
    
    def parse_all_data(self):
        """모든 SGIS 데이터 파싱"""
        print("🚀 SGIS 전국 동별 데이터 파싱 시작...")
        
        try:
            # 각 데이터 타입별로 파싱
            self.parse_population_data()
            self.parse_density_data()
            self.parse_age_data()
            
            # 통계 정보 생성
            total_regions = len(self.data)
            print(f"\n📊 SGIS 전국 동별 데이터 파싱 완료!")
            print(f"   - 총 지역 수: {total_regions:,}개")
            print(f"   - 인구 데이터: {len([r for r in self.data.values() if 'population' in r])}개")
            print(f"   - 인구밀도 데이터: {len([r for r in self.data.values() if 'density' in r])}개")
            print(f"   - 평균나이 데이터: {len([r for r in self.data.values() if 'avg_age' in r])}개")
            
            return self.data
            
        except Exception as e:
            print(f"❌ SGIS 데이터 파싱 실패: {e}")
            return None
    
    def save_to_json(self, output_file="sgis_census_data.json"):
        """파싱된 데이터를 JSON 파일로 저장"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ SGIS 데이터 저장 완료: {output_file}")
            return True
        except Exception as e:
            print(f"❌ SGIS 데이터 저장 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    print("=== SGIS 전국 동별 데이터 파서 시작 ===")
    
    # SGIS 데이터 파서 초기화
    parser = SGISCensusParser()
    
    # 모든 데이터 파싱
    data = parser.parse_all_data()
    
    if data:
        # JSON 파일로 저장
        parser.save_to_json("sgis_census_data.json")
        
        # 대시보드용 데이터 생성
        create_dashboard_census_data(data)
        
        print("\n🎉 SGIS 전국 동별 데이터 파싱 및 처리 완료!")
    else:
        print("\n❌ SGIS 데이터 파싱 실패")

def create_dashboard_census_data(sgis_data):
    """대시보드용 SGIS 데이터 생성"""
    print("\n📊 대시보드용 SGIS 데이터 생성 중...")
    
    dashboard_data = {
        "population": {},
        "density": {},
        "age": {}
    }
    
    # 지역별 데이터 처리
    for region_name, region_data in sgis_data.items():
        if 'population' in region_data:
            dashboard_data['population'][region_name] = {
                'population': region_data['population'],
                'year': region_data.get('year', '2023')
            }
        
        if 'density' in region_data:
            dashboard_data['density'][region_name] = {
                'density': region_data['density'],
                'year': region_data.get('year', '2023')
            }
        
        if 'avg_age' in region_data:
            dashboard_data['age'][region_name] = {
                'avg_age': region_data['avg_age'],
                'year': region_data.get('year', '2023')
            }
    
    # 대시보드용 데이터 저장
    with open('dashboard_sgis_census_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 대시보드용 SGIS 데이터 생성 완료: dashboard_sgis_census_data.json")
    print(f"인구 데이터: {len(dashboard_data['population'])}개 지역")
    print(f"인구밀도 데이터: {len(dashboard_data['density'])}개 지역")
    print(f"평균나이 데이터: {len(dashboard_data['age'])}개 지역")

if __name__ == "__main__":
    main()
