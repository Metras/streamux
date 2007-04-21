# -*- coding: utf-8 -*-

import os
import sys
import time

from twisted.web import xmlrpc, server
from twisted.internet import reactor, threads
from twisted.internet.defer import Deferred

import ConfigParser

pathname = os.path.dirname(sys.argv[0])
if pathname == "":
    pathname = "."
sys.path.append(os.path.abspath(pathname+'/libs'))

from streamux.streamer import Streamer

class strD(xmlrpc.XMLRPC):

  def __init__(self):
    # Load configuration file
    self._conf = ConfigParser.SafeConfigParser()
    self._conf.read(sys.argv[1])
    self._s = Streamer(self._conf)
    print "Streamer booted, adding HardRadio to the playlist and starting playback"
    print ("MPD is running on port %d , using password %s "
           "(not supposed to tell you this, but useful for debugging)" %
          (self._s._mpd_runner.port, self._s._mpd_runner.password))
    print "ncmpc -p %d -P %s" % (self._s._mpd_runner.port, self._s._mpd_runner.password)

  def xmlrpc_addid(self, track_url, user="", password=""):
    return self._s.addid(track_url, user, password)

  def xmlrpc_playid(self, tid, user="", password=""):
    self._s.playid(tid, user, password)
    return True

  def xmlrpc_seekid(self, tid, postime, user="", password=""):
    self._s.seekid(tid, postime, user, password)
    return True

  def xmlrpc_delid(self, tid, user="", password=""):
    self._s.delid(tid, user, password)
    return True

  def xmlrpc_next(self, user="", password=""):
    self._s.next(user, password)
    return True

  def xmlrpc_stop(self, user="", password=""):
    self._s.stop(user, password)
    return True
  
  def xmlrpc_update(self, dirname, user="", password=""):
    self._s.update(dirname, user, password)
    return True

  def xmlrpc_status(self, user="", password=""):
    return self._s.status(user, password)

  def xmlrpc_playing(self, user="", password=""):
    return self._s.playing(user, password)

if __name__ == '__main__':
    r = strD()
    conf = ConfigParser.SafeConfigParser()
    conf.read(sys.argv[1])
    xmlrpc_config = dict(conf.items('xmlrpc'))
    reactor.listenTCP(int(xmlrpc_config['port']), server.Site(r))
    reactor.run()
