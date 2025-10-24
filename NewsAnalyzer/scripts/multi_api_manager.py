#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-API Manager for NewsAnalyzer
3개의 네이버 API 계정을 로테이션하여 사용하는 시스템
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import threading
import queue

@dataclass
class APIAccount:
    id: str
    client_id: str
    client_secret: str
    daily_limit: int
    enabled: bool
    priority: int
    description: str
    used_today: int = 0
    last_reset: str = None

class MultiAPIManager:
    def __init__(self, config_path: str = "multi_api_config.json"):
        self.config_path = config_path
        self.accounts: List[APIAccount] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.usage_log = []
        self.load_config()
        self.setup_logging()
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/multi_api_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.accounts = []
            for account_config in config['api_accounts']:
                account = APIAccount(**account_config)
                self.accounts.append(account)
                
            self.collection_settings = config['collection_settings']
            self.monitoring = config['monitoring']
            
            # 사용량 로그 로드
            self.load_usage_log()
            
            self.logger.info(f"✅ {len(self.accounts)}개 API 계정 로드 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 설정 로드 실패: {e}")
            raise
            
    def load_usage_log(self):
        """사용량 로그 로드"""
        try:
            with open('data/api_usage_log.json', 'r', encoding='utf-8') as f:
                self.usage_log = json.load(f)
        except FileNotFoundError:
            self.usage_log = []
            
    def save_usage_log(self):
        """사용량 로그 저장"""
        try:
            with open('data/api_usage_log.json', 'w', encoding='utf-8') as f:
                json.dump(self.usage_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"❌ 사용량 로그 저장 실패: {e}")
            
    def get_available_account(self) -> Optional[APIAccount]:
        """사용 가능한 API 계정 반환"""
        with self.lock:
            # 활성화된 계정 중 사용량이 한도 미만인 계정 찾기
            available_accounts = [
                account for account in self.accounts 
                if account.enabled and account.used_today < account.daily_limit
            ]
            
            if not available_accounts:
                return None
                
            # 우선순위별로 정렬
            available_accounts.sort(key=lambda x: x.priority)
            
            # 라운드 로빈 방식으로 선택
            if self.current_index >= len(available_accounts):
                self.current_index = 0
                
            selected_account = available_accounts[self.current_index]
            self.current_index += 1
            
            return selected_account
            
    def make_api_call(self, query: str, display: int = 100, start: int = 1, sort: str = "sim") -> Tuple[bool, Dict, Optional[str]]:
        """API 호출 실행"""
        account = self.get_available_account()
        
        if not account:
            self.logger.warning("⚠️ 사용 가능한 API 계정이 없습니다")
            return False, {}, "NO_AVAILABLE_ACCOUNT"
            
        try:
            # API 호출
            url = "https://openapi.naver.com/v1/search/news.json"
            headers = {
                "X-Naver-Client-Id": account.client_id,
                "X-Naver-Client-Secret": account.client_secret
            }
            params = {
                "query": query,
                "display": display,
                "start": start,
                "sort": sort
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            # 사용량 업데이트
            with self.lock:
                account.used_today += 1
                
            # 사용량 로그 기록
            self.log_usage(account.id, query, response.status_code)
            
            if response.status_code == 200:
                self.logger.info(f"✅ API 호출 성공 (계정: {account.id}, 사용량: {account.used_today}/{account.daily_limit})")
                return True, response.json(), None
            else:
                self.logger.error(f"❌ API 호출 실패 (계정: {account.id}, 상태코드: {response.status_code})")
                return False, {}, f"HTTP_{response.status_code}"
                
        except Exception as e:
            self.logger.error(f"❌ API 호출 중 오류 (계정: {account.id}): {e}")
            return False, {}, str(e)
            
    def log_usage(self, account_id: str, query: str, status_code: int):
        """사용량 로그 기록"""
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "account_id": account_id,
            "query": query,
            "status_code": status_code,
            "total_used": sum(account.used_today for account in self.accounts)
        }
        
        self.usage_log.append(usage_entry)
        
        # 로그 파일 크기 제한 (최근 1000개만 유지)
        if len(self.usage_log) > 1000:
            self.usage_log = self.usage_log[-1000:]
            
    def get_usage_summary(self) -> Dict:
        """사용량 요약 반환"""
        total_used = sum(account.used_today for account in self.accounts)
        total_limit = sum(account.daily_limit for account in self.accounts)
        
        account_summary = []
        for account in self.accounts:
            account_summary.append({
                "id": account.id,
                "description": account.description,
                "used": account.used_today,
                "limit": account.daily_limit,
                "remaining": account.daily_limit - account.used_today,
                "enabled": account.enabled
            })
            
        return {
            "total_used": total_used,
            "total_limit": total_limit,
            "remaining": total_limit - total_used,
            "accounts": account_summary,
            "last_updated": datetime.now().isoformat()
        }
        
    def reset_daily_usage(self):
        """일일 사용량 리셋"""
        with self.lock:
            for account in self.accounts:
                account.used_today = 0
                account.last_reset = datetime.now().isoformat()
                
        self.logger.info("🔄 일일 사용량 리셋 완료")
        
    def add_api_account(self, account_config: Dict):
        """새 API 계정 추가"""
        with self.lock:
            new_account = APIAccount(**account_config)
            self.accounts.append(new_account)
            
        self.logger.info(f"✅ 새 API 계정 추가: {new_account.id}")
        
    def remove_api_account(self, account_id: str):
        """API 계정 제거"""
        with self.lock:
            self.accounts = [account for account in self.accounts if account.id != account_id]
            
        self.logger.info(f"✅ API 계정 제거: {account_id}")
        
    def update_api_account(self, account_id: str, updates: Dict):
        """API 계정 정보 업데이트"""
        with self.lock:
            for account in self.accounts:
                if account.id == account_id:
                    for key, value in updates.items():
                        setattr(account, key, value)
                    break
                    
        self.logger.info(f"✅ API 계정 업데이트: {account_id}")
        
    def save_config(self):
        """설정 파일 저장"""
        try:
            config = {
                "api_accounts": [
                    {
                        "id": account.id,
                        "client_id": account.client_id,
                        "client_secret": account.client_secret,
                        "daily_limit": account.daily_limit,
                        "enabled": account.enabled,
                        "priority": account.priority,
                        "description": account.description
                    }
                    for account in self.accounts
                ],
                "collection_settings": self.collection_settings,
                "monitoring": self.monitoring
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            self.logger.info("✅ 설정 파일 저장 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 설정 파일 저장 실패: {e}")
            
    def monitor_usage(self):
        """사용량 모니터링"""
        while True:
            try:
                # 사용량 요약 생성
                summary = self.get_usage_summary()
                
                # 사용량 로그 저장
                self.save_usage_log()
                
                # 한도 임계치 체크 (80% 이상 사용시 경고)
                if summary["total_used"] > summary["total_limit"] * 0.8:
                    self.logger.warning(f"⚠️ API 사용량이 80% 이상: {summary['total_used']}/{summary['total_limit']}")
                
                # 일일 리셋 체크
                now = datetime.now()
                if now.hour == 0 and now.minute == 0:
                    self.reset_daily_usage()
                    
                time.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                self.logger.error(f"❌ 모니터링 오류: {e}")
                time.sleep(60)

if __name__ == "__main__":
    # 테스트 코드
    manager = MultiAPIManager()
    
    # 사용량 요약 출력
    summary = manager.get_usage_summary()
    print("📊 API 사용량 요약:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
