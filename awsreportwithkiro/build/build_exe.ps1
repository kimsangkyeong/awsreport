# ##################################################################################################
# [방법 B] 단일 실행파일(.exe) 빌드 (Windows)
# Developer : k.s.k & kiro
#
# 전제: 인터넷 가능 PC, 폐쇄망 대상과 '동일한 Windows/아키텍처'.
# 사용:
#   powershell -ExecutionPolicy Bypass -File .\build\build_exe.ps1
# 산출물: dist\awsreportwithkiro.exe  (단일 실행파일, 대상 PC 에 Python 불필요)
#
# 반입물: dist\awsreportwithkiro.exe  +  settings.yaml(수정용, 선택)
# 실행(폐쇄망):  .\awsreportwithkiro.exe --profile <name> --region ap-northeast-2
# ##################################################################################################
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "[1/3] 빌드 의존성 설치 (requirements + pyinstaller)"
python -m pip install -r requirements.txt pyinstaller

Write-Host "[2/3] 이전 빌드 정리"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build\awsreportwithkiro, dist

Write-Host "[3/3] PyInstaller 빌드"
python -m PyInstaller awsreportwithkiro.spec --clean --noconfirm

Write-Host ""
if (Test-Path "dist\awsreportwithkiro.exe") {
  Write-Host "완료: dist\awsreportwithkiro.exe"
  Write-Host "이 exe 를 폐쇄망으로 반입 후 실행:"
  Write-Host "  .\awsreportwithkiro.exe --profile <name> --region ap-northeast-2"
} else {
  Write-Host "빌드 산출물을 찾지 못했습니다. 로그를 확인하세요."
}
