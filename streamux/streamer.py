# Streamer component
#
# Connects to an MPD instance using py-mpdclient2 and drives it.

import random
import tempfile
import os.path
import subprocess
import signal

import streamux.error

class StreamuxStreamerError(streamux.error.StreamuxError):
  """Streamer error"""

class MpdRunner(object):
  """Encapsulates a control thread that runs an instance of MPD with a
  configuration suitable for Streamux streaming."""

  def __init__(self, stream_config, mpd_bin="mpd"):
    """Initialize a runner with an empty configuration."""
    self._mpd_bin = mpd_bin
    self._port = random.randint(10000,65000)
    self._rundir = tempfile.mkdtemp(".run","mpd_")
    self._config = { 'port':str(self._port),
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
    print config
    fd, config_fname = tempfile.mkstemp(".conf", "mpd", self._rundir, text=True)
    os.write(fd, config)
    os.close(fd)
    return config_fname

  def run(self):
    """Build the MPD configuration and start an MPD instance with that
    config."""
    if hasattr(self, "_pid"):
      raise StreamuxStreamerError

    self._config_fname = self._build_mpd_config()
    nothing = open('/dev/null', 'r+')
    self._mpd = subprocess.Popen(['mpd.streamux', self._config_fname],
                                 executable=self._mpd_bin,
                                 close_fds=True,
                                 cwd=self._rundir,
                                 stdin=nothing,
                                 stdout=nothing,
                                 stderr=nothing,
                                 env={})

  def stop(self):
    """Stop the previously started MPD instance and remove its
    temporary data directory."""
    if not hasattr(self, "_mpd"):
      raise StreamuxStreamerError
    p = subprocess.Popen([self._mpd_bin, "--kill", self._config_fname])
    p.wait()
    self._mpd.wait()

    # Delete everything in the runtime mpd directory.
    for root,dirs,files in os.walk(self._rundir, topdown=False):
      for name in files:
        os.remove(os.path.join(root, name))
      for name in dirs:
        os.rmdir(os.path.join(root, name))
    os.rmdir(self._rundir)
