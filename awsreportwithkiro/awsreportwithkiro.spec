# -*- mode: python ; coding: utf-8 -*-
# ##################################################################################################
# PyInstaller spec - awsreportwithkiro 단일 실행파일(onefile) 빌드
# Developer : k.s.k & kiro
#
# 빌드(인터넷 가능 PC, 폐쇄망과 동일 OS 에서):
#   pip install -r requirements.txt pyinstaller
#   pyinstaller awsreportwithkiro.spec --clean
# 산출물: dist/awsreportwithkiro(.exe)  (단일 실행파일)
#
# 주의: PyInstaller 는 크로스컴파일 불가. Windows 대상이면 Windows 에서,
#       Linux 대상이면 Linux 에서 빌드할 것.
# ##################################################################################################
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# 설정/로그 conf 를 번들에 포함 (런타임에 sys._MEIPASS 에서 로드)
datas = [
    ("kskpkg/config/logging.conf", "kskpkg/config"),
    ("kskpkg/config/settings.yaml", "kskpkg/config"),
]
# boto3/botocore 의 서비스 모델 JSON(endpoints/service-2.json 등)을 반드시 포함해야
# 폐쇄망에서 client 생성이 된다. (동적 로드되므로 data 로 명시 수집)
datas += collect_data_files("botocore")
datas += collect_data_files("boto3")

# 동적 import 되는 모듈들을 hiddenimports 로 포함
hiddenimports = []
hiddenimports += collect_submodules("botocore")
hiddenimports += collect_submodules("boto3")
# 서비스 모듈은 importlib 로 동적 로드되므로 명시적으로 포함
hiddenimports += collect_submodules("kskpkg")

a = Analysis(
    ["awsreportwithkiro.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="awsreportwithkiro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
