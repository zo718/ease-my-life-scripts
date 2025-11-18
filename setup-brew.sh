#!/usr/bin/env bash
#version 1.0 - Written by Alfredo Jo ® - 2025

#fail safe statement
set -euo pipefail

#Install Homebrew if missing

if ! command -v brew >/dev/null 2>&1; then
  echo "[*] Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  # Add brew to PATH for this script run
  if [ -d "/opt/homebrew/bin" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -d "/usr/local/bin" ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
else
  echo "[*] Homebrew is already installed."
fi

echo "[*] Running brew update..."
brew update

#Formulae to install. Paste the output of `brew list --formula` from your old Mac here. Add or remove as needed.

FORMULAE=(
  aom
  aribb24
  autoconf
  boxes
  brotli
  c-ares
  ca-certificates
  cairo
  capstone
  cjson
  dav1d
  dtc
  ffmpeg
  flac
  fontconfig
  fortune
  freerdp
  freetype
  frei0r
  fribidi
  gcc
  gdbm
  gettext
  giflib
  git
  glib
  gmp
  gnupg
  gnutls
  graphite2
  harfbuzz
  highway
  hping
  htop
  icu4c
  icu4c@76
  icu4c@77
  imagemagick
  imath
  iperf
  isl
  jansson
  jemalloc
  jq
  lame
  leptonica
  libass
  libavif
  libb2
  libbluray
  libde265
  libdeflate
  libevent
  libffi
  libgcrypt
  libgpg-error
  libidn2
  libksba
  liblinear
  libmicrohttpd
  libmpc
  libnet
  libnghttp2
  libogg
  libpng
  librist
  libsamplerate
  libslirp
  libsndfile
  libsodium
  libsoxr
  libssh
  libssh2
  libtasn1
  libtiff
  libtool
  libunistring
  libusb
  libvorbis
  libvpx
  libx11
  libxau
  libxcb
  libxcursor
  libxdmcp
  libxext
  libxfixes
  libxi
  libxinerama
  libxrandr
  libxrender
  libyaml
  little-cms2
  lua
  lz4
  lzo
  m4
  mbedtls
  mpdecimal
  mpfr
  mpg123
  mtr
  ncurses
  net-snmp
  nettle
  nmap
  node
  npth
  oniguruma
  opencore-amr
  openexr
  openjpeg
  openssl@3
  opus
  p11-kit
  pango
  pcre
  pcre2
  pinentry
  pinentry-mac
  pixman
  pkcs11-helper
  pkgconf
  powerlevel10k
  python-packaging
  python@3.10
  python@3.12
  python@3.13
  python@3.9
  qemu
  rav1e
  readline
  rubberband
  ruby
  sdl2
  sdl3
  sdl3_ttf
  snappy
  speex
  sqlite
  srt
  sshpass
  step
  svt-av1
  tcptraceroute
  telnet
  terraform
  tesseract
  the_silver_searcher
  theora
  unbound
  vde
  vim
  webp
  wget
  x264
  x265
  xorgproto
  xvid
  xz
  zeromq
  zimg
  zsh-syntax-highlighting
  zstd
)

#Casks to install. Paste the output of `brew list --cask` here from your old Mac.

CASKS=(
  1password-cli
  adoptopenjdk
  apache-directory-studio
  hashicorp-vagrant
  oracle-jdk
  temurin
  vagrant
  vagrant-vmware-utility
  xquartz
)

#Install everything

echo "[*] Installing formulae..."
for pkg in "${FORMULAE[@]}"; do
  if brew list --formula "$pkg" >/dev/null 2>&1; then
    echo "    [skip] $pkg already installed"
  else
    echo "    [install] $pkg"
    brew install "$pkg"
  fi
done

echo "[*] Installing casks..."
for cask in "${CASKS[@]}"; do
  if brew list --cask "$cask" >/dev/null 2>&1; then
    echo "    [skip] $cask already installed"
  else
    echo "    [install] $cask"
    brew install --cask "$cask"
  fi
done

echo "[*] All done."
