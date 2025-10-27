#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
샘플 선거 데이터 생성기
API 키 문제로 인해 실제 데이터 대신 샘플 데이터를 생성하여 시스템 구축
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
import logging

logger = logging.getLogger(__name__)

class SampleElectionDataGenerator:
    def __init__(self):
        self.data_dir = "election_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 샘플 선거 데이터
        self.sample_elections = {
            "20240410": {"type": "2", "name": "제22대 국회의원선거", "year": 2024},
            "20220415": {"type": "2", "name": "제21대 국회의원선거", "year": 2022},
            "20200601": {"type": "3", "name": "제8회 지방선거", "year": 2020},
            "20180415": {"type": "2", "name": "제20대 국회의원선거", "year": 2018},
            "20160601": {"type": "3", "name": "제7회 지방선거", "year": 2016},
            "20140415": {"type": "2", "name": "제19대 국회의원선거", "year": 2014},
            "20120601": {"type": "3", "name": "제6회 지방선거", "year": 2012},
            "20100415": {"type": "2", "name": "제18대 국회의원선거", "year": 2010},
            "20080601": {"type": "3", "name": "제5회 지방선거", "year": 2008}
        }
        
        # 시도 목록
        self.sido_list = [
            "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
            "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도",
            "충청북도", "충청남도", "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
        ]
        
        # 정당 목록
        self.party_list = [
            "더불어민주당", "국민의힘", "정의당", "기본소득당", "녹색당",
            "새로운미래", "개혁신당", "진보당", "무소속"
        ]
        
        # 직업 목록
        self.job_list = [
            "정치인", "변호사", "교수", "의사", "기업가", "공무원", "언론인", "시민사회활동가"
        ]
        
        # 학력 목록
        self.education_list = [
            "고졸", "대졸", "석사", "박사"
        ]

    def generate_sample_candidates(self, election_id: str, sido_name: str, num_candidates: int = None) -> List[Dict[str, Any]]:
        """샘플 후보자 데이터 생성"""
        if num_candidates is None:
            num_candidates = random.randint(2, 8)
        
        candidates = []
        for i in range(num_candidates):
            candidate = {
                "sgId": election_id,
                "sgTypecode": self.sample_elections[election_id]["type"],
                "huboid": f"{election_id}{i+1:03d}",
                "sggName": f"{sido_name} {random.choice(['종로구', '중구', '용산구', '성동구', '광진구'])}",
                "sdName": sido_name,
                "wiwName": f"{sido_name} {random.choice(['종로구', '중구', '용산구', '성동구', '광진구'])}",
                "jdName": random.choice(self.party_list),
                "name": f"후보자{i+1}",
                "hanjaName": f"候補者{i+1}",
                "gender": random.choice(["남", "여"]),
                "birthday": f"{random.randint(1960, 1990)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}",
                "age": random.randint(30, 70),
                "addr": f"{sido_name} {random.choice(['종로구', '중구', '용산구', '성동구', '광진구'])}",
                "jobId": str(random.randint(1, 8)),
                "job": random.choice(self.job_list),
                "eduId": str(random.randint(1, 4)),
                "edu": random.choice(self.education_list),
                "career1": f"{random.choice(['국회의원', '시의원', '구의원', '시장', '구청장'])} 경력",
                "career2": f"{random.choice(['변호사', '교수', '의사', '기업가'])} 경력",
                "regdate": election_id,
                "status": "등록",
                "num": i + 1
            }
            candidates.append(candidate)
        
        return candidates

    def generate_election_data(self) -> Dict[str, Any]:
        """전체 선거 데이터 생성"""
        all_elections_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_elections": len(self.sample_elections),
                "data_type": "sample_election_data"
            },
            "elections": {}
        }
        
        for election_id, election_info in self.sample_elections.items():
            logger.info(f"샘플 데이터 생성 중: {election_info['name']} ({election_id})")
            
            election_data = {
                "election_id": election_id,
                "election_name": election_info["name"],
                "election_type": election_info["type"],
                "year": election_info["year"],
                "regions": {}
            }
            
            # 시도별 데이터 생성
            for sido_name in self.sido_list:
                num_candidates = random.randint(3, 12)
                candidates = self.generate_sample_candidates(election_id, sido_name, num_candidates)
                
                # 통계 분석
                gender_dist = {"남": 0, "여": 0}
                age_dist = {"20대": 0, "30대": 0, "40대": 0, "50대": 0, "60대": 0, "70대": 0}
                education_dist = {}
                party_dist = {}
                
                for candidate in candidates:
                    # 성별 분포
                    gender_dist[candidate["gender"]] += 1
                    
                    # 연령 분포
                    age = candidate["age"]
                    if 20 <= age < 30:
                        age_dist["20대"] += 1
                    elif 30 <= age < 40:
                        age_dist["30대"] += 1
                    elif 40 <= age < 50:
                        age_dist["40대"] += 1
                    elif 50 <= age < 60:
                        age_dist["50대"] += 1
                    elif 60 <= age < 70:
                        age_dist["60대"] += 1
                    elif age >= 70:
                        age_dist["70대"] += 1
                    
                    # 학력 분포
                    education = candidate["edu"]
                    education_dist[education] = education_dist.get(education, 0) + 1
                    
                    # 정당 분포
                    party = candidate["jdName"]
                    party_dist[party] = party_dist.get(party, 0) + 1
                
                election_data["regions"][sido_name] = {
                    "total_count": len(candidates),
                    "candidates": candidates,
                    "parties": list(party_dist.keys()),
                    "gender_distribution": gender_dist,
                    "age_distribution": age_dist,
                    "education_distribution": education_dist,
                    "career_analysis": self._analyze_careers(candidates)
                }
            
            all_elections_data["elections"][election_id] = election_data
            logger.info(f"✅ {election_info['name']} 샘플 데이터 생성 완료")
        
        return all_elections_data

    def _analyze_careers(self, candidates: List[Dict[str, Any]]) -> Dict[str, int]:
        """경력 분석"""
        career_count = {}
        for candidate in candidates:
            career = candidate.get("career1", "")
            career_count[career] = career_count.get(career, 0) + 1
        return career_count

    def create_timeline_analysis(self, all_elections_data: Dict[str, Any]) -> Dict[str, Any]:
        """시계열 분석 데이터 생성"""
        timeline_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "analysis_type": "election_timeline_analysis"
            },
            "timeline": [],
            "regional_analysis": {},
            "candidate_analysis": {},
            "party_analysis": {}
        }
        
        # 시간순 정렬
        sorted_elections = sorted(all_elections_data["elections"].items(), key=lambda x: x[0])
        
        for election_id, election_data in sorted_elections:
            timeline_entry = {
                "election_id": election_id,
                "election_name": election_data["election_name"],
                "election_type": election_data["election_type"],
                "year": election_data["year"],
                "total_candidates": sum(region["total_count"] for region in election_data["regions"].values()),
                "regions": {}
            }
            
            # 지역별 분석
            for region_name, region_data in election_data["regions"].items():
                timeline_entry["regions"][region_name] = {
                    "candidate_count": region_data["total_count"],
                    "parties": region_data["parties"],
                    "gender_distribution": region_data["gender_distribution"],
                    "age_distribution": region_data["age_distribution"],
                    "education_distribution": region_data["education_distribution"],
                    "career_analysis": region_data["career_analysis"]
                }
            
            timeline_data["timeline"].append(timeline_entry)
        
        return timeline_data

    def create_vercel_optimized_data(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Vercel 배포 최적화된 데이터 구조 생성"""
        vercel_data = {
            "metadata": timeline_data["metadata"],
            "summary": {
                "total_elections": len(timeline_data["timeline"]),
                "total_candidates": sum(entry["total_candidates"] for entry in timeline_data["timeline"]),
                "date_range": {
                    "start": min(entry["election_id"] for entry in timeline_data["timeline"]),
                    "end": max(entry["election_id"] for entry in timeline_data["timeline"])
                }
            },
            "elections": timeline_data["timeline"],
            "regional_summary": self._create_regional_summary(timeline_data),
            "party_summary": self._create_party_summary(timeline_data),
            "influence_analysis": self._create_influence_analysis(timeline_data)
        }
        
        return vercel_data

    def _create_regional_summary(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """지역별 요약 데이터 생성"""
        regional_summary = {}
        
        for entry in timeline_data["timeline"]:
            for region_name, region_data in entry["regions"].items():
                if region_name not in regional_summary:
                    regional_summary[region_name] = {
                        "total_elections": 0,
                        "total_candidates": 0,
                        "elections": []
                    }
                
                regional_summary[region_name]["total_elections"] += 1
                regional_summary[region_name]["total_candidates"] += region_data["candidate_count"]
                regional_summary[region_name]["elections"].append({
                    "election_id": entry["election_id"],
                    "election_name": entry["election_name"],
                    "candidate_count": region_data["candidate_count"],
                    "parties": region_data["parties"]
                })
        
        return regional_summary

    def _create_party_summary(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """정당별 요약 데이터 생성"""
        party_summary = {}
        
        for entry in timeline_data["timeline"]:
            for region_name, region_data in entry["regions"].items():
                for party in region_data["parties"]:
                    if party not in party_summary:
                        party_summary[party] = {
                            "total_candidates": 0,
                            "regions": set(),
                            "elections": []
                        }
                    
                    party_summary[party]["total_candidates"] += 1
                    party_summary[party]["regions"].add(region_name)
                    party_summary[party]["elections"].append({
                        "election_id": entry["election_id"],
                        "election_name": entry["election_name"],
                        "region": region_name
                    })
        
        # set을 list로 변환
        for party in party_summary:
            party_summary[party]["regions"] = list(party_summary[party]["regions"])
        
        return party_summary

    def _create_influence_analysis(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """영향력 분석 데이터 생성"""
        influence_analysis = {
            "trend_analysis": {},
            "regional_patterns": {},
            "temporal_patterns": {},
            "correlation_analysis": {}
        }
        
        # 추세 분석
        for entry in timeline_data["timeline"]:
            influence_analysis["trend_analysis"][entry["election_id"]] = {
                "total_candidates": entry["total_candidates"],
                "region_diversity": len(entry["regions"]),
                "participation_rate": entry["total_candidates"] / len(entry["regions"]) if entry["regions"] else 0
            }
        
        return influence_analysis

    def save_vercel_data(self, vercel_data: Dict[str, Any]) -> str:
        """Vercel 배포용 데이터 저장"""
        output_file = f"{self.data_dir}/vercel_election_data.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(vercel_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Vercel 배포용 데이터 저장 완료: {output_file}")
        return output_file

def main():
    """메인 실행 함수"""
    generator = SampleElectionDataGenerator()
    
    logger.info("=== 샘플 선거 데이터 생성 시작 ===")
    
    # 샘플 선거 데이터 생성
    all_elections_data = generator.generate_election_data()
    
    # 시계열 분석 데이터 생성
    timeline_data = generator.create_timeline_analysis(all_elections_data)
    
    # Vercel 최적화 데이터 생성
    vercel_data = generator.create_vercel_optimized_data(timeline_data)
    
    # 데이터 저장
    output_file = generator.save_vercel_data(vercel_data)
    
    logger.info("=== 샘플 선거 데이터 생성 완료 ===")
    logger.info(f"출력 파일: {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()
