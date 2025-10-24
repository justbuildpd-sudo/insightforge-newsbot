#!/usr/bin/env python3
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
    print("\n🔄 데이터 처리 시작...")
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
        
        print("\n🎉 데이터 처리 완료!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 데이터 처리 실패: {str(e)}")

if __name__ == "__main__":
    main()
