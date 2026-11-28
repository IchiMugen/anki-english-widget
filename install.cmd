@echo off
rem English Trainer for Anki - one-time installer (Windows). Double-click me.
rem Started straight from the .zip (Explorer copies only this file to a temp folder, install.ps1 is not next
rem to it): download the latest English-Trainer-Setup.zip from GitHub, unpack it and run the installer from there.
if exist "%~dp0install.ps1" goto run
echo English Trainer: downloading the installer from GitHub...
set "ETDIR=%TEMP%\English-Trainer-Setup-%RANDOM%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; New-Item -ItemType Directory -Force $env:ETDIR | Out-Null; $z=Join-Path $env:ETDIR 'setup.zip'; Invoke-WebRequest -UseBasicParsing 'https://github.com/IchiMugen/anki-english-widget/releases/latest/download/English-Trainer-Setup.zip' -OutFile $z; Expand-Archive -Force $z $env:ETDIR"
if errorlevel 1 goto fail
powershell -NoProfile -ExecutionPolicy Bypass -File "%ETDIR%\English-Trainer-Setup\install.ps1" %*
goto end
:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
goto end
:fail
echo Could not download the installer. Unpack English-Trainer-Setup.zip (right click - Extract All) and run install.cmd from the unpacked folder.
:end
pause
