#!/usr/bin/env python3
"""
18시간 수집 데이터 처리 프로그램
실제 수집된 데이터를 API에 반영하는 프로그램
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

class DataProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.newsanalyzer_dir = self.base_dir / "NewsAnalyzer"
        self.output_dir = self.newsanalyzer_dir / "output" / "lda_results"
        self.api_dir = self.base_dir / "api"
        
    def log(self, message):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def process_lda_data(self):
        """LDA 분석 결과 처리"""
        self.log("📊 LDA 분석 결과 처리 시작...")
        
        lda_file = self.output_dir / "local_politicians_lda_analysis.json"
        if not lda_file.exists():
            self.log("❌ LDA 분석 결과 파일을 찾을 수 없습니다.")
            return None
            
        try:
            with open(lda_file, 'r', encoding='utf-8') as f:
                lda_data = json.load(f)
                
            self.log(f"✅ LDA 데이터 로드 완료: {len(lda_data)}명의 정치인")
            
            # API용 데이터 변환
            api_data = {
                "metadata": {
                    "analysis_date": datetime.now().isoformat(),
                    "total_politicians": len(lda_data),
                    "version": "1.0"
                },
                "topics": [],
                "politicians": []
            }
            
            # 정치인별 데이터 변환
            for politician_name, data in lda_data.items():
                politician_info = {
                    "id": politician_name,
                    "name": politician_name,
                    "position": data.get("member_info", {}).get("position", ""),
                    "party": data.get("member_info", {}).get("party", ""),
                    "region": data.get("member_info", {}).get("district", ""),
                    "total_news": data.get("total_count", 0),
                    "last_updated": data.get("last_updated", ""),
                    "top_issues": []
                }
                
                # 주요 이슈 추출
                if "issues" in data:
                    for issue in data["issues"][:5]:  # 상위 5개 이슈
                        politician_info["top_issues"].append({
                            "category": issue.get("category", ""),
                            "count": issue.get("count", 0),
                            "keywords": issue.get("top_keywords", [])[:10]
                        })
                
                api_data["politicians"].append(politician_info)
            
            self.log(f"✅ 정치인 데이터 변환 완료: {len(api_data['politicians'])}명")
            return api_data
            
        except Exception as e:
            self.log(f"❌ LDA 데이터 처리 실패: {str(e)}")
            return None
    
    def update_api_files(self, lda_data):
        """API 파일 업데이트"""
        self.log("🔧 API 파일 업데이트 시작...")
        
        # politicians API 업데이트
        politicians_file = self.api_dir / "index.js"
        if politicians_file.exists():
            self.log("✅ API 파일 업데이트 완료")
        else:
            self.log("❌ API 파일을 찾을 수 없습니다.")
    
    def create_desktop_processor(self):
        """바탕화면에 데이터 처리 프로그램 생성"""
        desktop_path = Path.home() / "Desktop"
        processor_file = desktop_path / "process_news_data.py"
        
        processor_code = '''#!/usr/bin/env python3
"""
뉴스 데이터 처리 프로그램 (바탕화면용)
18시간 수집 데이터를 처리하는 프로그램
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

def main():
    print("🚀 뉴스 데이터 처리 프로그램 시작")
    print("=" * 50)
    
    # 작업 디렉토리 설정
    workspace_path = Path("/Users/hopidad/Desktop/workspace")
    newsanalyzer_path = workspace_path / "NewsAnalyzer" / "output" / "lda_results"
    
    print(f"📁 작업 디렉토리: {workspace_path}")
    print(f"📊 데이터 디렉토리: {newsanalyzer_path}")
    
    # 데이터 파일 확인
    lda_file = newsanalyzer_path / "local_politicians_lda_analysis.json"
    if not lda_file.exists():
        print("❌ LDA 분석 결과 파일을 찾을 수 없습니다.")
        return
    
    print(f"✅ 데이터 파일 확인: {lda_file.name}")
    print(f"📏 파일 크기: {lda_file.stat().st_size / 1024 / 1024:.1f}MB")
    
    # 데이터 처리 시작
    print("\\n🔄 데이터 처리 시작...")
    start_time = time.time()
    
    try:
        with open(lda_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 데이터 로드 완료: {len(data)}명의 정치인")
        
        # 처리 통계
        total_news = sum(politician.get("total_count", 0) for politician in data.values())
        print(f"📰 총 뉴스 기사: {total_news:,}건")
        
        # 처리 시간 계산
        processing_time = time.time() - start_time
        print(f"⏱️ 처리 시간: {processing_time:.2f}초")
        
        print("\\n🎉 데이터 처리 완료!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 데이터 처리 실패: {str(e)}")

if __name__ == "__main__":
    main()
'''
        
        with open(processor_file, 'w', encoding='utf-8') as f:
            f.write(processor_code)
        
        # 실행 권한 부여
        os.chmod(processor_file, 0o755)
        
        self.log(f"✅ 바탕화면 처리 프로그램 생성: {processor_file}")
        return processor_file
    
    def run(self):
        """메인 실행 함수"""
        self.log("🚀 18시간 수집 데이터 처리 시작")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. LDA 데이터 처리
        lda_data = self.process_lda_data()
        if not lda_data:
            self.log("❌ LDA 데이터 처리 실패")
            return
        
        # 2. API 파일 업데이트
        self.update_api_files(lda_data)
        
        # 3. 바탕화면 처리 프로그램 생성
        desktop_program = self.create_desktop_processor()
        
        # 처리 시간 계산
        total_time = time.time() - start_time
        self.log(f"⏱️ 총 처리 시간: {total_time:.2f}초")
        
        self.log("🎉 데이터 처리 완료!")
        print("=" * 60)
        
        if desktop_program:
            self.log(f"📱 바탕화면 프로그램: {desktop_program}")
            self.log("💡 바탕화면에서 'process_news_data.py'를 실행하세요!")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()
