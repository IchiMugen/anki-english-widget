# English Trainer for Anki - one-time installer for Windows.
# Run install.cmd (double-click). What it does:
#   1. Anki not installed?  -> downloads the official Anki installer and runs it
#   2. installs the add-on  -> %APPDATA%\Anki2\addons21\english_widget
#   3. downloads the offline voice (Piper + one voice model, ~135 MB) - once
#   4. imports the deck     -> opens English_Trainer.apkg in Anki
# Running it again is safe: it updates the add-on and skips what is already there.
param(
    [string]$Voice = "en_US-lessac-high",
    [string]$AnkiBase = "$env:APPDATA\Anki2",    # for testing: another Anki data folder
    [switch]$SkipDeck                              # for testing: don't open the deck
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

$PiperZip = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
$VoicePaths = @{
    "en_US-lessac-high" = "en_US/lessac/high/"
    "en_US-ryan-high"   = "en_US/ryan/high/"
    "en_GB-cori-high"   = "en_GB/cori/high/"
}
$VoiceBase = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/"

function Say($text) { Write-Host ""; Write-Host "== $text" -ForegroundColor Cyan }
function Get-File($url, $dest) {
    $tmp = "$dest.part"
    (New-Object Net.WebClient).DownloadFile($url, $tmp)
    Move-Item -Force $tmp $dest
}
function Find-Anki {
    foreach ($base in @($env:ProgramData, $env:APPDATA)) {
        $menu = Join-Path $base "Microsoft\Windows\Start Menu\Programs"
        $lnk = Get-ChildItem $menu -Recurse -Filter "Anki.lnk" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($lnk) { return $lnk.FullName }
    }
    return $null
}

if (-not $VoicePaths.ContainsKey($Voice)) { throw "Unknown voice '$Voice'. Use: $($VoicePaths.Keys -join ', ')" }

# 1. Anki
$anki = Find-Anki
if (-not $anki) {
    Say "Anki не найден - скачиваю официальный установщик (около 200 МБ)"
    $rel = Invoke-RestMethod "https://api.github.com/repos/ankitects/anki/releases/latest" -Headers @{ "User-Agent" = "anki-english-widget" }
    $arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "win-arm64.msi" } else { "win-x64.msi" }
    $asset = $rel.assets | Where-Object { $_.name -like "*$arch" } | Select-Object -First 1
    if (-not $asset) { throw "Не нашёл установщик Anki. Скачайте его вручную: https://apps.ankiweb.net" }
    $msi = Join-Path $env:TEMP $asset.name
    Get-File $asset.browser_download_url $msi
    Say "Устанавливаю Anki $($rel.tag_name) - подтвердите установку, если Windows спросит"
    $p = Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /qb" -Wait -PassThru
    if ($p.ExitCode -ne 0) { throw "Установка Anki не завершилась (код $($p.ExitCode))." }
    $anki = Find-Anki
}

# 2. the add-on (Anki must be closed so it picks the files up on start)
$running = Get-Process | Where-Object { $_.Path -and $_.Path -like "*\Anki\*" }
if ($running) {
    Say "Закройте Anki (в трее: правый клик по значку -> Выход) и нажмите Enter"
    Read-Host | Out-Null
}
$addons = Join-Path $AnkiBase "addons21"
$dest = Join-Path $addons "english_widget"
Say "Ставлю дополнение"
New-Item -ItemType Directory -Force $dest | Out-Null
Get-ChildItem (Join-Path $Here "addon\english_widget") -Exclude "user_files", "meta.json", "__pycache__" |
    Copy-Item -Destination $dest -Recurse -Force
$user = Join-Path $dest "user_files"
New-Item -ItemType Directory -Force $user | Out-Null

# 3. the voice
$piperDir = Join-Path $user "piper"
if (-not (Test-Path (Join-Path $piperDir "piper.exe"))) {
    Say "Скачиваю движок голоса Piper (22 МБ)"
    $zip = Join-Path $env:TEMP "piper_windows_amd64.zip"
    Get-File $PiperZip $zip
    $tmp = Join-Path $env:TEMP "piper_extract"
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    Expand-Archive $zip $tmp -Force
    if (Test-Path $piperDir) { Remove-Item -Recurse -Force $piperDir }
    Move-Item (Join-Path $tmp "piper") $piperDir
    Remove-Item -Recurse -Force $tmp, $zip
}
$voices = Join-Path $user "voices"
New-Item -ItemType Directory -Force $voices | Out-Null
foreach ($ext in @(".onnx.json", ".onnx")) {
    $f = Join-Path $voices "$Voice$ext"
    if (-not (Test-Path $f)) {
        if ($ext -eq ".onnx") { Say "Скачиваю голос $Voice (около 115 МБ)" }
        Get-File "$VoiceBase$($VoicePaths[$Voice])$Voice$ext" $f
    }
}
if ($Voice -ne "en_US-lessac-high") {
    $cfgPath = Join-Path $dest "config.json"
    $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
    $cfg.voice = $Voice
    $cfg | ConvertTo-Json | Set-Content -Encoding UTF8 $cfgPath
}

# 4. the deck
Say "Открываю колоду в Anki - подтвердите импорт"
if (-not (Test-Path $AnkiBase)) {
    Write-Host "Anki запустится впервые: выберите язык и профиль, импорт колоды начнётся сам."
}
if (-not $SkipDeck) { Start-Process (Join-Path $Here "English_Trainer.apkg") }

Say "Готово!"
Write-Host "Anki откроется виджетом. Значок в трее (у часов): правый клик - меню."
Write-Host "Совет: в меню значка включите 'Запускать вместе с системой'."
