import os
import os.path
import sys
import time
import atexit

from streamux.streamer import MpdRunner

# Icecast stream configuration
c = {'mount':'/streamux.ogg', 'password':'Rie4alau'}

# Create an MpdRunner
m = MpdRunner(c, mpd_bin='/home/danderson/pythonstuff/streamux/mpd/mpd')
m.run()

print "Running MPD from %s, on port %d" % (m._rundir, m._port)
print "Sleeping for 60 seconds..."
time.sleep(60)
print "Shutting down MPD and clearing up"
m.stop()
