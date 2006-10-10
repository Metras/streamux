# Streamer component
#
# Connects to an MPD instance using py-mpdclient2 and drives it.

import random
import tempfile
import os.path
import subprocess
import signal
import atexit
import time

import mpdclient2

import streamux.error

class StreamuxStreamerError(streamux.error.StreamuxError):
  """Streamer error"""

class MpdRunner(object):
  """Encapsulates a control thread that runs an instance of MPD with a
  configuration suitable for Streamux streaming."""

  def __init__(self, stream_config, mpd_bin="mpd"):
    """Initialize a runner with an empty configuration."""
    self._mpd_bin = mpd_bin
    self.port = random.randint(10000,65000)
    self.password = ''.join([random.choice("abcdefghijkmnopqrstuvwxyz0123456789")
                             for x in xrange(8)])
    self._rundir = tempfile.mkdtemp(".run","mpd_")
    self._config = { 'port':str(self.port),
                     'password':"%s@read,add,control,admin" % self.password,
                     'music_directory':self._rundir,
                     'playlist_directory':self._rundir,
                     'log_file':os.path.join(self._rundir, 'log'),
                     'error_file':os.path.join(self._rundir, 'error'),
                     'db_file':os.path.join(self._rundir, 'db'),
                     'pid_file':os.path.join(self._rundir, 'pid')}
    self._set_stream(stream_config)

  def _set_stream(self, stream):
    """Set the output stream of MPD according to the given
    configuration dictionary. The valid values and meanings of these
    values correspond to the MPD Shout streaming configuration
    values."""
    self._stream = { 'type':'shout',
                     'name':'Streamux',
                     'host':'localhost',
                     'port':'8000',
                     'quality':'5.0',
                     'format':'44100:16:2',
                     'user': 'source' }
    self._stream.update(stream)

  def _dict_to_mpd_config(self, config):
    """Take a dictionary of configuration key/value pairs, and return
    a string representing that configuration in MPD's configuration
    format."""
    config_file = []
    for k,v in config.items():
      config_file.append("%s \"%s\"" % (k,v))
    config_file.append("")

    return '\n'.join(config_file)

  def _build_mpd_config(self):
    """Write out the current MPD configuration (given by self._config
    and self._stream) to a file in the MPD temporary runtime
    directory, and return the path to the file."""
    stream_config = "audio_output {\n%s}" % self._dict_to_mpd_config(self._stream)
    config = self._dict_to_mpd_config(self._config) + stream_config
    fd, config_fname = tempfile.mkstemp(".conf", "mpd", self._rundir, text=True)
    os.write(fd, config)
    os.close(fd)
    return config_fname

  def run(self):
    """Build the MPD configuration and start an MPD instance with that
    config."""
    if hasattr(self, "_running"):
      raise StreamuxStreamerError

    self._config_fname = self._build_mpd_config()
    nothing = open('/dev/null', 'r+')
    mpd = subprocess.Popen(['mpd.streamux', self._config_fname],
                           executable=self._mpd_bin,
                           close_fds=True,
                           cwd=self._rundir,
                           stdin=nothing,
                           stdout=nothing,
                           stderr=nothing,
                           env={})
    # Wait for the parent MPD process to fork off
    mpd.wait()
    self._running = True

  def stop(self):
    """Stop the previously started MPD instance and remove its
    temporary data directory."""
    if not hasattr(self, "_running"):
      raise StreamuxStreamerError
    p = subprocess.Popen([self._mpd_bin, "--kill", self._config_fname])
    p.wait()

    # Delete everything in the runtime mpd directory, ignoring errors
    # at this stage.
    for root,dirs,files in os.walk(self._rundir, topdown=False):
      for name in files:
        try:
          os.remove(os.path.join(root, name))
        except:
          pass
      for name in dirs:
        try:
          os.rmdir(os.path.join(root, name))
        except:
          pass
    os.rmdir(self._rundir)


class Streamer(object):
  """Main streamer class. Takes a configuration file and creates an
  MPD instance ready to stream."""

  def __init__(self, config):
    streamer_config = dict(config.items('streamer'))

    if streamer_config.has_key('mpd'):
      mpd = config.get('streamer', 'mpd')
      del streamer_config['mpd']
    else:
      mpd = 'mpd'

    self._mpd_runner = MpdRunner(streamer_config, mpd_bin=mpd)
    self._mpd_runner.run()
    atexit.register(self._mpd_runner.stop)
    self._client = mpdclient2.connect(port=self._mpd_runner.port,
                                      password=self._mpd_runner.password)

    # Clear any existing playlist
    self._last_track_id = -1
    self._client.clear()
    self._client.random(0)
    self._client.repeat(0)
    self._client.crossfade(2)

  def _prune_playlist(self):
    """Remove tracks that have already been played from the
    playlist."""
    c = self._client.currentsong()
    for _ in xrange(int(c.pos)):
      self._client.delete(0)

  def add(self, track_url):
    """Add an URI to the playlist."""
    self._client.add(track_url)
    s = self._client.status()
    if s.state != "play":
      self._client.play(0)
      self.status()
    self._prune_playlist()

  def next(self):
    """Start playing the next track in the list immediately, without
    waiting for the previous one to end. This also calls status(), so
    that future calls to it don't notify of this track change, as it
    is known already."""
    self._client.next()
    self._prune_playlist()
    self.status()

  def status(self):
    """Return a 4-tuple giving a status summary of the streamer:
    (playing, play_url, songs_in_queue, track_changed). playing is a
    boolean indicating whether something is currently streaming,
    play_url gives the URL of the currently playing (or previously
    playing if stopped) entry, songs_in_queue gives the number of
    entries in the queue *after* the current one, and track_changed is
    a boolean indicating whether the track currently playing has
    changed since the last call to status()."""
    s = self._client.status()
    c = self._client.currentsong()
    if s.state == "play":
      playing = True
      songs_in_queue = int(s.playlistlength) - int(s.song) - 1
      if self._last_track_id != s.songid:
        self._last_track_id = s.songid
        track_changed = True
      else:
        track_changed = False
      fname = c.file
    else:
      playing = False
      songs_in_queue = int(s.playlistlength)
      track_changed = False
      fname = ""

    return (playing, songs_in_queue, fname, track_changed)
