#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메인 선거 데이터 처리 스크립트
공공데이터포털 API → 행정동 매핑 → LDA 상관관계 → 영향력 분석 → Vercel API 생성
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('election_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """메인 실행 함수"""
    logger.info("=== 선거 데이터 처리 파이프라인 시작 ===")
    
    try:
        # 1단계: 공공데이터포털 API로 선거 데이터 수집
        logger.info("1단계: 공공데이터포털 API로 선거 데이터 수집")
        from election_data_collector import ElectionDataCollector
        
        api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
        collector = ElectionDataCollector(api_key)
        
        logger.info("선거 데이터 수집 중...")
        all_elections_data = collector.collect_all_elections()
        
        logger.info("시계열 분석 데이터 생성 중...")
        timeline_data = collector.create_timeline_analysis(all_elections_data)
        
        logger.info("Vercel 최적화 데이터 생성 중...")
        vercel_data = collector.create_vercel_optimized_data(timeline_data)
        
        election_output_file = collector.save_vercel_data(vercel_data)
        logger.info(f"✅ 선거 데이터 수집 완료: {election_output_file}")
        
        # 2단계: 행정동 단위 매핑
        logger.info("2단계: 행정동 단위 매핑")
        from region_election_mapper import RegionElectionMapper
        
        mapper = RegionElectionMapper()
        dong_mapping = mapper.map_elections_to_dong(vercel_data)
        vercel_dong_data = mapper.create_vercel_optimized_structure(dong_mapping)
        dong_output_file = mapper.save_vercel_data(vercel_dong_data)
        logger.info(f"✅ 행정동 매핑 완료: {dong_output_file}")
        
        # 3단계: 영향력 분석
        logger.info("3단계: 영향력 분석")
        from influence_analyzer import InfluenceAnalyzer
        
        analyzer = InfluenceAnalyzer()
        comprehensive_analysis = analyzer.create_comprehensive_analysis(vercel_dong_data)
        influence_output_file = analyzer.save_analysis_results(comprehensive_analysis)
        logger.info(f"✅ 영향력 분석 완료: {influence_output_file}")
        
        # 4단계: Vercel API 엔드포인트 생성
        logger.info("4단계: Vercel API 엔드포인트 생성")
        from vercel_api_endpoints import VercelAPIEndpoints
        
        api_creator = VercelAPIEndpoints()
        created_files = api_creator.create_all_apis(vercel_dong_data, comprehensive_analysis)
        logger.info(f"✅ Vercel API 생성 완료: {len(created_files)}개 파일")
        
        # 5단계: 배포 준비 완료
        logger.info("5단계: 배포 준비 완료")
        self.create_deployment_summary(created_files)
        
        logger.info("=== 선거 데이터 처리 파이프라인 완료 ===")
        
    except Exception as e:
        logger.error(f"❌ 처리 중 오류 발생: {e}")
        raise

def create_deployment_summary(created_files: List[str]) -> str:
    """배포 요약 생성"""
    summary = {
        "deployment_info": {
            "created_at": datetime.now().isoformat(),
            "total_files": len(created_files),
            "status": "ready_for_deployment"
        },
        "created_files": created_files,
        "api_endpoints": [
            "/api/dong-list",
            "/api/dong-elections", 
            "/api/timeline-analysis",
            "/api/lda-correlation",
            "/api/influence-analysis"
        ],
        "deployment_commands": [
            "npm install",
            "npm run dev  # 개발 서버",
            "npm run deploy  # Vercel 배포"
        ],
        "data_files": [
            "election_data/vercel_election_data.json",
            "vercel_optimized_data/dong_election_analysis.json",
            "influence_analysis/comprehensive_influence_analysis.json"
        ]
    }
    
    summary_file = "deployment_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    logger.info(f"배포 요약 생성 완료: {summary_file}")
    return summary_file

if __name__ == "__main__":
    main()
