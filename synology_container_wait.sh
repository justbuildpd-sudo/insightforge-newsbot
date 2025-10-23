#!/bin/bash
# Synology 컨테이너 재시작 대기 및 상태 확인 스크립트

echo "=== Synology 컨테이너 상태 확인 및 대기 ==="

# 1. 컨테이너 상태 확인
echo "📊 Docker 컨테이너 상태:"
sudo docker ps -a | grep newsanalyzer

echo ""
echo "📊 컨테이너 재시작 상태 확인:"
sudo docker ps | grep newsanalyzer-historical

# 2. 컨테이너 재시작 대기
echo ""
echo "⏳ 컨테이너 재시작 완료 대기 중..."

# 재시작 완료까지 대기 (최대 60초)
for i in {1..12}; do
    echo "대기 중... ($i/12)"
    if sudo docker ps | grep -q "newsanalyzer-historical.*Up"; then
        echo "✅ newsanalyzer-historical 컨테이너가 실행 중입니다"
        break
    fi
    sleep 5
done

# 3. 컨테이너 상태 재확인
echo ""
echo "📊 최종 컨테이너 상태:"
sudo docker ps | grep newsanalyzer

# 4. 컨테이너 로그 확인
echo ""
echo "📊 컨테이너 로그 확인 (최근 20줄):"
sudo docker compose logs --tail=20 newsanalyzer-historical

# 5. 권한 수정 시도
echo ""
echo "🔧 권한 수정 시도:"

# 컨테이너가 실행 중인지 확인
if sudo docker ps | grep -q "newsanalyzer-historical.*Up"; then
    echo "✅ 컨테이너가 실행 중입니다. 권한 수정을 시도합니다."
    
    # 권한 수정 시도
    sudo docker exec -it newsanalyzer-historical chown -R 1000:1000 /app/output/ 2>/dev/null && echo "✅ 권한 수정 성공" || echo "❌ 권한 수정 실패"
    
    # 또는 루트 권한으로 시도
    sudo docker exec -u root -it newsanalyzer-historical chown -R 1000:1000 /app/output/ 2>/dev/null && echo "✅ 루트 권한으로 수정 성공" || echo "❌ 루트 권한으로 수정 실패"
    
else
    echo "❌ 컨테이너가 아직 실행되지 않았습니다."
    echo "💡 컨테이너 재시작을 시도합니다."
    
    # 컨테이너 재시작
    sudo docker compose restart newsanalyzer-historical
    
    echo "⏳ 재시작 완료 대기 중..."
    sleep 10
    
    # 재시작 후 상태 확인
    sudo docker ps | grep newsanalyzer-historical
fi

# 6. 데이터 파일 확인
echo ""
echo "📊 데이터 파일 확인:"
ls -la output/lda_results/ 2>/dev/null || echo "❌ LDA 결과 디렉토리가 없습니다"

# 7. 파일 생성 테스트
echo ""
echo "📝 파일 생성 테스트:"
touch output/test_file.txt 2>/dev/null && echo "✅ 파일 생성 성공" || echo "❌ 파일 생성 실패"

# 8. 최종 권한 확인
echo ""
echo "📊 최종 권한 상태:"
ls -la output/ 2>/dev/null || echo "output 디렉토리가 없습니다"

echo ""
echo "=== 컨테이너 상태 확인 완료 ==="
echo "✅ 컨테이너 재시작 대기 완료"
echo "✅ 권한 수정 시도 완료"
echo "✅ 파일 생성 테스트 완료"
echo ""
echo "🔍 다음 단계:"
echo "1. 컨테이너 로그 확인"
echo "2. 데이터 수집 상태 확인"
echo "3. API 상태 확인"
