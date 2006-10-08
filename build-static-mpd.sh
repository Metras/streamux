#!/bin/sh
#
# Checkout and build a static version of mpd with all decoders
# compiled in, and shoutcast and alsa output (for testing)

VERSION="0.12.0"

svn export https://svn.musicpd.org/mpd/tags/release-$VERSION/ mpd
cd mpd
./autogen.sh
./configure --enable-static --disable-shared --disable-dependency-tracking --disable-ao --enable-shout --disable-sun --disable-pulse --disable-oss --enable-alsa
make LDFLAGS='-all-static'
mv src/mpd .
cd ..
