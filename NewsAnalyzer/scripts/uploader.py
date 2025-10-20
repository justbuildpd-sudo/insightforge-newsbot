#!/usr/bin/env python3
"""
InsightForge 업데이트 - LDA 분석 결과를 InsightForge에 반영
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
import subprocess
import sys

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / 'config.json'
OUTPUT_DIR = BASE_DIR / 'output' / 'lda_results'
INSIGHTFORGE_DIR = BASE_DIR.parent / 'insightforge-web' / 'data'

def load_config():
    """설정 파일 로드"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_latest_lda_files():
    """최신 LDA 파일 찾기"""
    assembly_files = sorted(OUTPUT_DIR.glob('assembly_lda_*.json'))
    local_files = sorted(OUTPUT_DIR.glob('local_lda_*.json'))
    
    if not assembly_files or not local_files:
        print("❌ LDA 분석 결과 파일이 없습니다.")
        return None, None
    
    return assembly_files[-1], local_files[-1]

def update_insightforge():
    """InsightForge 데이터 업데이트"""
    print("=== InsightForge 업데이트 시작 ===")
    print(f"시작 시간: {datetime.now()}")
    
    config = load_config()
    assembly_file, local_file = get_latest_lda_files()
    
    if not assembly_file or not local_file:
        return False
    
    print(f"\n📂 국회의원 LDA: {assembly_file.name}")
    print(f"📂 지방정치인 LDA: {local_file.name}")
    
    # InsightForge 디렉토리로 복사
    target_assembly = INSIGHTFORGE_DIR / config['output']['assembly_lda_file']
    target_local = INSIGHTFORGE_DIR / config['output']['local_lda_file']
    
    try:
        shutil.copy2(assembly_file, target_assembly)
        shutil.copy2(local_file, target_local)
        
        print(f"\n✅ 복사 완료:")
        print(f"  → {target_assembly}")
        print(f"  → {target_local}")
        
        # Git 커밋 및 푸시
        try:
            # Git add
            subprocess.run(['git', 'add', str(target_assembly), str(target_local)], 
                         cwd=INSIGHTFORGE_DIR.parent.parent, check=True)
            
            # Git commit
            commit_msg = f"update: LDA 분석 결과 업데이트 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                         cwd=INSIGHTFORGE_DIR.parent.parent, check=True)
            
            # Git push
            subprocess.run(['git', 'push', 'origin', 'main'], 
                         cwd=INSIGHTFORGE_DIR.parent.parent, check=True)
            
            print(f"\n✅ Git 푸시 완료!")
            print(f"📝 커밋 메시지: {commit_msg}")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git 작업 실패 (수동 푸시 필요): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 업데이트 실패: {e}")
        return False

def create_summary_report():
    """요약 보고서 생성"""
    assembly_file, local_file = get_latest_lda_files()
    
    if not assembly_file or not local_file:
        return
    
    with open(assembly_file, 'r', encoding='utf-8') as f:
        assembly_data = json.load(f)
    
    with open(local_file, 'r', encoding='utf-8') as f:
        local_data = json.load(f)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'assembly_members': len(assembly_data),
            'local_politicians': len(local_data),
            'total': len(assembly_data) + len(local_data)
        },
        'top_active_assembly': sorted(
            [(name, data['total_count']) for name, data in assembly_data.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10],
        'top_active_local': sorted(
            [(name, data['total_count']) for name, data in local_data.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
    }
    
    report_file = OUTPUT_DIR / f'summary_{datetime.now().strftime("%Y%m%d")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 요약 보고서:")
    print(f"  국회의원: {report['summary']['assembly_members']}명")
    print(f"  지방정치인: {report['summary']['local_politicians']}명")
    print(f"  총계: {report['summary']['total']}명")
    print(f"\n💾 저장: {report_file}")

if __name__ == '__main__':
    try:
        success = update_insightforge()
        if success:
            create_summary_report()
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

