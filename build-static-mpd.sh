#!/bin/sh
#
# Checkout and build a static version of mpd with all decoders
# compiled in, and shoutcast and alsa output (for testing)

# Checkout or update a pristine copy of the MPD trunk
if [ -d mpd ]; then
    cd mpd
    svn revert -R *
    svn update
else
    svn co https://svn.musicpd.org/mpd/trunk/ mpd
    cd mpd
fi

# Apply the Streamux machette-shoutcast patch
patch -p0 < ../mpd-seamless-icecast.patch

./autogen.sh --enable-static --disable-shared --disable-dependency-tracking --disable-ao --enable-shout --disable-sun --disable-pulse --disable-oss --enable-alsa
make LDFLAGS='-all-static'
cd ..
