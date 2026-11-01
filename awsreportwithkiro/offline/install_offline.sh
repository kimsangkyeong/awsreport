#!/usr/bin/env bash
# ##################################################################################################
# [방법 A - 2단계] 폐쇄망 PC 오프라인 설치 (Linux/macOS)
# Developer : k.s.k & kiro
#
# 전제: Python 3.12+ 설치됨, offline/wheels 반입됨.
# 사용: bash offline/install_offline.sh
# 실행: ./.venv/bin/python awsreportwithkiro.py --profile <name> --region ap-northeast-2
# ##################################################################################################
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
WHEELS="$SCRIPT_DIR/wheels"
VENV="$ROOT/.venv"

[ -d "$WHEELS" ] || { echo "wheels 폴더 없음: $WHEELS"; exit 1; }

echo "[1/3] 가상환경 생성: $VENV"
python3 -m venv "$VENV"
PY="$VENV/bin/python"

echo "[2/3] pip 업그레이드(오프라인)"
"$PY" -m pip install --no-index --find-links "$WHEELS" --upgrade pip setuptools wheel

echo "[3/3] 의존성 설치(오프라인)"
"$PY" -m pip install --no-index --find-links "$WHEELS" -r "$ROOT/requirements.txt"

echo ""
echo "설치 완료. 실행 예:"
echo "  $PY awsreportwithkiro.py --profile <name> --region ap-northeast-2"
