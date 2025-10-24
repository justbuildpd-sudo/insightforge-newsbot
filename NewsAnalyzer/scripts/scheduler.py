#!/usr/bin/env python3
"""
스케줄러 - 매일 정해진 시간에 뉴스 수집 및 LDA 분석 실행
"""

import schedule
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / 'config.json'
LOG_DIR = BASE_DIR / 'logs'

LOG_DIR.mkdir(parents=True, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_config():
    """설정 파일 로드"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_collector():
    """뉴스 수집 실행"""
    logger.info("=" * 50)
    logger.info("뉴스 수집 시작")
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/collector.py'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=3600  # 1시간 타임아웃
        )
        
        if result.returncode == 0:
            logger.info("✅ 뉴스 수집 완료")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ 뉴스 수집 실패: {result.stderr}")
    
    except Exception as e:
        logger.error(f"❌ 뉴스 수집 오류: {e}")

def run_analyzer():
    """LDA 분석 실행"""
    logger.info("=" * 50)
    logger.info("LDA 분석 시작")
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/lda_analyzer.py'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=7200  # 2시간 타임아웃
        )
        
        if result.returncode == 0:
            logger.info("✅ LDA 분석 완료")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ LDA 분석 실패: {result.stderr}")
    
    except Exception as e:
        logger.error(f"❌ LDA 분석 오류: {e}")

def run_uploader():
    """InsightForge 업데이트 실행"""
    logger.info("=" * 50)
    logger.info("InsightForge 업데이트 시작")
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/uploader.py'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=600  # 10분 타임아웃
        )
        
        if result.returncode == 0:
            logger.info("✅ 업데이트 완료")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ 업데이트 실패: {result.stderr}")
    
    except Exception as e:
        logger.error(f"❌ 업데이트 오류: {e}")

def run_full_pipeline():
    """전체 파이프라인 실행"""
    logger.info("🚀 전체 파이프라인 시작")
    run_collector()
    time.sleep(60)  # 1분 대기
    run_analyzer()
    time.sleep(30)  # 30초 대기
    run_uploader()
    logger.info("✅ 전체 파이프라인 완료")

def main():
    """스케줄러 메인"""
    logger.info("=" * 50)
    logger.info("NewsAnalyzer 스케줄러 시작")
    logger.info(f"시작 시간: {datetime.now()}")
    
    config = load_config()
    schedule_config = config['schedule']
    
    # 스케줄 등록
    schedule.every().day.at(schedule_config['collection_time']).do(run_collector)
    schedule.every().day.at(schedule_config['analysis_time']).do(run_analyzer)
    schedule.every().day.at(schedule_config['upload_time']).do(run_uploader)
    
    logger.info(f"⏰ 스케줄 등록:")
    logger.info(f"  수집: {schedule_config['collection_time']}")
    logger.info(f"  분석: {schedule_config['analysis_time']}")
    logger.info(f"  업로드: {schedule_config['upload_time']}")
    
    # 즉시 한 번 실행 (선택사항)
    # run_full_pipeline()
    
    # 스케줄 루프
    logger.info("⏳ 대기 중...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏹️ 스케줄러 종료")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

