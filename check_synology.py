import requests
import json

synology_ip = "192.168.219.2"
port = 5000

print("=== 시놀로지 NAS 정보 확인 ===\n")

# 1. 기본 연결 확인
try:
    response = requests.get(f"http://{synology_ip}:{port}", timeout=5)
    print(f"✅ DSM 웹 인터페이스 연결 성공")
    print(f"   URL: http://{synology_ip}:{port}")
except Exception as e:
    print(f"❌ 연결 실패: {e}")

# 2. API 정보 확인
try:
    api_url = f"http://{synology_ip}:{port}/webapi/entry.cgi?api=SYNO.API.Info&version=1&method=query&query=SYNO.Docker.Container"
    response = requests.get(api_url, timeout=5)
    data = response.json()
    
    if data.get('success'):
        print(f"\n✅ Docker API 사용 가능")
        print(f"   {json.dumps(data['data'], indent=2)}")
    else:
        print(f"\n⚠️  Docker API 확인 필요")
except Exception as e:
    print(f"\n⚠️  API 확인 중 오류: {e}")

# 3. 포트 스캔
print("\n📡 주요 포트 확인:")
ports = [
    (5000, "DSM HTTP"),
    (5001, "DSM HTTPS"),
    (22, "SSH"),
    (80, "HTTP"),
    (443, "HTTPS"),
    (3000, "Custom (프론트엔드)"),
    (8000, "Custom (백엔드)")
]

for port_num, service in ports:
    try:
        response = requests.get(f"http://{synology_ip}:{port_num}", timeout=2)
        print(f"  ✅ {port_num}: {service} - 열림")
    except requests.exceptions.ConnectRefused:
        print(f"  ❌ {port_num}: {service} - 닫힘")
    except requests.exceptions.Timeout:
        print(f"  ⏱️  {port_num}: {service} - 타임아웃")
    except Exception as e:
        print(f"  ❓ {port_num}: {service} - {type(e).__name__}")

print(f"\n💡 권장 사항:")
print(f"  1. 웹 브라우저에서 http://{synology_ip}:5000 접속")
print(f"  2. btf_admin / Ks&js140405 로 로그인")
print(f"  3. 제어판 → 터미널 및 SNMP → SSH 서비스 활성화")
print(f"  4. Docker 패키지 설치 확인")
