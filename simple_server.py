#!/usr/bin/env python3
"""
간단한 NewsAnalyzer 테스트 서버
"""

import json
import gzip
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GET 요청 처리"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # CORS 헤더
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            if path == '/':
                self.serve_homepage()
            elif path == '/api/health':
                self.serve_health()
            elif path == '/api/politicians':
                self.serve_politicians_list()
            elif path.startswith('/api/politicians/'):
                politician_id = path.split('/')[-1]
                self.serve_politician_detail(politician_id)
            elif path == '/api/lda':
                politician_id = query_params.get('politician_id', [None])[0]
                self.serve_lda_results(politician_id)
            elif path.startswith('/api/lda/topics/'):
                topic_id = path.split('/')[-1]
                self.serve_topic_detail(topic_id)
            else:
                self.send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Error: {e}")
            self.send_error(500, "Internal server error")
    
    def send_json_response(self, data, status=200):
        """JSON 응답 전송"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # gzip 압축
        compressed_data = gzip.compress(json_data.encode('utf-8'))
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(compressed_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(compressed_data)
    
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
    
    def serve_lda_results(self, politician_id=None):
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
        
        if politician_id:
            politician = next((p for p in optimized_data["politicians"] if p["id"] == politician_id), None)
            if politician:
                self.send_json_response({
                    "metadata": optimized_data["metadata"],
                    "politician": politician
                })
                return
        
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

def run_server(port=3000):
    """서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    
    print(f"🚀 NewsAnalyzer API Server running on port {port}")
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
