#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGIS 데이터 로더
국토교통부 통계지리정보서비스(SGIS) 데이터를 통합하여 로드하는 스크립트
"""

import pandas as pd
import json
import os
from pathlib import Path
import glob

class SGISDataLoader:
    def __init__(self, gis_dir="/Users/hopidad/Desktop/workspace/gis"):
        self.gis_dir = Path(gis_dir)
        self.data = {}
        
    def load_human_data(self):
        """인구 관련 데이터 로드"""
        print("📊 인구 데이터 로딩 중...")
        human_dir = self.gis_dir / "human"
        
        human_data = {}
        
        # 인구 밀도 데이터
        popl_dn_file = human_dir / "tb_pda_st_epmndn_yrly_popl_dn.csv"
        if popl_dn_file.exists():
            try:
                df = pd.read_csv(popl_dn_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(popl_dn_file, encoding='cp949')
                except UnicodeDecodeError:
                    df = pd.read_csv(popl_dn_file, encoding='euc-kr')
            human_data['population_density'] = df.to_dict('records')
            print(f"✅ 인구 밀도 데이터 로드: {len(df)} 행")
        
        # 인구 성장률 데이터
        popl_growth_file = human_dir / "tb_pda_st_epmndn_yrly_popl_growth_rt.csv"
        if popl_growth_file.exists():
            try:
                df = pd.read_csv(popl_growth_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(popl_growth_file, encoding='cp949')
                except UnicodeDecodeError:
                    df = pd.read_csv(popl_growth_file, encoding='euc-kr')
            human_data['population_growth'] = df.to_dict('records')
            print(f"✅ 인구 성장률 데이터 로드: {len(df)} 행")
        
        # 세대수 데이터
        hshld_file = human_dir / "tb_pda_st_epmndn_yrly_rr_hshld_popl_cnt.csv"
        if hshld_file.exists():
            try:
                df = pd.read_csv(hshld_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(hshld_file, encoding='cp949')
                except UnicodeDecodeError:
                    df = pd.read_csv(hshld_file, encoding='euc-kr')
            human_data['household_count'] = df.to_dict('records')
            print(f"✅ 세대수 데이터 로드: {len(df)} 행")
        
        # 평균 연령 데이터
        avg_age_file = human_dir / "tb_pda_st_sex_epmndn_yrly_avrg_age.csv"
        if avg_age_file.exists():
            try:
                df = pd.read_csv(avg_age_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(avg_age_file, encoding='cp949')
                except UnicodeDecodeError:
                    df = pd.read_csv(avg_age_file, encoding='euc-kr')
            human_data['average_age'] = df.to_dict('records')
            print(f"✅ 평균 연령 데이터 로드: {len(df)} 행")
        
        # 중위 연령 데이터
        median_age_file = human_dir / "tb_pda_st_sex_epmndn_yrly_median_age.csv"
        if median_age_file.exists():
            try:
                df = pd.read_csv(median_age_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(median_age_file, encoding='cp949')
                except UnicodeDecodeError:
                    df = pd.read_csv(median_age_file, encoding='euc-kr')
            human_data['median_age'] = df.to_dict('records')
            print(f"✅ 중위 연령 데이터 로드: {len(df)} 행")
        
        return human_data
    
    def load_land_data(self):
        """부동산 관련 데이터 로드"""
        print("🏠 부동산 데이터 로딩 중...")
        land_dir = self.gis_dir / "land"
        
        land_data = {}
        
        # 전월세가 데이터 (매매)
        jeonse_file = land_dir / "주택가격지수(전세)_20251003223737.xlsx"
        if jeonse_file.exists():
            df = pd.read_excel(jeonse_file)
            land_data['jeonse_price'] = df.to_dict('records')
            print(f"✅ 전세가 데이터 로드: {len(df)} 행")
        
        # 주택가격지수 데이터 (매매)
        price_file = land_dir / "주택가격지수(매매)_20251003223641.xlsx"
        if price_file.exists():
            df = pd.read_excel(price_file)
            land_data['house_price'] = df.to_dict('records')
            print(f"✅ 주택가격지수 데이터 로드: {len(df)} 행")
        
        # 아파트 매매가격 데이터
        apt_file = land_dir / "아파트매매가격+현황_20251003221221.xlsx"
        if apt_file.exists():
            df = pd.read_excel(apt_file)
            land_data['apartment_price'] = df.to_dict('records')
            print(f"✅ 아파트 매매가격 데이터 로드: {len(df)} 행")
        
        # 전월세가 데이터 (월세)
        monthly_file = land_dir / "미거주+주택(빈집)+현황(구별)_20251003223938.xlsx"
        if monthly_file.exists():
            df = pd.read_excel(monthly_file)
            land_data['monthly_rent'] = df.to_dict('records')
            print(f"✅ 월세 데이터 로드: {len(df)} 행")
        
        return land_data
    
    def load_gdp_data(self):
        """경제 관련 데이터 로드"""
        print("💰 경제 데이터 로딩 중...")
        gdp_dir = self.gis_dir / "GDP"
        
        gdp_data = {}
        
        # 지역내총생산 데이터
        gdp_file = gdp_dir / "자치구별+경제활동별+지역내총생산2015년+기준_20251004023554.xlsx"
        if gdp_file.exists():
            df = pd.read_excel(gdp_file)
            gdp_data['regional_gdp'] = df.to_dict('records')
            print(f"✅ 지역내총생산 데이터 로드: {len(df)} 행")
        
        return gdp_data
    
    def load_safety_data(self):
        """안전 관련 데이터 로드"""
        print("🛡️ 안전 데이터 로딩 중...")
        safe_dir = self.gis_dir / "safe"
        
        safety_data = {}
        
        # 건강보험 데이터
        health_files = list(safe_dir.glob("*건강보험*.xlsx"))
        for file in health_files:
            if file.exists():
                df = pd.read_excel(file)
                safety_data[f'health_insurance_{file.stem}'] = df.to_dict('records')
                print(f"✅ 건강보험 데이터 로드: {file.name} - {len(df)} 행")
        
        # 노인여가복지시설 데이터
        welfare_file = safe_dir / "노인여가복지시설(동별)_20251002134427.xlsx"
        if welfare_file.exists():
            df = pd.read_excel(welfare_file)
            safety_data['elderly_welfare'] = df.to_dict('records')
            print(f"✅ 노인여가복지시설 데이터 로드: {len(df)} 행")
        
        # 독거노인 데이터
        elderly_file = safe_dir / "독거노인+현황(연령별_동별)_20251002134046.xlsx"
        if elderly_file.exists():
            df = pd.read_excel(elderly_file)
            safety_data['elderly_living_alone'] = df.to_dict('records')
            print(f"✅ 독거노인 데이터 로드: {len(df)} 행")
        
        return safety_data
    
    def load_all_data(self):
        """모든 SGIS 데이터 로드"""
        print("🚀 SGIS 데이터 통합 로딩 시작...")
        
        try:
            # 각 카테고리별 데이터 로드
            self.data['human'] = self.load_human_data()
            self.data['land'] = self.load_land_data()
            self.data['gdp'] = self.load_gdp_data()
            self.data['safety'] = self.load_safety_data()
            
            # 통계 정보 생성
            total_records = sum(
                len(category_data) 
                for category in self.data.values() 
                for category_data in category.values()
            )
            
            print(f"\n📊 SGIS 데이터 로딩 완료!")
            print(f"   - 총 레코드 수: {total_records:,}개")
            print(f"   - 인구 데이터: {len(self.data['human'])}개 파일")
            print(f"   - 부동산 데이터: {len(self.data['land'])}개 파일")
            print(f"   - 경제 데이터: {len(self.data['gdp'])}개 파일")
            print(f"   - 안전 데이터: {len(self.data['safety'])}개 파일")
            
            return self.data
            
        except Exception as e:
            print(f"❌ SGIS 데이터 로딩 실패: {e}")
            return None
    
    def save_to_json(self, output_file="sgis_data.json"):
        """로드된 데이터를 JSON 파일로 저장"""
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
    print("=== SGIS 데이터 로더 시작 ===")
    
    # SGIS 데이터 로더 초기화
    loader = SGISDataLoader()
    
    # 모든 데이터 로드
    data = loader.load_all_data()
    
    if data:
        # JSON 파일로 저장
        loader.save_to_json("sgis_data.json")
        
        # 대시보드용 데이터 생성
        create_dashboard_data(data)
        
        print("\n🎉 SGIS 데이터 로딩 및 처리 완료!")
    else:
        print("\n❌ SGIS 데이터 로딩 실패")

def create_dashboard_data(sgis_data):
    """대시보드용 데이터 생성"""
    print("\n📊 대시보드용 데이터 생성 중...")
    
    dashboard_data = {
        "population": {},
        "real_estate": {},
        "economy": {},
        "safety": {}
    }
    
    # 인구 데이터 처리
    if 'human' in sgis_data:
        human_data = sgis_data['human']
        print(f"인구 데이터 키: {list(human_data.keys())}")
        
        # 인구 밀도 데이터 처리
        if 'population_density' in human_data:
            print(f"인구 밀도 데이터 샘플: {human_data['population_density'][:2]}")
            for record in human_data['population_density']:
                # 컬럼명 확인
                columns = list(record.keys())
                print(f"인구 밀도 컬럼: {columns}")
                
                # 지역명과 인구밀도 찾기
                region_key = None
                density_key = None
                
                for col in columns:
                    if '지역' in col or '시도' in col or '시군구' in col:
                        region_key = col
                    if '밀도' in col or '인구' in col:
                        density_key = col
                
                if region_key and density_key:
                    region = record.get(region_key, '')
                    density = record.get(density_key, 0)
                    if region and density:
                        dashboard_data['population'][region] = {
                            'density': density,
                            'year': record.get('년도', 2024)
                        }
        
        # 평균 연령 데이터 처리
        if 'average_age' in human_data:
            print(f"평균 연령 데이터 샘플: {human_data['average_age'][:2]}")
            for record in human_data['average_age']:
                columns = list(record.keys())
                print(f"평균 연령 컬럼: {columns}")
                
                region_key = None
                age_key = None
                
                for col in columns:
                    if '지역' in col or '시도' in col or '시군구' in col:
                        region_key = col
                    if '연령' in col or '나이' in col:
                        age_key = col
                
                if region_key and age_key:
                    region = record.get(region_key, '')
                    age = record.get(age_key, 0)
                    if region and age:
                        if region not in dashboard_data['population']:
                            dashboard_data['population'][region] = {}
                        dashboard_data['population'][region]['average_age'] = age
    
    # 경제 데이터 처리
    if 'gdp' in sgis_data:
        gdp_data = sgis_data['gdp']
        print(f"경제 데이터 키: {list(gdp_data.keys())}")
        
        if 'regional_gdp' in gdp_data:
            print(f"지역내총생산 데이터 샘플: {gdp_data['regional_gdp'][:2]}")
            for record in gdp_data['regional_gdp']:
                columns = list(record.keys())
                print(f"GDP 컬럼: {columns}")
                
                region_key = None
                gdp_key = None
                
                for col in columns:
                    if '지역' in col or '시도' in col or '시군구' in col:
                        region_key = col
                    if '총생산' in col or 'GDP' in col:
                        gdp_key = col
                
                if region_key and gdp_key:
                    region = record.get(region_key, '')
                    gdp = record.get(gdp_key, 0)
                    if region and gdp:
                        dashboard_data['economy'][region] = {
                            'gdp': gdp,
                            'year': record.get('년도', 2024)
                        }
    
    # 대시보드용 데이터 저장
    with open('dashboard_sgis_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 대시보드용 SGIS 데이터 생성 완료: dashboard_sgis_data.json")
    print(f"인구 데이터: {len(dashboard_data['population'])}개 지역")
    print(f"경제 데이터: {len(dashboard_data['economy'])}개 지역")

if __name__ == "__main__":
    main()
