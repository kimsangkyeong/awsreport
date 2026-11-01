#!/usr/bin/env bash
# ##################################################################################################
# [방법 B] 단일 실행파일 빌드 (Linux)
# Developer : k.s.k & kiro
#
# 전제: 인터넷 가능 서버, 폐쇄망 대상과 '동일한 Linux 배포판/아키텍처(glibc)'.
# 사용: bash build/build_exe.sh
# 산출물: dist/awsreportwithkiro (단일 실행파일, 대상에 Python 불필요)
# 실행(폐쇄망): ./awsreportwithkiro --profile <name> --region ap-northeast-2
#
# 참고: glibc 버전 차이로 깨질 수 있으니, 가능하면 '대상과 같은 베이스 이미지'(예: 동일 OS 버전
#       컨테이너)에서 빌드하는 것을 권장.
# ##################################################################################################
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
cd "$ROOT"

echo "[1/3] 빌드 의존성 설치"
python3 -m pip install -r requirements.txt pyinstaller

echo "[2/3] 이전 빌드 정리"
rm -rf build/awsreportwithkiro dist

echo "[3/3] PyInstaller 빌드"
python3 -m PyInstaller awsreportwithkiro.spec --clean --noconfirm

echo ""
if [ -f "dist/awsreportwithkiro" ]; then
  echo "완료: dist/awsreportwithkiro"
  echo "실행: ./dist/awsreportwithkiro --profile <name> --region ap-northeast-2"
else
  echo "빌드 산출물을 찾지 못했습니다. 로그 확인."
fi
