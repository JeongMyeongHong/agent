#!/bin/bash

# 원격 서버에 SSH로 배포하는 스크립트

echo "🌐 Remote Deploy Script"
echo "========================"
echo ""

# 설정 (여기를 수정하세요)
SERVER_USER="root"
SERVER_HOST="175.117.82.131"
SERVER_PORT="22"

echo ""
echo "📍 배포 대상:"
echo "   서버: $SERVER_USER@$SERVER_HOST:$SERVER_PORT"
echo ""

read -p "계속하시겠습니까? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "배포 취소됨"
    exit 0
fi

# .env.prod 파일 확인
echo ""
echo "📋 .env.prod 파일 확인..."
if [ ! -f ".env.prod" ]; then
    echo "   ❌ Error: .env.prod 파일이 없습니다!"
    echo "   .env.prod 파일을 생성하고 API 키를 설정하세요."
    exit 1
else
    echo "   ✅ .env.prod 파일 확인됨"
fi

# SSH로 배포 스크립트 실행
echo ""
echo "🚀 원격 서버에 배포 중..."
echo ""

# SSH 실행 결과를 확인하고 에러 시 종료
if ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
# 서버에서 실행될 명령어들

set -e

echo "📥 배포 스크립트 다운로드..."
curl -sSL https://raw.githubusercontent.com/JeongMyeongHong/agent/main/deploy.sh -o /tmp/deploy.sh
chmod +x /tmp/deploy.sh

echo ""
echo "🚀 배포 시작..."
/tmp/deploy.sh

echo ""
echo "✅ 원격 배포 완료!"
ENDSSH
then
    # 배포 성공 후 .env.prod 파일 전송
    echo ""
    echo "📤 .env.prod 파일 전송 중..."
    scp -P $SERVER_PORT .env.prod $SERVER_USER@$SERVER_HOST:/root/stock-invest/.env.prod
    echo "   ✅ 전송 완료"

    # 컨테이너 재시작 (환경 변수 반영)
    echo ""
    echo "🔄 컨테이너 재시작 중..."
    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "cd /root/stock-invest && docker-compose --env-file .env.prod restart"
    echo "   ✅ 재시작 완료"

    # 배포 성공
    echo ""
    echo "✅ 배포가 완료되었습니다!"
    echo ""
    echo "📍 접속 정보:"
    echo "   API: http://$SERVER_HOST:38000"
    echo "   Docs: http://$SERVER_HOST:38000/docs"
    echo ""
    echo "📝 서버 접속:"
    echo "   ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST"
    echo "   cd /root/stock-invest"
    echo "   docker-compose ps"
else
    # 배포 실패
    echo ""
    echo "❌ 배포 중 오류가 발생했습니다!"
    echo ""
    echo "📝 서버 로그 확인:"
    echo "   ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST"
    echo "   cd /root/stock-invest"
    echo "   docker-compose logs"
    exit 1
fi
