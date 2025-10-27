#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지역이슈+통계변화+선거구도+선거결과 영향력 분석
LDA 시계열 포인트와 선거 데이터의 상관관계 분석
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
import os
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class InfluenceAnalyzer:
    def __init__(self):
        self.data_dir = "vercel_optimized_data"
        self.output_dir = "influence_analysis"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # LDA 토픽 매핑
        self.lda_topics = {
            "교통정책": ["교통", "대중교통", "지하철", "버스", "교통체증", "주차", "도로"],
            "환경보호": ["환경", "대기질", "미세먼지", "녹지", "공원", "재활용", "친환경"],
            "복지정책": ["복지", "보육", "노인", "장애인", "주거", "의료", "교육"],
            "경제발전": ["경제", "일자리", "창업", "투자", "상권", "관광", "산업"],
            "도시재생": ["재개발", "재건축", "뉴타운", "도시계획", "건축", "주택", "아파트"],
            "안전": ["안전", "범죄", "CCTV", "경찰", "소방", "응급", "재난"],
            "문화": ["문화", "예술", "체육", "축제", "공연", "박물관", "도서관"],
            "교육": ["교육", "학교", "학원", "대학", "유치원", "교사", "학생"]
        }
        
        # 통계 지표 매핑
        self.statistical_indicators = {
            "인구": ["총인구", "인구밀도", "인구증감률", "연령구조"],
            "경제": ["GDP", "소득", "고용률", "실업률", "물가"],
            "사회": ["교육수준", "의료접근성", "주거환경", "교통편의성"],
            "환경": ["대기질", "수질", "녹지율", "소음", "폐기물"]
        }

    def load_dong_election_data(self, file_path: str) -> Dict[str, Any]:
        """행정동 선거 데이터 로드"""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
        return {}

    def analyze_influence(self, mapped_election_data: Dict[str, Any], population_data: Dict[str, Any], news_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """영향력 분석 메인 메서드"""
        logger.info("📊 영향력 분석 시작...")
        
        if not mapped_election_data or "dong_elections" not in mapped_election_data:
            logger.error("❌ 매핑된 선거 데이터가 올바르지 않습니다.")
            return {}

        analysis_results = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "analysis_type": "influence_analysis"
            },
            "regional_analysis": {},
            "temporal_analysis": {},
            "correlation_analysis": {},
            "influence_summary": {}
        }

        # 지역별 분석
        for dong_key, dong_info in mapped_election_data["dong_elections"].items():
            sido_name = dong_info.get("sido_name", "")
            gu_name = dong_info.get("gu_name", "")
            dong_name = dong_info.get("dong_name", "")
            
            analysis_results["regional_analysis"][dong_key] = {
                "sido_name": sido_name,
                "gu_name": gu_name,
                "dong_name": dong_name,
                "population": population_data.get(sido_name, {}).get("population", 0),
                "election_count": len(dong_info.get("elections", [])),
                "party_diversity": len(dong_info.get("party_history", {})),
                "candidate_analysis": self._analyze_candidates(dong_info.get("elections", [])),
                "trend_analysis": self._analyze_trends(dong_info.get("elections", []))
            }

        # 시간순 분석
        analysis_results["temporal_analysis"] = self._analyze_temporal_patterns(mapped_election_data["dong_elections"])
        
        # 상관관계 분석
        analysis_results["correlation_analysis"] = self._analyze_correlations(mapped_election_data["dong_elections"], population_data)
        
        # 영향력 요약
        analysis_results["influence_summary"] = self._create_influence_summary(analysis_results)
        
        logger.info("✅ 영향력 분석 완료")
        return analysis_results

    def _analyze_candidates(self, elections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """후보자 분석"""
        if not elections:
            return {}
        
        total_candidates = sum(len(election.get("candidates", [])) for election in elections)
        gender_dist = {"남": 0, "여": 0}
        age_groups = {"20대": 0, "30대": 0, "40대": 0, "50대": 0, "60대": 0, "70대": 0}
        
        for election in elections:
            for candidate in election.get("candidates", []):
                gender = candidate.get("gender", "남")
                age = candidate.get("age", 0)
                
                gender_dist[gender] += 1
                
                if 20 <= age < 30:
                    age_groups["20대"] += 1
                elif 30 <= age < 40:
                    age_groups["30대"] += 1
                elif 40 <= age < 50:
                    age_groups["40대"] += 1
                elif 50 <= age < 60:
                    age_groups["50대"] += 1
                elif 60 <= age < 70:
                    age_groups["60대"] += 1
                elif age >= 70:
                    age_groups["70대"] += 1
        
        return {
            "total_candidates": total_candidates,
            "gender_distribution": gender_dist,
            "age_distribution": age_groups
        }

    def _analyze_trends(self, elections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """트렌드 분석"""
        if not elections:
            return {}
        
        # 시간순 정렬
        sorted_elections = sorted(elections, key=lambda x: x.get("date", ""))
        
        trends = {
            "participation_trend": [],
            "party_diversity_trend": [],
            "candidate_count_trend": []
        }
        
        for election in sorted_elections:
            trends["participation_trend"].append({
                "date": election.get("date", ""),
                "candidate_count": len(election.get("candidates", []))
            })
            
            parties = set()
            for candidate in election.get("candidates", []):
                parties.add(candidate.get("jdName", "무소속"))
            
            trends["party_diversity_trend"].append({
                "date": election.get("date", ""),
                "party_count": len(parties)
            })
        
        return trends

    def _analyze_temporal_patterns(self, dong_elections: Dict[str, Any]) -> Dict[str, Any]:
        """시간순 패턴 분석"""
        temporal_patterns = {
            "election_frequency": {},
            "participation_patterns": {},
            "party_evolution": {}
        }
        
        for dong_key, dong_info in dong_elections.items():
            elections = dong_info.get("elections", [])
            temporal_patterns["election_frequency"][dong_key] = len(elections)
            
            # 참여 패턴 분석
            participation_years = [election.get("date", "")[:4] for election in elections]
            temporal_patterns["participation_patterns"][dong_key] = {
                "years": participation_years,
                "frequency": len(set(participation_years))
            }
        
        return temporal_patterns

    def _analyze_correlations(self, dong_elections: Dict[str, Any], population_data: Dict[str, Any]) -> Dict[str, Any]:
        """상관관계 분석"""
        correlations = {
            "population_participation": {},
            "regional_correlations": {}
        }
        
        for dong_key, dong_info in dong_elections.items():
            sido_name = dong_info.get("sido_name", "")
            population = population_data.get(sido_name, {}).get("population", 0)
            election_count = len(dong_info.get("elections", []))
            
            correlations["population_participation"][dong_key] = {
                "population": population,
                "election_count": election_count,
                "participation_rate": election_count / max(population / 1000000, 1)  # 백만명당 선거 수
            }
        
        return correlations

    def _create_influence_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """영향력 요약 생성"""
        summary = {
            "total_regions": len(analysis_results["regional_analysis"]),
            "high_influence_regions": [],
            "trending_issues": [],
            "key_insights": []
        }
        
        # 고영향력 지역 식별
        for dong_key, dong_analysis in analysis_results["regional_analysis"].items():
            if dong_analysis.get("election_count", 0) > 5:  # 5회 이상 선거 참여
                summary["high_influence_regions"].append({
                    "dong_key": dong_key,
                    "election_count": dong_analysis.get("election_count", 0),
                    "party_diversity": dong_analysis.get("party_diversity", 0)
                })
        
        return summary

    def save_analysis_results(self, filename: str = "election_data/influence_analysis_results.json"):
        """분석 결과 저장"""
        import json
        import os
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=4)
        
        logger.info(f"✅ 영향력 분석 결과 저장 완료: {filename}")

    def analyze_regional_issues(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """지역 이슈 분석"""
        regional_issues = {
            "issue_frequency": {},
            "issue_evolution": {},
            "issue_correlation": {},
            "issue_impact": {}
        }
        
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            dong_issues = {
                "frequent_issues": [],
                "emerging_issues": [],
                "declining_issues": [],
                "issue_trends": {}
            }
            
            # 선거별 이슈 분석
            for election in dong_info.get("elections", []):
                election_issues = self._extract_election_issues(election)
                dong_issues["frequent_issues"].extend(election_issues)
            
            # 이슈 빈도 분석
            issue_frequency = {}
            for issue in dong_issues["frequent_issues"]:
                issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
            
            dong_issues["issue_frequency"] = issue_frequency
            dong_issues["top_issues"] = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            
            regional_issues["issue_frequency"][dong_key] = dong_issues
        
        return regional_issues

    def _extract_election_issues(self, election: Dict[str, Any]) -> List[str]:
        """선거에서 이슈 추출"""
        issues = []
        
        # 정당별 이슈 추출
        for party in election.get("parties", []):
            if party in self.lda_topics:
                issues.extend(self.lda_topics[party])
        
        # 후보자 경력에서 이슈 추출
        for candidate in election.get("candidates", []):
            career = candidate.get("career1", "")
            for topic, keywords in self.lda_topics.items():
                if any(keyword in career for keyword in keywords):
                    issues.append(topic)
        
        return list(set(issues))

    def analyze_statistical_changes(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """통계 변화 분석"""
        statistical_analysis = {
            "population_trends": {},
            "economic_indicators": {},
            "social_indicators": {},
            "environmental_indicators": {}
        }
        
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            # 인구 통계 분석
            population_analysis = self._analyze_population_trends(dong_info)
            statistical_analysis["population_trends"][dong_key] = population_analysis
            
            # 경제 지표 분석
            economic_analysis = self._analyze_economic_indicators(dong_info)
            statistical_analysis["economic_indicators"][dong_key] = economic_analysis
            
            # 사회 지표 분석
            social_analysis = self._analyze_social_indicators(dong_info)
            statistical_analysis["social_indicators"][dong_key] = social_analysis
            
            # 환경 지표 분석
            environmental_analysis = self._analyze_environmental_indicators(dong_info)
            statistical_analysis["environmental_indicators"][dong_key] = environmental_analysis
        
        return statistical_analysis

    def _analyze_population_trends(self, dong_info: Dict[str, Any]) -> Dict[str, Any]:
        """인구 트렌드 분석"""
        elections = dong_info.get("elections", [])
        if not elections:
            return {}
        
        # 연령 분포 변화 분석
        age_trends = {}
        for election in elections:
            age_dist = election.get("age_distribution", {})
            for age_group, count in age_dist.items():
                if age_group not in age_trends:
                    age_trends[age_group] = []
                age_trends[age_group].append(count)
        
        # 인구 변화율 계산
        population_change = {}
        for age_group, counts in age_trends.items():
            if len(counts) > 1:
                change_rate = (counts[-1] - counts[0]) / counts[0] * 100 if counts[0] > 0 else 0
                population_change[age_group] = change_rate
        
        return {
            "age_distribution_trend": age_trends,
            "population_change_rate": population_change,
            "dominant_age_group": max(age_trends.keys(), key=lambda k: sum(age_trends[k]) / len(age_trends[k]) if age_trends[k] else 0) if age_trends else "기타"
        }

    def _analyze_economic_indicators(self, dong_info: Dict[str, Any]) -> Dict[str, Any]:
        """경제 지표 분석"""
        elections = dong_info.get("elections", [])
        if not elections:
            return {}
        
        # 직업 분포 분석
        job_distribution = {}
        for election in elections:
            for candidate in election.get("candidates", []):
                job = candidate.get("job", "기타")
                job_distribution[job] = job_distribution.get(job, 0) + 1
        
        # 교육 수준 분석
        education_distribution = {}
        for election in elections:
            edu_dist = election.get("education_distribution", {})
            for education, count in edu_dist.items():
                education_distribution[education] = education_distribution.get(education, 0) + count
        
        return {
            "job_diversity": len(job_distribution),
            "education_level": education_distribution,
            "economic_activity": job_distribution
        }

    def _analyze_social_indicators(self, dong_info: Dict[str, Any]) -> Dict[str, Any]:
        """사회 지표 분석"""
        elections = dong_info.get("elections", [])
        if not elections:
            return {}
        
        # 성별 분포 분석
        gender_distribution = {}
        for election in elections:
            gender_dist = election.get("gender_distribution", {})
            for gender, count in gender_dist.items():
                gender_distribution[gender] = gender_distribution.get(gender, 0) + count
        
        # 정당 다양성 분석
        party_diversity = len(set(party for election in elections for party in election.get("parties", [])))
        
        return {
            "gender_balance": gender_distribution,
            "party_diversity": party_diversity,
            "social_participation": len(elections)
        }

    def _analyze_environmental_indicators(self, dong_info: Dict[str, Any]) -> Dict[str, Any]:
        """환경 지표 분석"""
        elections = dong_info.get("elections", [])
        if not elections:
            return {}
        
        # 환경 관련 이슈 분석
        environmental_issues = []
        for election in elections:
            for candidate in election.get("candidates", []):
                career = candidate.get("career1", "")
                if any(keyword in career for keyword in ["환경", "녹지", "공원", "대기", "수질"]):
                    environmental_issues.append(career)
        
        return {
            "environmental_awareness": len(environmental_issues),
            "environmental_issues": environmental_issues[:10]  # 상위 10개
        }

    def analyze_election_district_changes(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """선거구도 변화 분석"""
        district_analysis = {
            "boundary_changes": {},
            "district_evolution": {},
            "political_geography": {}
        }
        
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            elections = dong_info.get("elections", [])
            if not elections:
                continue
            
            # 선거구 변화 분석
            district_changes = {
                "election_count": len(elections),
                "party_changes": [],
                "candidate_changes": [],
                "political_stability": 0
            }
            
            # 정당 변화 추적
            party_history = []
            for election in elections:
                parties = election.get("parties", [])
                party_history.append(parties)
            
            # 정당 안정성 분석
            if len(party_history) > 1:
                stable_parties = set(party_history[0])
                for parties in party_history[1:]:
                    stable_parties = stable_parties.intersection(set(parties))
                district_changes["political_stability"] = len(stable_parties) / len(party_history[0]) if party_history[0] else 0
            
            district_analysis["boundary_changes"][dong_key] = district_changes
        
        return district_analysis

    def analyze_election_results_impact(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """선거 결과 영향 분석"""
        results_analysis = {
            "voting_patterns": {},
            "political_swings": {},
            "result_correlations": {},
            "impact_assessment": {}
        }
        
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            elections = dong_info.get("elections", [])
            if not elections:
                continue
            
            # 투표 패턴 분석
            voting_patterns = {
                "participation_trend": [],
                "party_preference": {},
                "candidate_diversity": []
            }
            
            for election in elections:
                voting_patterns["participation_trend"].append(election.get("candidate_count", 0))
                for party in election.get("parties", []):
                    voting_patterns["party_preference"][party] = voting_patterns["party_preference"].get(party, 0) + 1
                voting_patterns["candidate_diversity"].append(len(election.get("candidates", [])))
            
            results_analysis["voting_patterns"][dong_key] = voting_patterns
        
        return results_analysis

    def create_lda_correlation_analysis(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """LDA 상관관계 분석"""
        lda_correlation = {
            "topic_election_correlation": {},
            "temporal_correlation": {},
            "influence_network": {}
        }
        
        # LDA 토픽과 선거 데이터 상관관계
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            elections = dong_info.get("elections", [])
            if not elections:
                continue
            
            topic_correlation = {}
            for topic, keywords in self.lda_topics.items():
                topic_frequency = 0
                for election in elections:
                    for candidate in election.get("candidates", []):
                        career = candidate.get("career1", "")
                        if any(keyword in career for keyword in keywords):
                            topic_frequency += 1
                
                topic_correlation[topic] = topic_frequency
            
            lda_correlation["topic_election_correlation"][dong_key] = topic_correlation
        
        return lda_correlation

    def create_comprehensive_analysis(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """종합 영향력 분석"""
        comprehensive_analysis = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "analysis_type": "comprehensive_influence_analysis",
                "version": "1.0.0"
            },
            "regional_issues": self.analyze_regional_issues(dong_data),
            "statistical_changes": self.analyze_statistical_changes(dong_data),
            "district_changes": self.analyze_election_district_changes(dong_data),
            "election_results": self.analyze_election_results_impact(dong_data),
            "lda_correlation": self.create_lda_correlation_analysis(dong_data),
            "influence_network": self._create_influence_network(dong_data),
            "recommendations": self._generate_recommendations(dong_data)
        }
        
        return comprehensive_analysis

    def _create_influence_network(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """영향력 네트워크 생성"""
        influence_network = {
            "nodes": [],
            "edges": [],
            "centrality": {}
        }
        
        # 노드 생성 (행정동)
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            node = {
                "id": dong_key,
                "type": "dong",
                "name": dong_info.get("dong_name", ""),
                "gu": dong_info.get("gu_name", ""),
                "sido": dong_info.get("sido_name", ""),
                "election_count": len(dong_info.get("elections", [])),
                "candidate_count": sum(e.get("candidate_count", 0) for e in dong_info.get("elections", []))
            }
            influence_network["nodes"].append(node)
        
        # 엣지 생성 (연결성)
        for i, node1 in enumerate(influence_network["nodes"]):
            for j, node2 in enumerate(influence_network["nodes"]):
                if i != j and node1["gu"] == node2["gu"]:
                    edge = {
                        "source": node1["id"],
                        "target": node2["id"],
                        "weight": 1.0,
                        "type": "same_gu"
                    }
                    influence_network["edges"].append(edge)
        
        return influence_network

    def _generate_recommendations(self, dong_data: Dict[str, Any]) -> Dict[str, Any]:
        """정책 권고사항 생성"""
        recommendations = {
            "regional_policy": {},
            "electoral_reform": {},
            "data_improvement": {}
        }
        
        for dong_key, dong_info in dong_data.get("dong_data", {}).items():
            elections = dong_info.get("elections", [])
            if not elections:
                continue
            
            # 지역별 정책 권고
            regional_recommendations = []
            
            # 참여도 기반 권고
            avg_participation = sum(e.get("candidate_count", 0) for e in elections) / len(elections)
            if avg_participation < 3:
                regional_recommendations.append("후보자 참여도 증진을 위한 정책 필요")
            
            # 정당 다양성 기반 권고
            all_parties = set()
            for election in elections:
                all_parties.update(election.get("parties", []))
            
            if len(all_parties) < 3:
                regional_recommendations.append("정당 다양성 증진을 위한 제도 개선 필요")
            
            recommendations["regional_policy"][dong_key] = regional_recommendations
        
        return recommendations

    def save_analysis_results(self, analysis_data: Dict[str, Any]) -> str:
        """분석 결과 저장"""
        output_file = f"{self.output_dir}/comprehensive_influence_analysis.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"종합 영향력 분석 결과 저장 완료: {output_file}")
        return output_file

def main():
    """메인 실행 함수"""
    analyzer = InfluenceAnalyzer()
    
    # 행정동 선거 데이터 로드
    dong_data_file = "vercel_optimized_data/dong_election_analysis.json"
    if not os.path.exists(dong_data_file):
        logger.error(f"행정동 선거 데이터 파일을 찾을 수 없습니다: {dong_data_file}")
        return
    
    dong_data = analyzer.load_dong_election_data(dong_data_file)
    
    # 종합 영향력 분석
    comprehensive_analysis = analyzer.create_comprehensive_analysis(dong_data)
    
    # 분석 결과 저장
    output_file = analyzer.save_analysis_results(comprehensive_analysis)
    
    logger.info(f"종합 영향력 분석 완료: {output_file}")

if __name__ == "__main__":
    main()
