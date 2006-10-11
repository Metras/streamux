# Streamux main class
#
# The Streamux main class aggregates the functionality of the other
# components and handles initialization.

import sys
import logging
import optparse
import ConfigParser

import streamux.db

__version__ = "dev build"

def error_and_exit(msg):
  """Log the given message as critical and exit with exit code 1."""
  logging.critical(msg)
  sys.exit(1)

class StreamuxApp(object):
  """Main Streamux class. Handles application initialization."""

  def _parse_args(self):
    """Parse the commandline arguments and store them in the app
    object. Exits if something is wrong, otherwise returns after
    assigning self.options and self.config_file."""

    usage = "usage: %prog [options] <configuration file>"
    version = "%%prog %s" % __version__

    parser = optparse.OptionParser(usage=usage, version=version)
    parser.set_defaults(debug=False)
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help=("Enable verbose logging to stdout, "
                            "and don't fork into the background."))
    self.options, args = parser.parse_args()
    if len(args) != 1:
      parser.error("You must supply a configuration file.")
    self.config_file = args[0]

  def _load_config(self):
    """Load the configuration file into self.config."""

    self.config = ConfigParser.SafeConfigParser()
    fd = open(self.config_file, 'r')

    try:
      self.config.readfp(fd)
    except ConfigParser.ParsingError:
      error_and_exit("Parse error while reading the configuration file.")
    except ConfigParser.InterpolationError:
      error_and_exit("Variable interpolation error while reading the configuration file.")

    fd.close()

  def _setup_logging(self):
    """Set up the logging infrastructure using the given configuration
    information in the 'logging' section."""

    log_format = '%(asctime)s (%(levelname)s) %(message)s'
    date_format = '%c'

    # If in debug mode, completely ignore the configuration and setup
    # a debug logger on stdout.
    if self.options.debug:
      logging.basicConfig(format=log_format,
                          datefmt=date_format,
                          level=logging.DEBUG,
                          stream=sys.stderr)
    else:

      log_levels = { 'error': logging.ERROR,
                     'warn': logging.WARN,
                     'info': logging.INFO,
                     'debug': logging.DEBUG }

      # Check configuration
      if not self.config.has_section('logging'):
        error_and_exit("Section [logging] is missing from the configuration.")
      elif not self.options.debug and (not self.config.has_option('logging', 'level') or
                                       not self.config.has_option('logging', 'file')):
        error_and_exit("Missing configuration attributes for logging.")

      level_str = self.config.get('logging', 'level')
      if level_str not in log_levels.keys():
        error_and_exit("Log level must be one of: %s" % ', '.join(log_levels.keys()))

      # Set up logging according to the configuration
      logging.basicConfig(format=log_format,
                          datefmt=date_format,
                          level=log_levels[level_str],
                          filename=self.config.get('logging', 'file'))

    logging.info("Logger initialized%s" % (self.options.debug and " in debug mode" or ""))

  def _start_components(self):
    """Start the components of Streamux in the correct init order."""
    db = streamux.db.StreamuxDatabase(self.config)

  def run(self):
    self._parse_args()
    self._load_config()
    self._setup_logging()
    self._start_components()
