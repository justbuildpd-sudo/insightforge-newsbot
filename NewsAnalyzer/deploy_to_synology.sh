#!/bin/bash
#
# Synology NAS 배포 스크립트
# 사용법: ./deploy_to_synology.sh SYNOLOGY_IP
#

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NewsAnalyzer Synology NAS 배포 스크립트              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Synology IP 확인
if [ -z "$1" ]; then
    echo -e "${RED}❌ Synology IP 주소를 입력하세요${NC}"
    echo -e "${YELLOW}사용법: $0 <SYNOLOGY_IP>${NC}"
    echo -e "${YELLOW}예시: $0 192.168.1.100${NC}"
    exit 1
fi

SYNOLOGY_IP=$1
SYNOLOGY_USER=${2:-admin}
SYNOLOGY_PATH="/volume1/docker/newsanalyzer"

echo -e "${GREEN}📍 Synology 정보${NC}"
echo -e "  IP: ${YELLOW}${SYNOLOGY_IP}${NC}"
echo -e "  사용자: ${YELLOW}${SYNOLOGY_USER}${NC}"
echo -e "  경로: ${YELLOW}${SYNOLOGY_PATH}${NC}"
echo ""

# Step 1: 패키징
echo -e "${BLUE}[1/5]${NC} 📦 파일 패키징 중..."
cd "$(dirname "$0")"

tar -czf newsanalyzer.tar.gz \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='hs_err_*.log' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='newsanalyzer.tar.gz' \
    .

FILE_SIZE=$(ls -lh newsanalyzer.tar.gz | awk '{print $5}')
echo -e "${GREEN}✅ 패키징 완료 (${FILE_SIZE})${NC}"
echo ""

# Step 2: 연결 테스트
echo -e "${BLUE}[2/5]${NC} 🔌 Synology 연결 테스트 중..."
if ssh -o ConnectTimeout=5 ${SYNOLOGY_USER}@${SYNOLOGY_IP} "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ SSH 연결 성공${NC}"
else
    echo -e "${RED}❌ SSH 연결 실패${NC}"
    echo -e "${YELLOW}💡 Synology에서 SSH 서비스를 활성화하세요:${NC}"
    echo -e "   제어판 → 터미널 및 SNMP → SSH 서비스 활성화"
    exit 1
fi
echo ""

# Step 3: 디렉토리 생성
echo -e "${BLUE}[3/5]${NC} 📁 Synology에 디렉토리 생성 중..."
ssh ${SYNOLOGY_USER}@${SYNOLOGY_IP} "mkdir -p ${SYNOLOGY_PATH}"
echo -e "${GREEN}✅ 디렉토리 생성 완료${NC}"
echo ""

# Step 4: 파일 업로드
echo -e "${BLUE}[4/5]${NC} 📤 파일 업로드 중..."
scp -o ConnectTimeout=10 newsanalyzer.tar.gz ${SYNOLOGY_USER}@${SYNOLOGY_IP}:${SYNOLOGY_PATH}/
echo -e "${GREEN}✅ 업로드 완료${NC}"
echo ""

# Step 5: 압축 해제 및 설치
echo -e "${BLUE}[5/5]${NC} 🛠️  Synology에서 설치 중..."
ssh ${SYNOLOGY_USER}@${SYNOLOGY_IP} << 'ENDSSH'
cd /volume1/docker/newsanalyzer

echo "📦 압축 해제 중..."
tar -xzf newsanalyzer.tar.gz
rm newsanalyzer.tar.gz

echo "⚙️  환경 설정 중..."
# .env 파일 생성 (이미 있으면 스킵)
if [ ! -f .env ]; then
    cat > .env << 'EOF'
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
GITHUB_TOKEN=
VERCEL_TOKEN=
EOF
    echo "✅ .env 파일 생성"
else
    echo "ℹ️  .env 파일 이미 존재"
fi

echo "🐳 Docker 이미지 빌드 중..."
sudo docker-compose build newsanalyzer-historical

echo "🚀 컨테이너 시작 중..."
sudo docker-compose up -d newsanalyzer-historical

echo "✅ 설치 완료!"
echo ""
echo "📊 상태 확인:"
sudo docker-compose ps

echo ""
echo "📝 로그 확인 명령어:"
echo "  sudo docker-compose logs -f newsanalyzer-historical"
ENDSSH

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 배포 완료!                                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 다음 단계:${NC}"
echo -e "  1️⃣  SSH 접속: ${BLUE}ssh ${SYNOLOGY_USER}@${SYNOLOGY_IP}${NC}"
echo -e "  2️⃣  로그 확인: ${BLUE}cd ${SYNOLOGY_PATH} && sudo docker-compose logs -f${NC}"
echo -e "  3️⃣  상태 확인: ${BLUE}cat ${SYNOLOGY_PATH}/data/collection_state.json${NC}"
echo ""
echo -e "${YELLOW}⏰ Cron 스케줄 설정 (DSM):${NC}"
echo -e "  제어판 → 작업 스케줄러 → 생성 → 사용자 정의 스크립트"
echo -e "  매일 새벽 2시: ${BLUE}cd ${SYNOLOGY_PATH} && docker-compose restart newsanalyzer-historical${NC}"
echo ""
