#!/bin/bash
# NewsAnalyzer 시놀로지 배포 스크립트

set -e

echo "=== NewsAnalyzer 시놀로지 배포 ==="
echo ""

# 설정
SYNOLOGY_IP="${1:-192.168.0.100}"
SYNOLOGY_USER="${2:-admin}"
TARGET_DIR="/volume1/docker/NewsAnalyzer"

echo "📡 대상: $SYNOLOGY_USER@$SYNOLOGY_IP:$TARGET_DIR"
echo ""

# 1. 로컬 테스트
echo "1️⃣ 로컬 테스트..."
if [ ! -f "config.json" ]; then
    echo "❌ config.json 파일이 없습니다."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 파일이 없습니다."
    exit 1
fi

echo "✅ 필수 파일 확인 완료"
echo ""

# 2. 압축 파일 생성
echo "2️⃣ 배포 패키지 생성..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="NewsAnalyzer_${TIMESTAMP}.tar.gz"

tar -czf "../${PACKAGE_NAME}" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='data/collected/*' \
    --exclude='output/*' \
    --exclude='logs/*' \
    .

echo "✅ 패키지 생성: ${PACKAGE_NAME}"
echo ""

# 3. 시놀로지로 전송
echo "3️⃣ 시놀로지로 전송..."
echo "rsync 명령어:"
echo "rsync -avz --progress ../${PACKAGE_NAME} ${SYNOLOGY_USER}@${SYNOLOGY_IP}:/volume1/docker/"
echo ""
echo "📋 수동 실행 명령어:"
echo "  1. SSH 접속: ssh ${SYNOLOGY_USER}@${SYNOLOGY_IP}"
echo "  2. 압축 해제: cd /volume1/docker && tar -xzf ${PACKAGE_NAME}"
echo "  3. 환경변수: cd NewsAnalyzer && cp .env.example .env && nano .env"
echo "  4. 실행: docker-compose up -d"
echo "  5. 로그: docker-compose logs -f"
echo ""

# 4. 배포 가이드 출력
echo "4️⃣ 배포 가이드:"
echo ""
cat << 'EOF'
=== 시놀로지 SSH 접속 후 실행할 명령어 ===

# 1. 디렉토리 이동
cd /volume1/docker

# 2. 압축 해제
tar -xzf NewsAnalyzer_*.tar.gz

# 3. 환경변수 설정
cd NewsAnalyzer
cp .env.example .env
nano .env
# API 키 입력 후 저장 (Ctrl+O, Enter, Ctrl+X)

# 4. Docker 빌드 및 실행
docker-compose build
docker-compose up -d

# 5. 로그 확인
docker-compose logs -f newsanalyzer

# 6. 상태 확인
docker-compose ps

=== 완료! ===
EOF

echo ""
echo "✅ 배포 패키지 준비 완료!"
echo "📦 파일: ../${PACKAGE_NAME}"
echo ""

