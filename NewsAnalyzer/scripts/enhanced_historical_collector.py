#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Historical News Collector with Multi-API Support
3개의 네이버 API 계정을 사용하여 하루 종일 수집하는 시스템
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys
from multi_api_manager import MultiAPIManager

class EnhancedHistoricalCollector:
    def __init__(self):
        self.setup_logging()
        self.api_manager = MultiAPIManager()
        self.load_config()
        self.load_state()
        
    def setup_logging(self):
        """로깅 설정"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/enhanced_historical_collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """설정 로드"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.logger.error("❌ config.json 파일을 찾을 수 없습니다")
            sys.exit(1)
            
    def load_state(self):
        """상태 로드"""
        try:
            with open('data/collection_state.json', 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {
                "current_phase": 1,
                "current_date": "2020-01-01",
                "total_api_calls_today": 0,
                "completed_dates": [],
                "last_run_date": datetime.now().strftime("%Y-%m-%d"),
                "politicians_completed": []
            }
            
    def save_state(self):
        """상태 저장"""
        os.makedirs('data', exist_ok=True)
        with open('data/collection_state.json', 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
            
    def load_politicians(self, phase: int) -> List[Dict]:
        """정치인 목록 로드"""
        try:
            filename = f"data/phase{phase}_politicians.json"
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"❌ {filename} 파일을 찾을 수 없습니다")
            return []
            
    def collect_news_for_politician(self, politician: Dict, date: str) -> bool:
        """특정 정치인의 뉴스 수집"""
        name = politician.get('name', '')
        if not name:
            return False
            
        # 검색 쿼리 생성
        query = f'"{name}"'
        
        # API 호출
        success, data, error = self.api_manager.make_api_call(query)
        
        if not success:
            self.logger.warning(f"⚠️ {name} 뉴스 수집 실패: {error}")
            return False
            
        # 결과 저장
        self.save_news_data(politician, date, data)
        return True
        
    def save_news_data(self, politician: Dict, date: str, data: Dict):
        """뉴스 데이터 저장"""
        os.makedirs('output/historical', exist_ok=True)
        
        filename = f"output/historical/{politician['name']}_{date}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "politician": politician,
                "date": date,
                "news_data": data,
                "collected_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
    def run_collection_cycle(self):
        """수집 사이클 실행"""
        self.logger.info("🚀 Enhanced Historical News Collector 시작")
        
        # 현재 상태 확인
        current_phase = self.state.get('current_phase', 1)
        current_date = self.state.get('current_date', '2020-01-01')
        
        self.logger.info(f"📊 현재 Phase: {current_phase}")
        self.logger.info(f"📅 수집 날짜: {current_date}")
        
        # API 사용량 확인
        usage_summary = self.api_manager.get_usage_summary()
        self.logger.info(f"🔢 API 사용량: {usage_summary['total_used']}/{usage_summary['total_limit']}")
        
        # 정치인 목록 로드
        politicians = self.load_politicians(current_phase)
        if not politicians:
            self.logger.error("❌ 정치인 목록을 로드할 수 없습니다")
            return
            
        self.logger.info(f"👥 대상: {len(politicians)}명")
        
        # 수집 시작
        start_time = time.time()
        success_count = 0
        
        for i, politician in enumerate(politicians):
            # API 사용량 체크
            if usage_summary['total_used'] >= usage_summary['total_limit']:
                self.logger.warning("⚠️ API 사용량 한도 도달")
                break
                
            # 뉴스 수집
            if self.collect_news_for_politician(politician, current_date):
                success_count += 1
                
            # 진행 상황 로그
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                eta = (elapsed / (i + 1)) * (len(politicians) - i - 1)
                self.logger.info(f"  [{i+1}/{len(politicians)}] 진행 중... (성공: {success_count}명, ETA: {eta/60:.1f}분)")
                
            # 요청 간격
            time.sleep(self.config.get('delay_between_requests', 0.1))
            
        # 결과 저장
        self.state['completed_dates'].append(current_date)
        self.state['total_api_calls_today'] = usage_summary['total_used']
        
        # 다음 날짜 설정
        next_date = (datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        self.state['current_date'] = next_date
        
        # Phase 업데이트 (2025년 도달시)
        if next_date.startswith('2025-'):
            self.state['current_phase'] = min(current_phase + 1, 4)
            
        self.save_state()
        
        # 결과 로그
        elapsed = time.time() - start_time
        self.logger.info(f"⏱️ 소요 시간: {elapsed/60:.1f}분")
        self.logger.info(f"🔢 API 호출: {usage_summary['total_used']}건")
        self.logger.info(f"✅ 성공: {success_count}명")
        self.logger.info(f"📅 다음 수집 날짜: {next_date}")
        
    def run_continuous_collection(self):
        """연속 수집 실행"""
        self.logger.info("🔄 연속 수집 모드 시작")
        
        while True:
            try:
                # API 사용량 확인
                usage_summary = self.api_manager.get_usage_summary()
                
                if usage_summary['total_used'] >= usage_summary['total_limit']:
                    self.logger.info("⏸️ API 사용량 한도 도달, 대기 중...")
                    time.sleep(3600)  # 1시간 대기
                    continue
                    
                # 수집 사이클 실행
                self.run_collection_cycle()
                
                # 잠시 대기
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ 사용자에 의해 중단됨")
                break
            except Exception as e:
                self.logger.error(f"❌ 오류 발생: {e}")
                time.sleep(300)  # 5분 대기 후 재시도
                
    def add_api_account(self, account_config: Dict):
        """새 API 계정 추가"""
        self.api_manager.add_api_account(account_config)
        self.api_manager.save_config()
        self.logger.info("✅ 새 API 계정 추가 완료")
        
    def remove_api_account(self, account_id: str):
        """API 계정 제거"""
        self.api_manager.remove_api_account(account_id)
        self.api_manager.save_config()
        self.logger.info(f"✅ API 계정 제거 완료: {account_id}")
        
    def update_api_account(self, account_id: str, updates: Dict):
        """API 계정 업데이트"""
        self.api_manager.update_api_account(account_id, updates)
        self.api_manager.save_config()
        self.logger.info(f"✅ API 계정 업데이트 완료: {account_id}")

if __name__ == "__main__":
    collector = EnhancedHistoricalCollector()
    
    # 연속 수집 실행
    collector.run_continuous_collection()
