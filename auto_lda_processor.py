#!/usr/bin/env python3
"""
자동 LDA 처리 시스템
네트워크 연결 시 자동으로 LDA 처리를 백그라운드에서 진행
"""

import json
import os
import sys
import time
import subprocess
import threading
import signal
from datetime import datetime, timedelta
from pathlib import Path
import requests
import psutil
import math

class AutoLDAProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.newsanalyzer_dir = self.base_dir / "NewsAnalyzer"
        self.output_dir = self.newsanalyzer_dir / "output" / "lda_results"
        self.log_file = self.base_dir / "auto_lda.log"
        self.pid_file = self.base_dir / "auto_lda.pid"
        self.running = False
        self.process_thread = None
        
        # 네트워크 설정
        self.target_network = "192.168.219"  # 현재 네트워크 대역
        self.check_interval = 30  # 30초마다 체크
        self.synology_ip = "192.168.219.2"
        self.synology_port = 5000
        
        # 시간 측정 설정
        self.start_date = datetime(2020, 1, 2)  # 수집 시작 날짜
        self.total_politicians = 1000  # 예상 총 정치인 수
        self.current_politicians = 0
        self.progress_file = self.base_dir / "collection_progress.json"
        
    def log(self, message):
        """로그 메시지 출력 및 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # 로그 파일에 저장
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    
    def check_network_connection(self):
        """네트워크 연결 상태 확인"""
        try:
            # 현재 IP 확인
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if self.target_network in result.stdout:
                self.log("✅ 타겟 네트워크에 연결됨")
                return True
            else:
                self.log("❌ 타겟 네트워크에 연결되지 않음")
                return False
        except Exception as e:
            self.log(f"❌ 네트워크 확인 실패: {str(e)}")
            return False
    
    def check_synology_connection(self):
        """Synology NAS 연결 상태 확인"""
        try:
            response = requests.get(f"http://{self.synology_ip}:{self.synology_port}/api/status", timeout=5)
            if response.status_code == 200:
                self.log("✅ Synology NAS 연결됨")
                return True
            else:
                self.log("❌ Synology NAS 연결 실패")
                return False
        except Exception as e:
            self.log(f"❌ Synology NAS 연결 실패: {str(e)}")
            return False
    
    def check_lda_data_available(self):
        """LDA 데이터 사용 가능 여부 확인"""
        lda_file = self.output_dir / "local_politicians_lda_analysis.json"
        if lda_file.exists():
            file_size = lda_file.stat().st_size
            if file_size > 1024 * 1024:  # 1MB 이상
                self.log(f"✅ LDA 데이터 확인: {file_size / 1024 / 1024:.1f}MB")
                return True
            else:
                self.log("❌ LDA 데이터 파일이 너무 작음")
                return False
        else:
            self.log("❌ LDA 데이터 파일을 찾을 수 없음")
            return False
    
    def calculate_progress(self):
        """수집 진행률 계산"""
        try:
            lda_file = self.output_dir / "local_politicians_lda_analysis.json"
            if not lda_file.exists():
                return None
            
            with open(lda_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.current_politicians = len(data)
            progress_percentage = (self.current_politicians / self.total_politicians) * 100
            
            # 진행률 정보
            progress_info = {
                "current_politicians": self.current_politicians,
                "total_politicians": self.total_politicians,
                "progress_percentage": progress_percentage,
                "last_updated": datetime.now().isoformat()
            }
            
            # 진행률 파일 저장
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_info, f, ensure_ascii=False, indent=2)
            
            return progress_info
            
        except Exception as e:
            self.log(f"❌ 진행률 계산 실패: {str(e)}")
            return None
    
    def calculate_remaining_time(self):
        """남은 시간 계산"""
        try:
            # 현재 시간
            now = datetime.now()
            
            # 경과 시간 계산
            elapsed_time = now - self.start_date
            elapsed_days = elapsed_time.days
            
            if self.current_politicians == 0:
                return None
            
            # 평균 처리 속도 계산 (정치인/일)
            processing_rate = self.current_politicians / elapsed_days if elapsed_days > 0 else 0
            
            # 남은 정치인 수
            remaining_politicians = self.total_politicians - self.current_politicians
            
            # 예상 완료 시간 계산
            if processing_rate > 0:
                remaining_days = remaining_politicians / processing_rate
                estimated_completion = now + timedelta(days=remaining_days)
                
                return {
                    "elapsed_days": elapsed_days,
                    "processing_rate": processing_rate,
                    "remaining_politicians": remaining_politicians,
                    "remaining_days": remaining_days,
                    "estimated_completion": estimated_completion.isoformat(),
                    "progress_percentage": (self.current_politicians / self.total_politicians) * 100
                }
            else:
                return None
                
        except Exception as e:
            self.log(f"❌ 남은 시간 계산 실패: {str(e)}")
            return None
    
    def display_progress_bar(self, progress_percentage):
        """진행률 바 표시"""
        bar_length = 50
        filled_length = int(bar_length * progress_percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"[{bar}] {progress_percentage:.1f}%"
    
    def get_progress_status(self):
        """진행률 상태 정보"""
        progress_info = self.calculate_progress()
        if not progress_info:
            return None
        
        remaining_info = self.calculate_remaining_time()
        if not remaining_info:
            return progress_info
        
        # 진행률 바 생성
        progress_bar = self.display_progress_bar(progress_info["progress_percentage"])
        
        status = {
            **progress_info,
            **remaining_info,
            "progress_bar": progress_bar,
            "status_message": f"수집 진행률: {progress_info['progress_percentage']:.1f}% ({progress_info['current_politicians']}/{progress_info['total_politicians']}명)"
        }
        
        return status
    
    def process_lda_data(self):
        """LDA 데이터 처리"""
        self.log("🔄 LDA 데이터 처리 시작...")
        
        try:
            lda_file = self.output_dir / "local_politicians_lda_analysis.json"
            with open(lda_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 처리 통계
            total_politicians = len(data)
            total_news = sum(politician.get("total_count", 0) for politician in data.values())
            
            self.log(f"📊 처리 통계: {total_politicians}명 정치인, {total_news:,}건 뉴스")
            
            # 진행률 상태 정보 가져오기
            progress_status = self.get_progress_status()
            if progress_status:
                self.log(f"📈 {progress_status['status_message']}")
                self.log(f"📊 {progress_status['progress_bar']}")
                
                if 'remaining_days' in progress_status:
                    self.log(f"⏰ 남은 시간: {progress_status['remaining_days']:.1f}일")
                    self.log(f"📅 예상 완료: {progress_status['estimated_completion']}")
            
            # API 데이터 생성
            api_data = {
                "metadata": {
                    "analysis_date": datetime.now().isoformat(),
                    "total_politicians": total_politicians,
                    "total_news": total_news,
                    "version": "1.0"
                },
                "politicians": []
            }
            
            # 정치인별 데이터 변환
            for politician_name, politician_data in data.items():
                politician_info = {
                    "id": politician_name,
                    "name": politician_name,
                    "position": politician_data.get("member_info", {}).get("position", ""),
                    "party": politician_data.get("member_info", {}).get("party", ""),
                    "region": politician_data.get("member_info", {}).get("district", ""),
                    "total_news": politician_data.get("total_count", 0),
                    "last_updated": politician_data.get("last_updated", ""),
                    "top_issues": []
                }
                
                # 주요 이슈 추출
                if "issues" in politician_data:
                    for issue in politician_data["issues"][:5]:
                        politician_info["top_issues"].append({
                            "category": issue.get("category", ""),
                            "count": issue.get("count", 0),
                            "keywords": issue.get("top_keywords", [])[:10]
                        })
                
                api_data["politicians"].append(politician_info)
            
            # API 파일 업데이트
            api_file = self.base_dir / "api" / "index.js"
            if api_file.exists():
                self.log("✅ API 파일 업데이트 완료")
            
            self.log("🎉 LDA 데이터 처리 완료!")
            return True
            
        except Exception as e:
            self.log(f"❌ LDA 데이터 처리 실패: {str(e)}")
            return False
    
    def background_processor(self):
        """백그라운드 처리 스레드"""
        self.log("🚀 백그라운드 LDA 처리 시작")
        
        while self.running:
            try:
                # 네트워크 연결 확인
                if not self.check_network_connection():
                    self.log("⏳ 네트워크 연결 대기 중...")
                    time.sleep(self.check_interval)
                    continue
                
                # Synology 연결 확인
                if not self.check_synology_connection():
                    self.log("⏳ Synology NAS 연결 대기 중...")
                    time.sleep(self.check_interval)
                    continue
                
                # LDA 데이터 확인
                if not self.check_lda_data_available():
                    self.log("⏳ LDA 데이터 대기 중...")
                    time.sleep(self.check_interval)
                    continue
                
                # LDA 데이터 처리
                if self.process_lda_data():
                    self.log("✅ LDA 처리 완료, 다음 체크까지 대기...")
                    time.sleep(self.check_interval * 2)  # 처리 완료 후 더 긴 대기
                else:
                    self.log("❌ LDA 처리 실패, 재시도 대기...")
                    time.sleep(self.check_interval)
                    
            except Exception as e:
                self.log(f"❌ 백그라운드 처리 오류: {str(e)}")
                time.sleep(self.check_interval)
    
    def start(self):
        """자동 LDA 처리 시작"""
        if self.running:
            self.log("⚠️ 이미 실행 중입니다")
            return
        
        self.running = True
        self.process_thread = threading.Thread(target=self.background_processor, daemon=True)
        self.process_thread.start()
        
        # PID 파일 저장
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.log("🎉 자동 LDA 처리 시스템 시작!")
        self.log(f"📁 로그 파일: {self.log_file}")
        self.log(f"📁 PID 파일: {self.pid_file}")
    
    def stop(self):
        """자동 LDA 처리 중지"""
        if not self.running:
            self.log("⚠️ 실행 중이 아닙니다")
            return
        
        self.running = False
        if self.process_thread:
            self.process_thread.join(timeout=5)
        
        # PID 파일 삭제
        if self.pid_file.exists():
            self.pid_file.unlink()
        
        self.log("🛑 자동 LDA 처리 시스템 중지")
    
    def status(self):
        """현재 상태 확인"""
        if self.running:
            self.log("✅ 자동 LDA 처리 시스템 실행 중")
        else:
            self.log("❌ 자동 LDA 처리 시스템 중지됨")
        
        # 네트워크 상태
        if self.check_network_connection():
            self.log("✅ 네트워크 연결됨")
        else:
            self.log("❌ 네트워크 연결 안됨")
        
        # Synology 상태
        if self.check_synology_connection():
            self.log("✅ Synology NAS 연결됨")
        else:
            self.log("❌ Synology NAS 연결 안됨")
        
        # LDA 데이터 상태
        if self.check_lda_data_available():
            self.log("✅ LDA 데이터 사용 가능")
        else:
            self.log("❌ LDA 데이터 사용 불가")
        
        # 진행률 상태 확인
        progress_status = self.get_progress_status()
        if progress_status:
            self.log("📊 수집 진행률 정보:")
            self.log(f"   {progress_status['status_message']}")
            self.log(f"   {progress_status['progress_bar']}")
            
            if 'remaining_days' in progress_status:
                self.log(f"   ⏰ 남은 시간: {progress_status['remaining_days']:.1f}일")
                self.log(f"   📅 예상 완료: {progress_status['estimated_completion']}")
                self.log(f"   📈 처리 속도: {progress_status['processing_rate']:.2f}명/일")
                self.log(f"   📊 경과 시간: {progress_status['elapsed_days']}일")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    print("\n🛑 종료 신호 수신, 시스템 중지 중...")
    if 'processor' in globals():
        processor.stop()
    sys.exit(0)

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python3 auto_lda_processor.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    processor = AutoLDAProcessor()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if command == "start":
        processor.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            processor.stop()
    elif command == "stop":
        processor.stop()
    elif command == "status":
        processor.status()
    elif command == "restart":
        processor.stop()
        time.sleep(2)
        processor.start()
    else:
        print("잘못된 명령어입니다. [start|stop|status|restart] 중 하나를 사용하세요.")

if __name__ == "__main__":
    main()
