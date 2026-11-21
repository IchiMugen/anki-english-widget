#!/usr/bin/env bash
# English Trainer for Anki - one-time installer for Linux and macOS.
#   bash install.sh                     (voice: en_US-lessac-high)
#   bash install.sh en_US-ryan-high     (another voice)
# What it does:
#   1. Anki not installed? -> downloads the official Anki and installs it
#      (Linux: asks for your password for the system-wide install; macOS: copies to /Applications)
#   2. installs the add-on  -> <Anki data>/addons21/english_widget
#   3. downloads the offline voice (Piper + one voice model, ~135 MB) - once
#   4. imports the deck     -> opens English_Trainer.apkg in Anki
# Running it again is safe: it updates the add-on and skips what is already there.
set -euo pipefail

VOICE="${1:-en_US-lessac-high}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PIPER_RELEASE="https://github.com/rhasspy/piper/releases/download/2023.11.14-2"
VOICE_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/en"
case "$VOICE" in
  en_US-lessac-high) VPATH="en_US/lessac/high" ;;
  en_US-ryan-high)   VPATH="en_US/ryan/high" ;;
  en_GB-cori-high)   VPATH="en_GB/cori/high" ;;
  *) echo "Unknown voice: $VOICE (en_US-lessac-high | en_US-ryan-high | en_GB-cori-high)"; exit 1 ;;
esac

say() { printf '\n\033[36m== %s\033[0m\n' "$1"; }
fetch() { curl -fL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"; }

OS="$(uname -s)"; ARCH="$(uname -m)"
if [ "$OS" = "Darwin" ]; then
  BASE="${ANKI_BASE:-$HOME/Library/Application Support/Anki2}"
  case "$ARCH" in arm64|aarch64) PIPER_TGZ="piper_macos_aarch64.tar.gz" ;; *) PIPER_TGZ="piper_macos_x64.tar.gz" ;; esac
else
  BASE="${ANKI_BASE:-${XDG_DATA_HOME:-$HOME/.local/share}/Anki2}"
  case "$ARCH" in aarch64|arm64) PIPER_TGZ="piper_linux_aarch64.tar.gz" ;; armv7l) PIPER_TGZ="piper_linux_armv7l.tar.gz" ;; *) PIPER_TGZ="piper_linux_x86_64.tar.gz" ;; esac
fi

# 1. Anki
have_anki() {
  if [ "$OS" = "Darwin" ]; then [ -d "/Applications/Anki.app" ] || [ -d "$HOME/Applications/Anki.app" ]; else command -v anki >/dev/null 2>&1; fi
}
if ! have_anki; then
  say "Anki не найден - скачиваю официальную версию"
  TAG="$(curl -fsSL https://api.github.com/repos/ankitects/anki/releases/latest | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -1)"
  [ -n "$TAG" ] || { echo "Не удалось узнать версию Anki. Установите вручную: https://apps.ankiweb.net"; exit 1; }
  TMP="$(mktemp -d)"
  if [ "$OS" = "Darwin" ]; then
    case "$ARCH" in arm64|aarch64) PKG="anki-$TAG-mac-apple.dmg" ;; *) PKG="anki-$TAG-mac-intel.dmg" ;; esac
    fetch "https://github.com/ankitects/anki/releases/download/$TAG/$PKG" "$TMP/$PKG"
    MNT="$(hdiutil attach -nobrowse "$TMP/$PKG" | tail -1 | sed 's/.*\(\/Volumes\/.*\)/\1/')"
    cp -R "$MNT/Anki.app" /Applications/
    hdiutil detach "$MNT" >/dev/null
  else
    case "$ARCH" in aarch64|arm64) PKG="anki-$TAG-linux-aarch64.tar.zst" ;; *) PKG="anki-$TAG-linux-x86_64.tar.zst" ;; esac
    command -v zstd >/dev/null 2>&1 || { echo "Нужен zstd: sudo apt install zstd (или dnf/pacman), затем запустите скрипт снова."; exit 1; }
    fetch "https://github.com/ankitects/anki/releases/download/$TAG/$PKG" "$TMP/$PKG"
    tar --use-compress-program=unzstd -xf "$TMP/$PKG" -C "$TMP"
    say "Устанавливаю Anki $TAG (нужен пароль администратора)"
    (cd "$TMP"/anki-*-linux-*/ && sudo ./install.sh)
  fi
  rm -rf "$TMP"
fi

# 2. the add-on
if pgrep -fi "anki" >/dev/null 2>&1; then
  say "Закройте Anki (значок в трее -> Выход) и нажмите Enter"
  read -r _
fi
DEST="$BASE/addons21/english_widget"
say "Ставлю дополнение"
mkdir -p "$DEST/user_files"
( cd "$HERE/addon/english_widget" && for f in *; do [ "$f" = "user_files" ] || [ "$f" = "meta.json" ] || [ "$f" = "__pycache__" ] || cp -R "$f" "$DEST/"; done )

# 3. the voice
USERF="$DEST/user_files"
if [ ! -x "$USERF/piper/piper" ]; then
  say "Скачиваю движок голоса Piper"
  TMP="$(mktemp -d)"
  fetch "$PIPER_RELEASE/$PIPER_TGZ" "$TMP/piper.tgz"
  tar -xzf "$TMP/piper.tgz" -C "$TMP"
  rm -rf "$USERF/piper" && mv "$TMP/piper" "$USERF/piper" && chmod +x "$USERF/piper/piper"
  [ "$OS" = "Darwin" ] && xattr -dr com.apple.quarantine "$USERF/piper" 2>/dev/null || true
  rm -rf "$TMP"
fi
mkdir -p "$USERF/voices"
for ext in .onnx.json .onnx; do
  f="$USERF/voices/$VOICE$ext"
  if [ ! -f "$f" ]; then
    [ "$ext" = ".onnx" ] && say "Скачиваю голос $VOICE (около 115 МБ)"
    fetch "$VOICE_BASE/$VPATH/$VOICE$ext" "$f"
  fi
done
if [ "$VOICE" != "en_US-lessac-high" ]; then
  sed -i.bak "s/\"voice\": *\"[^\"]*\"/\"voice\": \"$VOICE\"/" "$DEST/config.json" && rm -f "$DEST/config.json.bak"
fi

# 4. the deck
say "Открываю колоду в Anki - подтвердите импорт"
if [ "$OS" = "Darwin" ]; then open "$HERE/English_Trainer.apkg"; else xdg-open "$HERE/English_Trainer.apkg" >/dev/null 2>&1 || anki "$HERE/English_Trainer.apkg" & fi

say "Готово!"
echo "Anki откроется виджетом. Значок в трее / строке меню: меню тренера."
echo "Совет: в меню значка включите «Запускать вместе с системой»."
