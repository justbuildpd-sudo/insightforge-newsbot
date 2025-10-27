#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공공데이터포털 선거 후보자 정보 수집기
모든 선거의 후보자 정보를 행정동 단위로 수집하고 시계열 분석을 위한 데이터 구축
"""

import requests
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pandas as pd
import os
from typing import Dict, List, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ElectionDataCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://apis.data.go.kr/9760000/PofelcddInfoInqireService/getPoelpcddRegistSttusInfoInqire"
        self.data_dir = "election_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 선거 ID 및 종류 코드 매핑
        self.election_mapping = {
            # 대통령선거
            "20220309": {"type": "1", "name": "제20대 대통령선거"},
            "20170409": {"type": "1", "name": "제19대 대통령선거"},
            "20121219": {"type": "1", "name": "제18대 대통령선거"},
            
            # 국회의원선거
            "20240410": {"type": "2", "name": "제22대 국회의원선거"},
            "20200415": {"type": "2", "name": "제21대 국회의원선거"},
            "20160413": {"type": "2", "name": "제20대 국회의원선거"},
            "20120411": {"type": "2", "name": "제19대 국회의원선거"},
            "20080409": {"type": "2", "name": "제18대 국회의원선거"},
            
            # 지방선거
            "20220601": {"type": "3", "name": "제8회 지방선거"},
            "20180613": {"type": "3", "name": "제7회 지방선거"},
            "20140604": {"type": "3", "name": "제6회 지방선거"},
            "20100602": {"type": "3", "name": "제5회 지방선거"},
            "20060531": {"type": "3", "name": "제4회 지방선거"},
            
            # 시도지사선거
            "20220601": {"type": "4", "name": "제8회 시도지사선거"},
            "20180613": {"type": "4", "name": "제7회 시도지사선거"},
            "20140604": {"type": "4", "name": "제6회 시도지사선거"},
            "20100602": {"type": "4", "name": "제5회 시도지사선거"},
            "20060531": {"type": "4", "name": "제4회 시도지사선거"},
            
            # 시군구장선거
            "20220601": {"type": "5", "name": "제8회 시군구장선거"},
            "20180613": {"type": "5", "name": "제7회 시군구장선거"},
            "20140604": {"type": "5", "name": "제6회 시군구장선거"},
            "20100602": {"type": "5", "name": "제5회 시군구장선거"},
            "20060531": {"type": "5", "name": "제4회 시군구장선거"},
            
            # 시도의원선거
            "20220601": {"type": "6", "name": "제8회 시도의원선거"},
            "20180613": {"type": "6", "name": "제7회 시도의원선거"},
            "20140604": {"type": "6", "name": "제6회 시도의원선거"},
            "20100602": {"type": "6", "name": "제5회 시도의원선거"},
            "20060531": {"type": "6", "name": "제4회 시도의원선거"},
            
            # 시군구의원선거
            "20220601": {"type": "7", "name": "제8회 시군구의원선거"},
            "20180613": {"type": "7", "name": "제7회 시군구의원선거"},
            "20140604": {"type": "7", "name": "제6회 시군구의원선거"},
            "20100602": {"type": "7", "name": "제5회 시군구의원선거"},
            "20060531": {"type": "7", "name": "제4회 시군구의원선거"},
        }
        
        # 시도 코드 매핑
        self.sido_codes = {
            "서울특별시": "11", "부산광역시": "26", "대구광역시": "27", "인천광역시": "28",
            "광주광역시": "29", "대전광역시": "30", "울산광역시": "31", "세종특별자치시": "36",
            "경기도": "41", "강원특별자치도": "42", "충청북도": "43", "충청남도": "44",
            "전북특별자치도": "45", "전라남도": "46", "경상북도": "47", "경상남도": "48", "제주특별자치도": "50"
        }

    def get_election_candidates(self, sg_id: str, sg_type_code: str, sgg_name: str = "", sd_name: str = "", page_no: int = 1, num_of_rows: int = 1000) -> Dict[str, Any]:
        """선거 후보자 정보 조회"""
        try:
            params = {
                "serviceKey": self.api_key,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
                "sgId": sg_id,
                "sgTypecode": sg_type_code,
                "sggName": sgg_name,
                "sdName": sd_name
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # 결과 파싱
            result = {
                "resultCode": root.find(".//resultCode").text if root.find(".//resultCode") is not None else "",
                "resultMsg": root.find(".//resultMsg").text if root.find(".//resultMsg") is not None else "",
                "totalCount": int(root.find(".//totalCount").text) if root.find(".//totalCount") is not None else 0,
                "candidates": []
            }
            
            # 후보자 정보 추출
            for item in root.findall(".//item"):
                candidate = {
                    "sgId": item.find("sgId").text if item.find("sgId") is not None else "",
                    "sgTypecode": item.find("sgTypecode").text if item.find("sgTypecode") is not None else "",
                    "huboid": item.find("huboid").text if item.find("huboid") is not None else "",
                    "sggName": item.find("sggName").text if item.find("sggName") is not None else "",
                    "sdName": item.find("sdName").text if item.find("sdName") is not None else "",
                    "wiwName": item.find("wiwName").text if item.find("wiwName") is not None else "",
                    "jdName": item.find("jdName").text if item.find("jdName") is not None else "",
                    "name": item.find("name").text if item.find("name") is not None else "",
                    "hanjaName": item.find("hanjaName").text if item.find("hanjaName") is not None else "",
                    "gender": item.find("gender").text if item.find("gender") is not None else "",
                    "birthday": item.find("birthday").text if item.find("birthday") is not None else "",
                    "age": int(item.find("age").text) if item.find("age") is not None else 0,
                    "addr": item.find("addr").text if item.find("addr") is not None else "",
                    "jobId": item.find("jobId").text if item.find("jobId") is not None else "",
                    "job": item.find("job").text if item.find("job") is not None else "",
                    "eduId": item.find("eduId").text if item.find("eduId") is not None else "",
                    "edu": item.find("edu").text if item.find("edu") is not None else "",
                    "career1": item.find("career1").text if item.find("career1") is not None else "",
                    "career2": item.find("career2").text if item.find("career2") is not None else "",
                    "regdate": item.find("regdate").text if item.find("regdate") is not None else "",
                    "status": item.find("status").text if item.find("status") is not None else "",
                    "num": int(item.find("num").text) if item.find("num") is not None else 0
                }
                result["candidates"].append(candidate)
            
            return result
            
        except Exception as e:
            logger.error(f"API 호출 실패: {e}")
            return {"resultCode": "ERROR", "resultMsg": str(e), "totalCount": 0, "candidates": []}

    def collect_all_elections(self) -> Dict[str, Any]:
        """모든 선거의 후보자 정보 수집"""
        all_elections_data = {}
        
        for sg_id, election_info in self.election_mapping.items():
            logger.info(f"수집 중: {election_info['name']} ({sg_id})")
            
            election_data = {
                "election_id": sg_id,
                "election_name": election_info["name"],
                "election_type": election_info["type"],
                "regions": {}
            }
            
            # 시도별 수집
            for sido_name, sido_code in self.sido_codes.items():
                logger.info(f"  - {sido_name} 수집 중...")
                
                try:
                    result = self.get_election_candidates(
                        sg_id=sg_id,
                        sg_type_code=election_info["type"],
                        sd_name=sido_name
                    )
                    
                    if result["resultCode"] == "INFO-00":
                        election_data["regions"][sido_name] = {
                            "total_count": result["totalCount"],
                            "candidates": result["candidates"]
                        }
                        logger.info(f"    ✅ {sido_name}: {result['totalCount']}명")
                    else:
                        logger.warning(f"    ❌ {sido_name}: {result['resultMsg']}")
                    
                    # API 호출 제한 고려
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"    ❌ {sido_name} 수집 실패: {e}")
                    continue
            
            all_elections_data[sg_id] = election_data
            
            # 중간 저장
            with open(f"{self.data_dir}/election_{sg_id}.json", "w", encoding="utf-8") as f:
                json.dump(election_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ {election_info['name']} 수집 완료")
            time.sleep(1)  # API 호출 제한 고려
        
        return all_elections_data

    def create_timeline_analysis(self, all_elections_data: Dict[str, Any]) -> Dict[str, Any]:
        """시계열 분석을 위한 데이터 구조 생성"""
        timeline_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_elections": len(all_elections_data),
                "analysis_type": "election_timeline_analysis"
            },
            "timeline": [],
            "regional_analysis": {},
            "candidate_analysis": {},
            "party_analysis": {}
        }
        
        # 시간순 정렬
        sorted_elections = sorted(all_elections_data.items(), key=lambda x: x[0])
        
        for sg_id, election_data in sorted_elections:
            timeline_entry = {
                "election_id": sg_id,
                "election_name": election_data["election_name"],
                "election_type": election_data["election_type"],
                "date": sg_id,
                "total_candidates": sum(region["total_count"] for region in election_data["regions"].values()),
                "regions": {}
            }
            
            # 지역별 분석
            for region_name, region_data in election_data["regions"].items():
                timeline_entry["regions"][region_name] = {
                    "candidate_count": region_data["total_count"],
                    "parties": list(set(candidate["jdName"] for candidate in region_data["candidates"] if candidate["jdName"])),
                    "gender_distribution": self._analyze_gender_distribution(region_data["candidates"]),
                    "age_distribution": self._analyze_age_distribution(region_data["candidates"]),
                    "education_distribution": self._analyze_education_distribution(region_data["candidates"]),
                    "career_analysis": self._analyze_career_distribution(region_data["candidates"])
                }
            
            timeline_data["timeline"].append(timeline_entry)
        
        return timeline_data

    def _analyze_gender_distribution(self, candidates: List[Dict]) -> Dict[str, int]:
        """성별 분포 분석"""
        gender_count = {"남": 0, "여": 0, "기타": 0}
        for candidate in candidates:
            gender = candidate.get("gender", "기타")
            gender_count[gender] = gender_count.get(gender, 0) + 1
        return gender_count

    def _analyze_age_distribution(self, candidates: List[Dict]) -> Dict[str, int]:
        """연령대 분포 분석"""
        age_groups = {"20대": 0, "30대": 0, "40대": 0, "50대": 0, "60대": 0, "70대": 0, "80대": 0}
        for candidate in candidates:
            age = candidate.get("age", 0)
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
            elif 70 <= age < 80:
                age_groups["70대"] += 1
            elif age >= 80:
                age_groups["80대"] += 1
        return age_groups

    def _analyze_education_distribution(self, candidates: List[Dict]) -> Dict[str, int]:
        """학력 분포 분석"""
        education_count = {}
        for candidate in candidates:
            education = candidate.get("edu", "기타")
            education_count[education] = education_count.get(education, 0) + 1
        return education_count

    def _analyze_career_distribution(self, candidates: List[Dict]) -> Dict[str, int]:
        """경력 분포 분석"""
        career_count = {}
        for candidate in candidates:
            career = candidate.get("career1", "기타")
            career_count[career] = career_count.get(career, 0) + 1
        return career_count

    def create_vercel_optimized_data(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Vercel 배포 최적화된 데이터 구조 생성"""
        vercel_data = {
            "metadata": timeline_data["metadata"],
            "summary": {
                "total_elections": len(timeline_data["timeline"]),
                "total_candidates": sum(entry["total_candidates"] for entry in timeline_data["timeline"]),
                "date_range": {
                    "start": min(entry["date"] for entry in timeline_data["timeline"]),
                    "end": max(entry["date"] for entry in timeline_data["timeline"])
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
    api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
    
    collector = ElectionDataCollector(api_key)
    
    logger.info("=== 공공데이터포털 선거 데이터 수집 시작 ===")
    
    # 모든 선거 데이터 수집
    all_elections_data = collector.collect_all_elections()
    
    # 시계열 분석 데이터 생성
    timeline_data = collector.create_timeline_analysis(all_elections_data)
    
    # Vercel 최적화 데이터 생성
    vercel_data = collector.create_vercel_optimized_data(timeline_data)
    
    # 데이터 저장
    output_file = collector.save_vercel_data(vercel_data)
    
    logger.info("=== 선거 데이터 수집 완료 ===")
    logger.info(f"출력 파일: {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()
