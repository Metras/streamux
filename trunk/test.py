import os
import os.path
import sys
import time
import atexit
import ConfigParser

sys.path.append(os.path.abspath('libs'))

from streamux.streamer import Streamer

if len(sys.argv) != 2:
  print "Usage: %s <configuration file>" % os.path.basename(sys.argv[0])
  sys.exit(1)

# Load configuration file
conf = ConfigParser.SafeConfigParser()
conf.read(sys.argv[1])

# Create an MpdRunner
s = Streamer(conf)

print "Streamer booted, adding HardRadio to the playlist and starting playback"
print ("MPD is running on port %d , using password %s "
       "(not supposed to tell you this, but useful for debugging)" %
       (s._mpd_runner.port, s._mpd_runner.password))
print "ncmpc -p %d -P %s" % (s._mpd_runner.port, s._mpd_runner.password)

raw_input("Hit enter to continue...")

s.add("http://207.44.200.158:80/hard.ogg")
s.add("http://ogg.smgradio.com/vx160.ogg")
s.add("http://207.44.200.158:80/hard.ogg")
s.add("http://ogg.smgradio.com/vx160.ogg")

print "Playing each enqueued URL for 10 seconds before switching to the next..."
while True:
  print "Currently playing '%s'" % s.status()[2]
  time.sleep(10)
  playing, n_tracks, url, changed = s.status()
  if not n_tracks:
    break
  s.next()

print "All tracks have been played 5 seconds!"
print "Shutting down."
