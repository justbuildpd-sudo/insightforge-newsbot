#!/usr/bin/env python3
"""
NewsAnalyzer 테스트 서버 - 최소 기능
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class TestAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GET 요청 처리"""
        try:
            if self.path == '/':
                self.serve_homepage()
            elif self.path == '/landing.html':
                self.serve_landing()
            elif self.path == '/dashboard.html':
                self.serve_dashboard()
            elif self.path == '/api/health':
                self.serve_health()
            elif self.path == '/api/politicians':
                self.serve_politicians_list()
            elif self.path.startswith('/api/politicians/'):
                politician_id = self.path.split('/')[-1]
                self.serve_politician_detail(politician_id)
            elif self.path == '/api/lda':
                self.serve_lda_results()
            elif self.path.startswith('/api/lda/topics/'):
                topic_id = self.path.split('/')[-1]
                self.serve_topic_detail(topic_id)
            elif self.path == '/api/sido':
                self.serve_sido_list()
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error: {e}")
            self.send_error(500, "Internal server error")
    
    def send_json_response(self, data, status=200):
        """JSON 응답 전송"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def load_json_file(self, filename):
        """JSON 파일 로드"""
        file_path = os.path.join('data', filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return None
    
    def serve_homepage(self):
        """홈페이지 서빙"""
        try:
            with open('public/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Homepage not found")
    
    def serve_landing(self):
        """랜딩 페이지 서빙"""
        try:
            with open('public/landing.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Landing page not found")
    
    def serve_dashboard(self):
        """대시보드 페이지 서빙"""
        try:
            with open('public/dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Dashboard page not found")
    
    def serve_health(self):
        """서버 상태 확인"""
        health_data = {
            "status": "healthy",
            "timestamp": "2025-10-23T10:00:00Z",
            "cache_size": 0,
            "memory_usage": {"rss": 1000000, "vms": 2000000}
        }
        self.send_json_response(health_data)
    
    def serve_politicians_list(self):
        """정치인 리스트 API"""
        raw_data = self.load_json_file('politicians_sample.json')
        
        if not raw_data:
            self.send_json_response({"error": "Politician data not found"}, 404)
            return
        
        # 데이터 최적화
        optimized_data = {
            "metadata": {
                "total_count": len(raw_data),
                "last_updated": "2025-10-23T10:00:00Z",
                "version": "1.0"
            },
            "politicians": [
                {
                    "id": politician.get("id", politician.get("name", "").replace(" ", "_")),
                    "name": politician.get("name"),
                    "position": politician.get("position", politician.get("title")),
                    "party": politician.get("party"),
                    "region": politician.get("region", politician.get("district")),
                    "term": politician.get("term"),
                    "top_topics": politician.get("lda_results", {}).get("topics", [])[:3]
                }
                for politician in raw_data
            ]
        }
        
        self.send_json_response(optimized_data)
    
    def serve_politician_detail(self, politician_id):
        """정치인 상세 정보 API"""
        raw_data = self.load_json_file('politicians_sample.json')
        
        if not raw_data:
            self.send_json_response({"error": "Politician data not found"}, 404)
            return
        
        politician = None
        for p in raw_data:
            if p.get("id") == politician_id or p.get("name", "").replace(" ", "_") == politician_id:
                politician = p
                break
        
        if not politician:
            self.send_json_response({"error": "Politician not found"}, 404)
            return
        
        optimized_politician = {
            "id": politician.get("id", politician.get("name", "").replace(" ", "_")),
            "name": politician.get("name"),
            "position": politician.get("position", politician.get("title")),
            "party": politician.get("party"),
            "region": politician.get("region", politician.get("district")),
            "term": politician.get("term"),
            "lda_analysis": {
                "topics": politician.get("lda_results", {}).get("topics", []),
                "analysis_date": politician.get("lda_results", {}).get("analysis_date"),
                "confidence": politician.get("lda_results", {}).get("confidence")
            }
        }
        
        self.send_json_response(optimized_politician)
    
    def serve_lda_results(self):
        """LDA 분석 결과 API"""
        raw_data = self.load_json_file('lda_results_sample.json')
        
        if not raw_data:
            self.send_json_response({"error": "LDA results not found"}, 404)
            return
        
        optimized_data = {
            "metadata": raw_data.get("metadata", {}),
            "topics": [
                {
                    "id": topic.get("id"),
                    "name": topic.get("name"),
                    "keywords": topic.get("keywords", [])[:10],
                    "weight": round(topic.get("weight", 0), 3),
                    "politician_count": len(topic.get("politicians", []))
                }
                for topic in raw_data.get("topics", [])
            ],
            "politicians": [
                {
                    "id": politician.get("id"),
                    "name": politician.get("name"),
                    "top_topics": politician.get("topics", [])[:3]
                }
                for politician in raw_data.get("politicians", [])
            ]
        }
        
        self.send_json_response(optimized_data)
    
    def serve_topic_detail(self, topic_id):
        """토픽 상세 정보 API"""
        raw_data = self.load_json_file('lda_results_sample.json')
        
        if not raw_data:
            self.send_json_response({"error": "LDA results not found"}, 404)
            return
        
        topic = None
        for t in raw_data.get("topics", []):
            if t.get("id") == topic_id:
                topic = t
                break
        
        if not topic:
            self.send_json_response({"error": "Topic not found"}, 404)
            return
        
        optimized_topic = {
            "id": topic.get("id"),
            "name": topic.get("name"),
            "keywords": topic.get("keywords", [])[:20],
            "weight": round(topic.get("weight", 0), 3),
            "politicians": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "weight": round(p.get("weight", 0), 3)
                }
                for p in topic.get("politicians", [])
            ],
            "analysis_date": topic.get("analysis_date")
        }
        
        self.send_json_response(optimized_topic)
    
    def serve_sido_list(self):
        """시도 목록 API"""
        sido_list = [
            {"code": "11", "sido_name": "서울특별시", "total_regions": 25},
            {"code": "26", "sido_name": "부산광역시", "total_regions": 16},
            {"code": "27", "sido_name": "대구광역시", "total_regions": 8},
            {"code": "28", "sido_name": "인천광역시", "total_regions": 10},
            {"code": "29", "sido_name": "광주광역시", "total_regions": 5},
            {"code": "30", "sido_name": "대전광역시", "total_regions": 5},
            {"code": "31", "sido_name": "울산광역시", "total_regions": 5},
            {"code": "36", "sido_name": "세종특별자치시", "total_regions": 1},
            {"code": "41", "sido_name": "경기도", "total_regions": 31},
            {"code": "42", "sido_name": "강원특별자치도", "total_regions": 18},
            {"code": "43", "sido_name": "충청북도", "total_regions": 11},
            {"code": "44", "sido_name": "충청남도", "total_regions": 15},
            {"code": "45", "sido_name": "전북특별자치도", "total_regions": 14},
            {"code": "46", "sido_name": "전라남도", "total_regions": 22},
            {"code": "47", "sido_name": "경상북도", "total_regions": 23},
            {"code": "48", "sido_name": "경상남도", "total_regions": 18},
            {"code": "50", "sido_name": "제주특별자치도", "total_regions": 2}
        ]
        
        self.send_json_response({"sido_list": sido_list})

def run_server(port=3002):
    """서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestAPIHandler)
    
    print(f"🚀 NewsAnalyzer Test Server running on port {port}")
    print(f"📊 Endpoints available:")
    print(f"   - GET / - 홈페이지")
    print(f"   - GET /api/health - 서버 상태")
    print(f"   - GET /api/politicians - 정치인 리스트")
    print(f"   - GET /api/politicians/:id - 정치인 상세")
    print(f"   - GET /api/lda - LDA 분석 결과")
    print(f"   - GET /api/lda/topics/:id - 토픽 상세")
    print(f"🌐 Open http://localhost:{port} in your browser")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3002
    run_server(port)
