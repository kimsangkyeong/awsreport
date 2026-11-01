# ##################################################################################################
# [방법 A - 1단계] 오프라인 wheel 다운로드 (인터넷 가능 PC, Windows)
# Developer : k.s.k & kiro
#
# 사용: 인터넷 되는 PC(폐쇄망과 동일 OS/Python 버전)에서 실행.
#   powershell -ExecutionPolicy Bypass -File .\offline\download_wheels.ps1
# 결과: offline\wheels\ 폴더에 requirements 의 모든 패키지 .whl 저장.
#   이 폴더 + 소스 전체를 폐쇄망으로 반입한다.
#
# 중요: '폐쇄망 대상과 동일한 OS/아키텍처/Python 마이너버전' 에서 받아야 한다.
#       (wheel 은 플랫폼/파이썬 버전별로 다름)
# ##################################################################################################
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$wheels = Join-Path $PSScriptRoot "wheels"
New-Item -ItemType Directory -Force -Path $wheels | Out-Null

Write-Host "[1/2] pip 자체도 오프라인 설치 가능하도록 다운로드..."
python -m pip download pip setuptools wheel -d $wheels

Write-Host "[2/2] requirements 패키지 다운로드..."
python -m pip download -r (Join-Path $root "requirements.txt") -d $wheels

Write-Host ""
Write-Host "완료: $wheels 에 $((Get-ChildItem $wheels -Filter *.whl).Count) 개 wheel (+ tar.gz) 저장됨."
Write-Host "이 offline 폴더와 소스 전체를 폐쇄망으로 반입하세요."
