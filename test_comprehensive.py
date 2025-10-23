#!/usr/bin/env python3
"""
NewsAnalyzer 종합 테스트 스크립트
"""

import requests
import json
import time
import sys

API_BASE = 'http://localhost:3002'

def test_endpoint(endpoint, description):
    """API 엔드포인트 테스트"""
    try:
        print(f"🔍 {description} 테스트 중...")
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: 성공")
            
            # 응답 크기 확인
            content_length = len(response.content)
            print(f"   - 응답 크기: {content_length:,} bytes")
            
            # 데이터 구조 확인
            if isinstance(data, dict):
                print(f"   - 키 개수: {len(data.keys())}")
                if 'metadata' in data:
                    print(f"   - 메타데이터: {data['metadata']}")
            
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: 네트워크 오류 - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ {description}: JSON 파싱 오류 - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: 예상치 못한 오류 - {e}")
        return False

def test_data_optimization():
    """데이터 최적화 테스트"""
    try:
        print(f"\n🔍 데이터 최적화 테스트 중...")
        
        # 정치인 리스트 테스트
        response = requests.get(f"{API_BASE}/api/politicians")
        if response.status_code == 200:
            data = response.json()
            politicians = data.get('politicians', [])
            
            print(f"✅ 정치인 리스트 최적화:")
            print(f"   - 총 정치인 수: {len(politicians)}명")
            print(f"   - 평균 토픽 수: {sum(len(p.get('top_topics', [])) for p in politicians) / len(politicians):.1f}개")
            print(f"   - 응답 크기: {len(response.content):,} bytes")
            
            # 각 정치인의 데이터 구조 확인
            for politician in politicians[:2]:  # 처음 2명만 확인
                print(f"   - {politician.get('name')}: {len(politician.get('top_topics', []))}개 토픽")
        
        # LDA 결과 테스트
        response = requests.get(f"{API_BASE}/api/lda")
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topics', [])
            
            print(f"✅ LDA 결과 최적화:")
            print(f"   - 총 토픽 수: {len(topics)}개")
            print(f"   - 평균 키워드 수: {sum(len(t.get('keywords', [])) for t in topics) / len(topics):.1f}개")
            print(f"   - 응답 크기: {len(response.content):,} bytes")
            
            # 각 토픽의 데이터 구조 확인
            for topic in topics[:3]:  # 처음 3개만 확인
                print(f"   - {topic.get('name')}: {len(topic.get('keywords', []))}개 키워드, {topic.get('politician_count', 0)}명")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 최적화 테스트 실패: {e}")
        return False

def test_performance():
    """성능 테스트"""
    try:
        print(f"\n🔍 성능 테스트 중...")
        
        endpoints = [
            '/api/health',
            '/api/politicians',
            '/api/lda',
            '/api/politicians/kim_dong_yeon',
            '/api/lda/topics/topic_1'
        ]
        
        total_time = 0
        successful_requests = 0
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = end_time - start_time
                    total_time += response_time
                    successful_requests += 1
                    print(f"   ✅ {endpoint}: {response_time:.3f}초")
                else:
                    print(f"   ❌ {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint}: {e}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"✅ 성능 테스트 완료:")
            print(f"   - 성공한 요청: {successful_requests}/{len(endpoints)}")
            print(f"   - 평균 응답 시간: {avg_time:.3f}초")
            print(f"   - 총 응답 시간: {total_time:.3f}초")
        
        return successful_requests == len(endpoints)
        
    except Exception as e:
        print(f"❌ 성능 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 NewsAnalyzer 종합 테스트 시작")
    print(f"📍 테스트 대상: {API_BASE}")
    print("=" * 60)
    
    # 서버 상태 확인
    server_running = test_endpoint('/api/health', '서버 상태 확인')
    if not server_running:
        print("❌ 서버가 실행되지 않았습니다.")
        print("💡 다음 명령어로 서버를 시작하세요:")
        print("   python3 test_server.py 3002")
        return
    
    print("✅ 서버가 실행 중입니다.")
    
    # API 엔드포인트 테스트
    tests = [
        ('/api/politicians', '정치인 리스트 API'),
        ('/api/politicians/kim_dong_yeon', '정치인 상세 정보 API'),
        ('/api/lda', 'LDA 분석 결과 API'),
        ('/api/lda/topics/topic_1', '토픽 상세 정보 API')
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for endpoint, description in tests:
        if test_endpoint(endpoint, description):
            passed_tests += 1
        print()  # 빈 줄 추가
    
    # 데이터 최적화 테스트
    test_data_optimization()
    
    # 성능 테스트
    test_performance()
    
    # 결과 요약
    print("=" * 60)
    print(f"📊 테스트 결과: {passed_tests}/{total_tests} 통과")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("🌐 웹 인터페이스: http://localhost:3002")
        print("📊 API 문서:")
        print("   - GET /api/health - 서버 상태")
        print("   - GET /api/politicians - 정치인 리스트")
        print("   - GET /api/politicians/:id - 정치인 상세")
        print("   - GET /api/lda - LDA 분석 결과")
        print("   - GET /api/lda/topics/:id - 토픽 상세")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 서버 상태를 확인해주세요.")

if __name__ == '__main__':
    main()
