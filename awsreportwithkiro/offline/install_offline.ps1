# ##################################################################################################
# [방법 A - 2단계] 폐쇄망 PC 에서 오프라인 설치 (Windows)
# Developer : k.s.k & kiro
#
# 전제: 폐쇄망 PC 에 Python 3.12+ 설치돼 있고, download_wheels 로 받은 offline\wheels 반입됨.
# 사용:
#   powershell -ExecutionPolicy Bypass -File .\offline\install_offline.ps1
# 동작: 로컬 wheels 폴더만으로 가상환경(.venv) 생성 후 의존성 설치 (인터넷 접근 없음).
# 실행:
#   .\.venv\Scripts\python.exe awsreportwithkiro.py --profile <name> --region ap-northeast-2
# ##################################################################################################
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$wheels = Join-Path $PSScriptRoot "wheels"
$venv = Join-Path $root ".venv"

if (-not (Test-Path $wheels)) { throw "wheels 폴더가 없습니다: $wheels (반입 확인)" }

Write-Host "[1/3] 가상환경 생성: $venv"
python -m venv $venv
$py = Join-Path $venv "Scripts\python.exe"

Write-Host "[2/3] pip 업그레이드(오프라인)"
& $py -m pip install --no-index --find-links $wheels --upgrade pip setuptools wheel

Write-Host "[3/3] 의존성 설치(오프라인)"
& $py -m pip install --no-index --find-links $wheels -r (Join-Path $root "requirements.txt")

Write-Host ""
Write-Host "설치 완료. 실행 예:"
Write-Host "  $py awsreportwithkiro.py --profile <name> --region ap-northeast-2"
