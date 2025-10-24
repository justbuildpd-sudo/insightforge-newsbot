#!/bin/bash
# Synology 배포 명령어 (비밀번호: Ks12121212)

echo "=== Synology 배포 단계별 가이드 ==="
echo ""
echo "IP: 192.168.219.2"
echo "사용자: admin"
echo "비밀번호: Ks12121212"
echo ""
echo "=================================================================================="
echo "Step 1: 파일 업로드"
echo "=================================================================================="
echo "scp newsanalyzer.tar.gz admin@192.168.219.2:/volume1/docker/"
echo ""
echo "=================================================================================="
echo "Step 2: SSH 접속"
echo "=================================================================================="
echo "ssh admin@192.168.219.2"
echo ""
echo "=================================================================================="
echo "Step 3: Synology에서 실행할 명령어들 (SSH 접속 후)"
echo "=================================================================================="
cat << 'ENDSSH'
# 압축 해제
cd /volume1/docker
tar -xzf newsanalyzer.tar.gz
rm newsanalyzer.tar.gz
cd newsanalyzer

# 환경 설정
cat > .env << 'EOF'
NAVER_CLIENT_ID=ULDLTGiPvrrPBgbuydSm
NAVER_CLIENT_SECRET=uO5mu7UQBg
COLLECTION_MODE=historical
EOF

# Docker 이미지 빌드
sudo docker-compose build newsanalyzer-historical

# 컨테이너 시작
sudo docker-compose up -d newsanalyzer-historical

# 로그 확인
sudo docker-compose logs -f newsanalyzer-historical
ENDSSH

echo ""
echo "=================================================================================="
echo "✅ 모든 명령어가 준비되었습니다!"
echo "=================================================================================="

