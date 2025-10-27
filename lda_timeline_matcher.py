#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LDA 시계열 포인트와 선거 데이터 매칭
각 동별, 시별, 도별 LDA 분석을 시계열에 맞춰 배치
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class LDATimelineMatcher:
    def __init__(self):
        self.data_dir = "election_data"
        self.lda_dir = "influence_analysis"
        
        # LDA 토픽 카테고리
        self.topic_categories = {
            "정치": ["정치", "선거", "정당", "의회", "정부", "정책"],
            "경제": ["경제", "경기", "고용", "산업", "투자", "성장"],
            "사회": ["사회", "복지", "교육", "보건", "환경", "안전"],
            "지역": ["지역", "개발", "교통", "도시", "농촌", "인프라"],
            "문화": ["문화", "체육", "관광", "예술", "전통", "혁신"]
        }
        
        # 시도별 주요 이슈 (샘플 데이터)
        self.regional_issues = {
            "서울특별시": ["도심재생", "교통혼잡", "주거문제", "환경보호", "복지정책"],
            "부산광역시": ["항만개발", "관광진흥", "해양환경", "교통망", "지역균형"],
            "대구광역시": ["도시재생", "교통정책", "환경보호", "복지정책", "경제발전"],
            "인천광역시": ["공항개발", "항만정책", "교통망", "환경보호", "지역발전"],
            "광주광역시": ["민주주의", "문화정책", "환경보호", "복지정책", "지역균형"],
            "대전광역시": ["과학기술", "연구개발", "교통정책", "환경보호", "복지정책"],
            "울산광역시": ["산업정책", "환경보호", "교통정책", "복지정책", "지역발전"],
            "세종특별자치시": ["행정중심", "교통정책", "환경보호", "복지정책", "지역발전"],
            "경기도": ["신도시", "교통망", "환경보호", "복지정책", "지역균형"],
            "강원특별자치도": ["관광정책", "환경보호", "교통정책", "복지정책", "지역발전"],
            "충청북도": ["산업정책", "교통정책", "환경보호", "복지정책", "지역발전"],
            "충청남도": ["산업정책", "교통정책", "환경보호", "복지정책", "지역발전"],
            "전북특별자치도": ["농업정책", "환경보호", "교통정책", "복지정책", "지역발전"],
            "전라남도": ["농업정책", "환경보호", "교통정책", "복지정책", "지역발전"],
            "경상북도": ["산업정책", "교통정책", "환경보호", "복지정책", "지역발전"],
            "경상남도": ["산업정책", "교통정책", "환경보호", "복지정책", "지역발전"],
            "제주특별자치도": ["관광정책", "환경보호", "교통정책", "복지정책", "지역발전"]
        }

    def generate_lda_timeline_data(self, election_data: Dict[str, Any], mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """LDA 시계열 데이터 생성"""
        logger.info("📊 LDA 시계열 데이터 생성 시작...")
        
        lda_timeline = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "analysis_type": "lda_timeline_analysis",
                "description": "각 동별, 시별, 도별 LDA 분석 시계열 매칭"
            },
            "dong_level": {},  # 동별 LDA
            "gu_level": {},    # 구별 LDA  
            "sido_level": {},  # 시도별 LDA
            "timeline_correlation": {},
            "topic_evolution": {}
        }
        
        # 동별 LDA 분석
        lda_timeline["dong_level"] = self._analyze_dong_lda(mapped_data)
        
        # 구별 LDA 분석
        lda_timeline["gu_level"] = self._analyze_gu_lda(mapped_data)
        
        # 시도별 LDA 분석
        lda_timeline["sido_level"] = self._analyze_sido_lda(election_data)
        
        # 시계열 상관관계 분석
        lda_timeline["timeline_correlation"] = self._analyze_timeline_correlation(lda_timeline)
        
        # 토픽 진화 분석
        lda_timeline["topic_evolution"] = self._analyze_topic_evolution(lda_timeline)
        
        logger.info("✅ LDA 시계열 데이터 생성 완료")
        return lda_timeline

    def _analyze_dong_lda(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """동별 LDA 분석"""
        dong_lda = {}
        
        for dong_key, dong_info in mapped_data.get("dong_elections", {}).items():
            sido_name = dong_info.get("sido_name", "")
            gu_name = dong_info.get("gu_name", "")
            dong_name = dong_info.get("dong_name", "")
            
            # 동별 주요 이슈 추출
            dong_issues = self._extract_dong_issues(sido_name, gu_name, dong_name)
            
            # 선거별 토픽 분석
            election_topics = {}
            for election in dong_info.get("elections", []):
                election_date = election.get("date", "")
                topics = self._analyze_election_topics(election, dong_issues)
                election_topics[election_date] = topics
            
            dong_lda[dong_key] = {
                "sido_name": sido_name,
                "gu_name": gu_name,
                "dong_name": dong_name,
                "main_issues": dong_issues,
                "election_topics": election_topics,
                "topic_trends": self._analyze_topic_trends(election_topics),
                "lda_scores": self._calculate_lda_scores(election_topics)
            }
        
        return dong_lda

    def _analyze_gu_lda(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """구별 LDA 분석"""
        gu_lda = {}
        gu_data = {}
        
        # 구별로 데이터 그룹화
        for dong_key, dong_info in mapped_data.get("dong_elections", {}).items():
            gu_key = f"{dong_info.get('sido_name', '')}_{dong_info.get('gu_name', '')}"
            
            if gu_key not in gu_data:
                gu_data[gu_key] = {
                    "sido_name": dong_info.get("sido_name", ""),
                    "gu_name": dong_info.get("gu_name", ""),
                    "elections": []
                }
            
            gu_data[gu_key]["elections"].extend(dong_info.get("elections", []))
        
        # 구별 LDA 분석
        for gu_key, gu_info in gu_data.items():
            sido_name = gu_info["sido_name"]
            gu_name = gu_info["gu_name"]
            
            # 구별 주요 이슈
            gu_issues = self._extract_gu_issues(sido_name, gu_name)
            
            # 선거별 토픽 분석
            election_topics = {}
            for election in gu_info["elections"]:
                election_date = election.get("date", "")
                topics = self._analyze_election_topics(election, gu_issues)
                election_topics[election_date] = topics
            
            gu_lda[gu_key] = {
                "sido_name": sido_name,
                "gu_name": gu_name,
                "main_issues": gu_issues,
                "election_topics": election_topics,
                "topic_trends": self._analyze_topic_trends(election_topics),
                "lda_scores": self._calculate_lda_scores(election_topics)
            }
        
        return gu_lda

    def _analyze_sido_lda(self, election_data: Dict[str, Any]) -> Dict[str, Any]:
        """시도별 LDA 분석"""
        sido_lda = {}
        
        for election in election_data.get("elections", []):
            for region_name, region_data in election.get("regions", {}).items():
                if region_name not in sido_lda:
                    sido_lda[region_name] = {
                        "sido_name": region_name,
                        "main_issues": self.regional_issues.get(region_name, []),
                        "election_topics": {},
                        "topic_trends": {},
                        "lda_scores": {}
                    }
                
                election_date = election.get("election_id", "")
                topics = self._analyze_region_topics(region_data, region_name)
                sido_lda[region_name]["election_topics"][election_date] = topics
        
        # 시도별 토픽 트렌드 분석
        for sido_name, sido_info in sido_lda.items():
            sido_info["topic_trends"] = self._analyze_topic_trends(sido_info["election_topics"])
            sido_info["lda_scores"] = self._calculate_lda_scores(sido_info["election_topics"])
        
        return sido_lda

    def _extract_dong_issues(self, sido_name: str, gu_name: str, dong_name: str) -> List[str]:
        """동별 주요 이슈 추출"""
        base_issues = self.regional_issues.get(sido_name, [])
        
        # 동별 특화 이슈 추가
        dong_specific_issues = []
        if "중심" in dong_name or "시청" in dong_name:
            dong_specific_issues.extend(["도심재생", "교통정책", "상권활성화"])
        elif "산" in dong_name or "공원" in dong_name:
            dong_specific_issues.extend(["환경보호", "녹지정책", "생태보전"])
        elif "강" in dong_name or "하천" in dong_name:
            dong_specific_issues.extend(["수질정책", "홍수방지", "하천정비"])
        elif "산업" in dong_name or "공단" in dong_name:
            dong_specific_issues.extend(["산업정책", "환경보호", "고용정책"])
        
        return base_issues + dong_specific_issues

    def _extract_gu_issues(self, sido_name: str, gu_name: str) -> List[str]:
        """구별 주요 이슈 추출"""
        base_issues = self.regional_issues.get(sido_name, [])
        
        # 구별 특화 이슈 추가
        gu_specific_issues = []
        if "강남" in gu_name or "서초" in gu_name:
            gu_specific_issues.extend(["부동산정책", "교통정책", "교육정책"])
        elif "종로" in gu_name or "중구" in gu_name:
            gu_specific_issues.extend(["도심재생", "문화정책", "관광정책"])
        elif "강서" in gu_name or "양천" in gu_name:
            gu_specific_issues.extend(["교통정책", "주거정책", "환경정책"])
        
        return base_issues + gu_specific_issues

    def _analyze_election_topics(self, election: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """선거별 토픽 분석"""
        topics = {
            "political_topics": [],
            "economic_topics": [],
            "social_topics": [],
            "regional_topics": [],
            "cultural_topics": []
        }
        
        # 후보자별 토픽 분석
        for candidate in election.get("candidates", []):
            party = candidate.get("jdName", "무소속")
            career = candidate.get("career1", "")
            
            # 정당별 주요 토픽
            if "더불어민주당" in party:
                topics["political_topics"].extend(["민주주의", "복지정책", "환경보호"])
            elif "국민의힘" in party:
                topics["political_topics"].extend(["경제정책", "안보정책", "자유시장"])
            elif "정의당" in party:
                topics["political_topics"].extend(["사회정의", "환경정책", "복지정책"])
            
            # 경력별 토픽
            if "변호사" in career:
                topics["political_topics"].extend(["법치주의", "인권정책"])
            elif "교수" in career:
                topics["social_topics"].extend(["교육정책", "연구개발"])
            elif "의사" in career:
                topics["social_topics"].extend(["보건정책", "의료정책"])
            elif "기업가" in career:
                topics["economic_topics"].extend(["경제정책", "산업정책"])
        
        # 지역 이슈와 매칭
        for issue in issues:
            if any(keyword in issue for keyword in self.topic_categories["정치"]):
                topics["political_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["경제"]):
                topics["economic_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["사회"]):
                topics["social_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["지역"]):
                topics["regional_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["문화"]):
                topics["cultural_topics"].append(issue)
        
        # 중복 제거 및 빈도 계산
        for category in topics:
            topics[category] = list(set(topics[category]))
        
        return topics

    def _analyze_region_topics(self, region_data: Dict[str, Any], region_name: str) -> Dict[str, Any]:
        """지역별 토픽 분석"""
        topics = {
            "political_topics": [],
            "economic_topics": [],
            "social_topics": [],
            "regional_topics": [],
            "cultural_topics": []
        }
        
        # 정당 분포에 따른 토픽 분석
        parties = region_data.get("parties", [])
        for party in parties:
            if "더불어민주당" in party:
                topics["political_topics"].extend(["민주주의", "복지정책"])
            elif "국민의힘" in party:
                topics["economic_topics"].extend(["경제정책", "안보정책"])
            elif "정의당" in party:
                topics["social_topics"].extend(["사회정의", "환경정책"])
        
        # 지역 이슈 추가
        regional_issues = self.regional_issues.get(region_name, [])
        for issue in regional_issues:
            if any(keyword in issue for keyword in self.topic_categories["정치"]):
                topics["political_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["경제"]):
                topics["economic_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["사회"]):
                topics["social_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["지역"]):
                topics["regional_topics"].append(issue)
            elif any(keyword in issue for keyword in self.topic_categories["문화"]):
                topics["cultural_topics"].append(issue)
        
        # 중복 제거
        for category in topics:
            topics[category] = list(set(topics[category]))
        
        return topics

    def _analyze_topic_trends(self, election_topics: Dict[str, Any]) -> Dict[str, Any]:
        """토픽 트렌드 분석"""
        trends = {
            "emerging_topics": [],
            "declining_topics": [],
            "stable_topics": [],
            "topic_frequency": {}
        }
        
        all_topics = []
        for election_date, topics in election_topics.items():
            for category, topic_list in topics.items():
                all_topics.extend(topic_list)
        
        # 토픽 빈도 계산
        topic_frequency = {}
        for topic in all_topics:
            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        trends["topic_frequency"] = topic_frequency
        
        # 트렌드 분석 (간단한 예시)
        sorted_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
        trends["emerging_topics"] = [topic for topic, freq in sorted_topics[:5]]
        trends["stable_topics"] = [topic for topic, freq in sorted_topics[5:10]]
        trends["declining_topics"] = [topic for topic, freq in sorted_topics[10:]]
        
        return trends

    def _calculate_lda_scores(self, election_topics: Dict[str, Any]) -> Dict[str, float]:
        """LDA 점수 계산"""
        scores = {
            "political_score": 0.0,
            "economic_score": 0.0,
            "social_score": 0.0,
            "regional_score": 0.0,
            "cultural_score": 0.0
        }
        
        total_elections = len(election_topics)
        if total_elections == 0:
            return scores
        
        for election_date, topics in election_topics.items():
            for category, topic_list in topics.items():
                if category == "political_topics":
                    scores["political_score"] += len(topic_list)
                elif category == "economic_topics":
                    scores["economic_score"] += len(topic_list)
                elif category == "social_topics":
                    scores["social_score"] += len(topic_list)
                elif category == "regional_topics":
                    scores["regional_score"] += len(topic_list)
                elif category == "cultural_topics":
                    scores["cultural_score"] += len(topic_list)
        
        # 평균 계산
        for score_key in scores:
            scores[score_key] = scores[score_key] / total_elections
        
        return scores

    def _analyze_timeline_correlation(self, lda_timeline: Dict[str, Any]) -> Dict[str, Any]:
        """시계열 상관관계 분석"""
        correlation = {
            "dong_gu_correlation": {},
            "gu_sido_correlation": {},
            "cross_regional_correlation": {}
        }
        
        # 동-구 상관관계
        for dong_key, dong_lda in lda_timeline["dong_level"].items():
            gu_key = f"{dong_lda['sido_name']}_{dong_lda['gu_name']}"
            if gu_key in lda_timeline["gu_level"]:
                correlation["dong_gu_correlation"][dong_key] = {
                    "gu_key": gu_key,
                    "correlation_score": self._calculate_correlation_score(
                        dong_lda["lda_scores"], 
                        lda_timeline["gu_level"][gu_key]["lda_scores"]
                    )
                }
        
        # 구-시도 상관관계
        for gu_key, gu_lda in lda_timeline["gu_level"].items():
            sido_name = gu_lda["sido_name"]
            if sido_name in lda_timeline["sido_level"]:
                correlation["gu_sido_correlation"][gu_key] = {
                    "sido_name": sido_name,
                    "correlation_score": self._calculate_correlation_score(
                        gu_lda["lda_scores"],
                        lda_timeline["sido_level"][sido_name]["lda_scores"]
                    )
                }
        
        return correlation

    def _analyze_topic_evolution(self, lda_timeline: Dict[str, Any]) -> Dict[str, Any]:
        """토픽 진화 분석"""
        evolution = {
            "global_trends": {},
            "regional_trends": {},
            "temporal_patterns": {}
        }
        
        # 전역 트렌드 분석
        all_topics = []
        for level in ["dong_level", "gu_level", "sido_level"]:
            for region_key, region_lda in lda_timeline[level].items():
                for election_date, topics in region_lda.get("election_topics", {}).items():
                    for category, topic_list in topics.items():
                        all_topics.extend(topic_list)
        
        # 토픽 빈도 분석
        topic_frequency = {}
        for topic in all_topics:
            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        evolution["global_trends"] = {
            "most_frequent_topics": sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "topic_diversity": len(set(all_topics)),
            "total_topic_mentions": len(all_topics)
        }
        
        return evolution

    def _calculate_correlation_score(self, scores1: Dict[str, float], scores2: Dict[str, float]) -> float:
        """상관관계 점수 계산"""
        if not scores1 or not scores2:
            return 0.0
        
        # 간단한 상관관계 계산 (코사인 유사도)
        dot_product = sum(scores1.get(key, 0) * scores2.get(key, 0) for key in scores1.keys())
        magnitude1 = sum(score ** 2 for score in scores1.values()) ** 0.5
        magnitude2 = sum(score ** 2 for score in scores2.values()) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def save_lda_timeline(self, lda_timeline: Dict[str, Any], filename: str = "election_data/lda_timeline_analysis.json"):
        """LDA 시계열 분석 결과 저장"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(lda_timeline, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ LDA 시계열 분석 결과 저장 완료: {filename}")
        return filename

def main():
    """메인 실행 함수"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    matcher = LDATimelineMatcher()
    
    logger.info("=== LDA 시계열 매칭 시작 ===")
    
    # 데이터 로드
    with open('election_data/vercel_election_data.json', 'r', encoding='utf-8') as f:
        election_data = json.load(f)
    
    with open('election_data/mapped_election_data.json', 'r', encoding='utf-8') as f:
        mapped_data = json.load(f)
    
    # LDA 시계열 데이터 생성
    lda_timeline = matcher.generate_lda_timeline_data(election_data, mapped_data)
    
    # 결과 저장
    output_file = matcher.save_lda_timeline(lda_timeline)
    
    logger.info("=== LDA 시계열 매칭 완료 ===")
    logger.info(f"출력 파일: {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()
