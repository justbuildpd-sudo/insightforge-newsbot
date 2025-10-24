#!/bin/bash
# Synology에서 직접 실행할 설치 스크립트
# File Station으로 이 파일을 업로드한 후 작업 스케줄러에서 실행

cd /volume1/docker

# newsanalyzer.tar.gz가 있는지 확인
if [ ! -f "newsanalyzer.tar.gz" ]; then
    echo "❌ newsanalyzer.tar.gz 파일을 먼저 업로드하세요"
    exit 1
fi

echo "📦 압축 해제 중..."
tar -xzf newsanalyzer.tar.gz

if [ ! -d "newsanalyzer" ]; then
    echo "❌ 압축 해제 실패"
    exit 1
fi

cd newsanalyzer
echo "✅ 디렉토리 생성 완료: $(pwd)"

# 환경 설정 파일 생성
echo "⚙️ 환경 설정 중..."
cat > .env << 'EOF'
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
COLLECTION_MODE=historical
TZ=Asia/Seoul
EOF

echo "✅ .env 파일 생성 완료"

# Docker Compose 버전 확인
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose를 찾을 수 없습니다"
    exit 1
fi

echo "🐳 Docker Compose: $DOCKER_COMPOSE"

# Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중... (5-10분 소요)"
$DOCKER_COMPOSE build newsanalyzer-historical

if [ $? -ne 0 ]; then
    echo "❌ Docker 빌드 실패"
    exit 1
fi

echo "✅ Docker 이미지 빌드 완료"

# 컨테이너 시작
echo "🚀 컨테이너 시작 중..."
$DOCKER_COMPOSE up -d newsanalyzer-historical

if [ $? -ne 0 ]; then
    echo "❌ 컨테이너 시작 실패"
    exit 1
fi

echo "✅ 컨테이너 시작 완료"

# 상태 확인
echo ""
echo "=================================================================================="
echo "✅ 설치 완료!"
echo "=================================================================================="
echo ""
$DOCKER_COMPOSE ps
echo ""
echo "📝 로그 확인 명령어:"
echo "  cd /volume1/docker/newsanalyzer"
echo "  $DOCKER_COMPOSE logs -f newsanalyzer-historical"
echo ""
echo "📊 진행 상황 확인:"
echo "  cat /volume1/docker/newsanalyzer/data/collection_state.json"
echo ""
echo "=================================================================================="

