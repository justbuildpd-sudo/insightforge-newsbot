#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
행정동 단위 선거 데이터 매핑 및 LDA 시계열 포인트 매칭
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
import os

logger = logging.getLogger(__name__)

class RegionElectionMapper:
    def __init__(self):
        self.data_dir = "election_data"
        self.output_dir = "vercel_optimized_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 행정동 코드 매핑 (실제 데이터 기반)
        self.dong_mapping = {
            "서울특별시": {
                "종로구": {
                    "청운효자동": "11110101", "사직동": "11110102", "삼청동": "11110103",
                    "부암동": "11110104", "평창동": "11110105", "무악동": "11110106",
                    "교남동": "11110107", "가회동": "11110108", "종로1.2.3.4가동": "11110109",
                    "종로5.6가동": "11110110", "이화동": "11110111", "혜화동": "11110112",
                    "명륜3가동": "11110113", "창신동": "11110114", "숭인동": "11110115"
                },
                "중구": {
                    "소공동": "11140101", "회현동": "11140102", "명동": "11140103",
                    "필동": "11140104", "장충동": "11140105", "광희동": "11140106",
                    "을지로동": "11140107", "신당동": "11140108", "다산동": "11140109",
                    "약수동": "11140110", "청구동": "11140111", "신당5동": "11140112",
                    "동화동": "11140113", "황학동": "11140114", "중림동": "11140115"
                },
                "용산구": {
                    "후암동": "11170101", "용산2가동": "11170102", "남영동": "11170103",
                    "청파동": "11170104", "원효로1동": "11170105", "원효로2동": "11170106",
                    "효창동": "11170107", "용문동": "11170108", "한강로동": "11170109",
                    "이촌동": "11170110", "이태원동": "11170111", "한남동": "11170112",
                    "서빙고동": "11170113", "보광동": "11170114"
                }
            }
        }
        
        # LDA 시계열 포인트 매핑
        self.lda_timeline_points = {
            "2006": ["20060531"],  # 제4회 지방선거
            "2010": ["20100602"],  # 제5회 지방선거
            "2012": ["20120411", "20121219"],  # 제19대 국회의원선거, 제18대 대통령선거
            "2014": ["20140604"],  # 제6회 지방선거
            "2016": ["20160413"],  # 제20대 국회의원선거
            "2017": ["20170409"],  # 제19대 대통령선거
            "2018": ["20180613"],  # 제7회 지방선거
            "2020": ["20200415"],  # 제21대 국회의원선거
            "2022": ["20220309", "20220601"],  # 제20대 대통령선거, 제8회 지방선거
            "2024": ["20240410"]   # 제22대 국회의원선거
        }

    def load_election_data(self, file_path: str) -> Dict[str, Any]:
        """선거 데이터 로드"""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
        return {}

    def map_elections_to_dong(self, election_data: Dict[str, Any]) -> Dict[str, Any]:
        """선거 데이터를 행정동 단위로 매핑"""
        dong_election_mapping = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "mapping_type": "dong_election_mapping",
                "total_dongs": 0
            },
            "dong_elections": {},
            "timeline_analysis": {},
            "lda_correlation": {}
        }
        
        total_dongs = 0
        
        for election in election_data.get("elections", []):
            election_id = election["election_id"]
            election_info = election
            logger.info(f"매핑 중: {election_info['election_name']}")
            
            for region_name, region_data in election_info.get("regions", {}).items():
                if region_name in self.dong_mapping:
                    for gu_name, dong_list in self.dong_mapping[region_name].items():
                        for dong_name, dong_code in dong_list.items():
                            dong_key = f"{region_name}_{gu_name}_{dong_name}"
                            
                            if dong_key not in dong_election_mapping["dong_elections"]:
                                dong_election_mapping["dong_elections"][dong_key] = {
                                    "dong_code": dong_code,
                                    "dong_name": dong_name,
                                    "gu_name": gu_name,
                                    "sido_name": region_name,
                                    "elections": [],
                                    "candidate_history": [],
                                    "party_history": [],
                                    "demographic_analysis": {}
                                }
                                total_dongs += 1
                            
                            # 선거 정보 추가
                            election_entry = {
                                "election_id": election_id,
                                "election_name": election_info["election_name"],
                                "election_type": election_info["election_type"],
                                "date": election_id,
                                "candidates": region_data.get("candidates", []),
                                "candidate_count": region_data.get("candidate_count", 0),
                                "parties": region_data.get("parties", []),
                                "gender_distribution": region_data.get("gender_distribution", {}),
                                "age_distribution": region_data.get("age_distribution", {}),
                                "education_distribution": region_data.get("education_distribution", {}),
                                "career_analysis": region_data.get("career_analysis", {})
                            }
                            
                            dong_election_mapping["dong_elections"][dong_key]["elections"].append(election_entry)
                            
                            # 후보자 히스토리 업데이트
                            for candidate in region_data.get("candidates", []):
                                dong_election_mapping["dong_elections"][dong_key]["candidate_history"].append({
                                    "name": candidate.get("name", ""),
                                    "party": candidate.get("jdName", ""),
                                    "age": candidate.get("age", 0),
                                    "gender": candidate.get("gender", ""),
                                    "education": candidate.get("edu", ""),
                                    "career": candidate.get("career1", ""),
                                    "election_id": election_id
                                })
                            
                            # 정당 히스토리 업데이트
                            for party in region_data.get("parties", []):
                                if party not in [p["party"] for p in dong_election_mapping["dong_elections"][dong_key]["party_history"]]:
                                    dong_election_mapping["dong_elections"][dong_key]["party_history"].append({
                                        "party": party,
                                        "first_appearance": election_id,
                                        "election_count": 1
                                    })
                                else:
                                    for p in dong_election_mapping["dong_elections"][dong_key]["party_history"]:
                                        if p["party"] == party:
                                            p["election_count"] += 1
        
        dong_election_mapping["metadata"]["total_dongs"] = total_dongs
        
        # 시계열 분석 생성
        dong_election_mapping["timeline_analysis"] = self._create_timeline_analysis(dong_election_mapping["dong_elections"])
        
        # LDA 상관관계 분석
        dong_election_mapping["lda_correlation"] = self._create_lda_correlation(dong_election_mapping["dong_elections"])
        
        return dong_election_mapping

    def save_mapped_data(self, mapped_data: Dict[str, Any], filename: str = "election_data/mapped_election_data.json"):
        """매핑된 데이터를 JSON 파일로 저장"""
        import json
        import os
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mapped_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"✅ 매핑된 선거 데이터 저장 완료: {filename}")

    def _create_timeline_analysis(self, dong_elections: Dict[str, Any]) -> Dict[str, Any]:
        """시계열 분석 데이터 생성"""
        timeline_analysis = {
            "election_frequency": {},
            "party_evolution": {},
            "demographic_trends": {},
            "regional_patterns": {}
        }
        
        for dong_key, dong_data in dong_elections.items():
            # 선거 빈도 분석
            timeline_analysis["election_frequency"][dong_key] = {
                "total_elections": len(dong_data["elections"]),
                "election_years": [e["date"][:4] for e in dong_data["elections"]],
                "participation_trend": self._analyze_participation_trend(dong_data["elections"])
            }
            
            # 정당 진화 분석
            timeline_analysis["party_evolution"][dong_key] = {
                "party_diversity": len(dong_data["party_history"]),
                "party_stability": self._analyze_party_stability(dong_data["party_history"]),
                "new_party_introduction": self._analyze_new_party_introduction(dong_data["party_history"])
            }
            
            # 인구통계학적 트렌드
            timeline_analysis["demographic_trends"][dong_key] = {
                "gender_trend": self._analyze_gender_trend(dong_data["elections"]),
                "age_trend": self._analyze_age_trend(dong_data["elections"]),
                "education_trend": self._analyze_education_trend(dong_data["elections"])
            }
        
        return timeline_analysis

    def _create_lda_correlation(self, dong_elections: Dict[str, Any]) -> Dict[str, Any]:
        """LDA 시계열 포인트와의 상관관계 분석"""
        lda_correlation = {
            "timeline_matching": {},
            "topic_election_correlation": {},
            "influence_analysis": {}
        }
        
        for year, election_dates in self.lda_timeline_points.items():
            lda_correlation["timeline_matching"][year] = {
                "lda_points": election_dates,
                "matching_elections": [],
                "correlation_strength": 0.0
            }
            
            for dong_key, dong_data in dong_elections.items():
                matching_elections = []
                for election in dong_data["elections"]:
                    if election["election_id"] in election_dates:
                        matching_elections.append({
                            "election_id": election["election_id"],
                            "election_name": election["election_name"],
                            "candidate_count": election["candidate_count"],
                            "parties": election["parties"]
                        })
                
                if matching_elections:
                    lda_correlation["timeline_matching"][year]["matching_elections"].append({
                        "dong": dong_key,
                        "elections": matching_elections
                    })
        
        return lda_correlation

    def _analyze_participation_trend(self, elections: List[Dict]) -> Dict[str, Any]:
        """참여 트렌드 분석"""
        if not elections:
            return {}
        
        candidate_counts = [e["candidate_count"] for e in elections]
        return {
            "trend": "increasing" if len(candidate_counts) > 1 and candidate_counts[-1] > candidate_counts[0] else "decreasing",
            "average_participation": sum(candidate_counts) / len(candidate_counts),
            "participation_variance": max(candidate_counts) - min(candidate_counts) if candidate_counts else 0
        }

    def _analyze_party_stability(self, party_history: List[Dict]) -> Dict[str, Any]:
        """정당 안정성 분석"""
        if not party_history:
            return {}
        
        return {
            "stable_parties": len([p for p in party_history if p["election_count"] > 1]),
            "new_parties": len([p for p in party_history if p["election_count"] == 1]),
            "stability_rate": len([p for p in party_history if p["election_count"] > 1]) / len(party_history) if party_history else 0
        }

    def _analyze_new_party_introduction(self, party_history: List[Dict]) -> Dict[str, Any]:
        """신규 정당 도입 분석"""
        if not party_history:
            return {}
        
        return {
            "total_new_parties": len([p for p in party_history if p["election_count"] == 1]),
            "introduction_rate": len([p for p in party_history if p["election_count"] == 1]) / len(party_history) if party_history else 0
        }

    def _analyze_gender_trend(self, elections: List[Dict]) -> Dict[str, Any]:
        """성별 트렌드 분석"""
        gender_trends = {"남": [], "여": []}
        
        for election in elections:
            gender_dist = election.get("gender_distribution", {})
            total = sum(gender_dist.values())
            if total > 0:
                gender_trends["남"].append(gender_dist.get("남", 0) / total)
                gender_trends["여"].append(gender_dist.get("여", 0) / total)
        
        return {
            "male_trend": "increasing" if len(gender_trends["남"]) > 1 and gender_trends["남"][-1] > gender_trends["남"][0] else "decreasing",
            "female_trend": "increasing" if len(gender_trends["여"]) > 1 and gender_trends["여"][-1] > gender_trends["여"][0] else "decreasing",
            "gender_balance": sum(gender_trends["여"]) / len(gender_trends["여"]) if gender_trends["여"] else 0
        }

    def _analyze_age_trend(self, elections: List[Dict]) -> Dict[str, Any]:
        """연령 트렌드 분석"""
        age_trends = {"20대": [], "30대": [], "40대": [], "50대": [], "60대": [], "70대": [], "80대": []}
        
        for election in elections:
            age_dist = election.get("age_distribution", {})
            total = sum(age_dist.values())
            if total > 0:
                for age_group in age_trends:
                    age_trends[age_group].append(age_dist.get(age_group, 0) / total)
        
        return {
            "dominant_age_group": max(age_trends.keys(), key=lambda k: sum(age_trends[k]) / len(age_trends[k]) if age_trends[k] else 0),
            "age_diversity": len([k for k, v in age_trends.items() if v and sum(v) > 0])
        }

    def _analyze_education_trend(self, elections: List[Dict]) -> Dict[str, Any]:
        """학력 트렌드 분석"""
        education_trends = {}
        
        for election in elections:
            edu_dist = election.get("education_distribution", {})
            for education, count in edu_dist.items():
                if education not in education_trends:
                    education_trends[education] = []
                education_trends[education].append(count)
        
        return {
            "education_diversity": len(education_trends),
            "dominant_education": max(education_trends.keys(), key=lambda k: sum(education_trends[k]) / len(education_trends[k]) if education_trends[k] else 0) if education_trends else "기타"
        }

    def create_vercel_optimized_structure(self, dong_election_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Vercel 배포 최적화된 데이터 구조 생성"""
        vercel_structure = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "data_type": "dong_election_analysis",
                "optimized_for": "vercel_deployment"
            },
            "summary": {
                "total_dongs": dong_election_mapping["metadata"]["total_dongs"],
                "total_elections": len(set(e["election_id"] for dong_data in dong_election_mapping["dong_elections"].values() for e in dong_data["elections"])),
                "analysis_scope": "행정동 단위 선거 데이터 분석"
            },
            "dong_data": dong_election_mapping["dong_elections"],
            "timeline_analysis": dong_election_mapping["timeline_analysis"],
            "lda_correlation": dong_election_mapping["lda_correlation"],
            "api_endpoints": {
                "dong_list": "/api/dong-list",
                "dong_elections": "/api/dong-elections/{dong_code}",
                "timeline_analysis": "/api/timeline-analysis",
                "lda_correlation": "/api/lda-correlation"
            }
        }
        
        return vercel_structure

    def save_vercel_data(self, vercel_data: Dict[str, Any]) -> str:
        """Vercel 배포용 데이터 저장"""
        output_file = f"{self.output_dir}/dong_election_analysis.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(vercel_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Vercel 배포용 데이터 저장 완료: {output_file}")
        return output_file

def main():
    """메인 실행 함수"""
    mapper = RegionElectionMapper()
    
    # 선거 데이터 로드 (실제 파일 경로로 수정 필요)
    election_file = "election_data/vercel_election_data.json"
    if not os.path.exists(election_file):
        logger.error(f"선거 데이터 파일을 찾을 수 없습니다: {election_file}")
        return
    
    election_data = mapper.load_election_data(election_file)
    
    # 행정동 단위 매핑
    dong_mapping = mapper.map_elections_to_dong(election_data)
    
    # Vercel 최적화 구조 생성
    vercel_data = mapper.create_vercel_optimized_structure(dong_mapping)
    
    # 데이터 저장
    output_file = mapper.save_vercel_data(vercel_data)
    
    logger.info(f"행정동 단위 선거 데이터 매핑 완료: {output_file}")

if __name__ == "__main__":
    main()
