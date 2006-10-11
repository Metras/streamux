#!/usr/bin/env python
#
# Streamux runner

def define_streamux_libs_path():
  import os.path
  import sys
  sys.path.append(os.path.abspath('libs'))

if __name__ == "__main__":
  define_streamux_libs_path()
  from streamux.main import StreamuxApp
  StreamuxApp().run()
