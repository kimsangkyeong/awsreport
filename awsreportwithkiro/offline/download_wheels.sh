#!/usr/bin/env bash
# ##################################################################################################
# [방법 A - 1단계] 오프라인 wheel 다운로드 (인터넷 가능 PC, Linux/macOS)
# Developer : k.s.k & kiro
#
# 사용: bash offline/download_wheels.sh
# 결과: offline/wheels/ 에 모든 패키지 wheel 저장. 소스 전체와 함께 폐쇄망 반입.
# 중요: 폐쇄망 대상과 동일 OS/아키텍처/Python 마이너버전에서 받을 것.
# ##################################################################################################
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
WHEELS="$SCRIPT_DIR/wheels"
mkdir -p "$WHEELS"

echo "[1/2] pip/setuptools/wheel 다운로드..."
python3 -m pip download pip setuptools wheel -d "$WHEELS"

echo "[2/2] requirements 패키지 다운로드..."
python3 -m pip download -r "$ROOT/requirements.txt" -d "$WHEELS"

echo ""
echo "완료: $WHEELS ($(ls "$WHEELS" | wc -l) 개 파일). offline 폴더+소스 전체를 폐쇄망으로 반입하세요."
