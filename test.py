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
s.add("http://207.44.200.158:80/hard.ogg")

print "Playing for 15 seconds..."
time.sleep(15)

print "Adding Radio Rivendell to the list and staying 15 more seconds on HardRadio..."
s.add("http://82.182.121.75:8003/")
time.sleep(15)

print "Switching to Radio Rivendell for 15 seconds..."
s.next()
time.sleep(15)

print "Shutting down."
