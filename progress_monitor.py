#!/usr/bin/env python3
"""
수집 진행률 모니터링 프로그램
실시간 진행률과 남은 시간을 표시하는 독립 프로그램
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class ProgressMonitor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.newsanalyzer_dir = self.base_dir / "NewsAnalyzer"
        self.output_dir = self.newsanalyzer_dir / "output" / "lda_results"
        self.progress_file = self.base_dir / "collection_progress.json"
        
        # 수집 설정
        self.start_date = datetime(2020, 1, 2)
        self.total_politicians = 1000
        
    def get_current_data(self):
        """현재 데이터 상태 확인"""
        lda_file = self.output_dir / "local_politicians_lda_analysis.json"
        if not lda_file.exists():
            return None
        
        try:
            with open(lda_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "current_politicians": len(data),
                "total_news": sum(politician.get("total_count", 0) for politician in data.values()),
                "file_size": lda_file.stat().st_size
            }
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {str(e)}")
            return None
    
    def calculate_progress(self):
        """진행률 계산"""
        data = self.get_current_data()
        if not data:
            return None
        
        current_politicians = data["current_politicians"]
        progress_percentage = (current_politicians / self.total_politicians) * 100
        
        # 경과 시간 계산
        now = datetime.now()
        elapsed_time = now - self.start_date
        elapsed_days = elapsed_time.days
        
        # 처리 속도 계산
        processing_rate = current_politicians / elapsed_days if elapsed_days > 0 else 0
        
        # 남은 시간 계산
        remaining_politicians = self.total_politicians - current_politicians
        remaining_days = remaining_politicians / processing_rate if processing_rate > 0 else 0
        estimated_completion = now + timedelta(days=remaining_days)
        
        return {
            "current_politicians": current_politicians,
            "total_politicians": self.total_politicians,
            "progress_percentage": progress_percentage,
            "total_news": data["total_news"],
            "file_size_mb": data["file_size"] / 1024 / 1024,
            "elapsed_days": elapsed_days,
            "processing_rate": processing_rate,
            "remaining_politicians": remaining_politicians,
            "remaining_days": remaining_days,
            "estimated_completion": estimated_completion,
            "last_updated": now.isoformat()
        }
    
    def display_progress_bar(self, progress_percentage):
        """진행률 바 표시"""
        bar_length = 50
        filled_length = int(bar_length * progress_percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"[{bar}] {progress_percentage:.1f}%"
    
    def format_time(self, days):
        """시간 포맷팅"""
        if days < 1:
            return f"{days * 24:.1f}시간"
        elif days < 30:
            return f"{days:.1f}일"
        elif days < 365:
            months = days / 30
            return f"{months:.1f}개월"
        else:
            years = days / 365
            return f"{years:.1f}년"
    
    def display_status(self):
        """상태 표시"""
        progress = self.calculate_progress()
        if not progress:
            print("❌ 진행률 정보를 가져올 수 없습니다.")
            return
        
        print("=" * 60)
        print("📊 수집 진행률 모니터")
        print("=" * 60)
        
        # 기본 정보
        print(f"📅 시작 날짜: {self.start_date.strftime('%Y-%m-%d')}")
        print(f"📅 현재 날짜: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"⏰ 경과 시간: {self.format_time(progress['elapsed_days'])}")
        print()
        
        # 진행률 정보
        print("📈 수집 진행률:")
        print(f"   {self.display_progress_bar(progress['progress_percentage'])}")
        print(f"   정치인: {progress['current_politicians']:,}/{progress['total_politicians']:,}명")
        print(f"   뉴스: {progress['total_news']:,}건")
        print(f"   파일 크기: {progress['file_size_mb']:.1f}MB")
        print()
        
        # 처리 속도
        print("📊 처리 속도:")
        print(f"   평균: {progress['processing_rate']:.2f}명/일")
        print(f"   주간: {progress['processing_rate'] * 7:.1f}명/주")
        print(f"   월간: {progress['processing_rate'] * 30:.1f}명/월")
        print()
        
        # 남은 시간
        if progress['remaining_days'] > 0:
            print("⏰ 남은 시간:")
            print(f"   남은 정치인: {progress['remaining_politicians']:,}명")
            print(f"   예상 완료: {self.format_time(progress['remaining_days'])}")
            print(f"   완료 날짜: {progress['estimated_completion'].strftime('%Y-%m-%d')}")
        else:
            print("🎉 수집 완료!")
        
        print("=" * 60)
        print(f"🕐 마지막 업데이트: {progress['last_updated']}")
        print("=" * 60)
    
    def monitor_continuous(self, interval=30):
        """연속 모니터링"""
        print("🔄 연속 모니터링 시작 (Ctrl+C로 중지)")
        print(f"⏰ 업데이트 간격: {interval}초")
        print()
        
        try:
            while True:
                # 화면 클리어 (터미널에서만)
                import os
                os.system('clear' if os.name == 'posix' else 'cls')
                
                self.display_status()
                
                print(f"\n⏳ {interval}초 후 업데이트...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 모니터링 중지됨")

def main():
    """메인 함수"""
    import sys
    
    monitor = ProgressMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # 연속 모니터링
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.monitor_continuous(interval)
    else:
        # 한 번만 표시
        monitor.display_status()

if __name__ == "__main__":
    main()
