# Streamux main class
#
# The Streamux main class aggregates the functionality of the other
# components and handles initialization.

import sys
import logging
import optparse
import ConfigParser

__version__ = "dev build"

class StreamuxApp(object):
  """Main Streamux class. Handles application initialization."""

  def error(self, msg):
    """Log the given message as critical, or print it if logging isn't
    yet set up, and exit with an exit code 1."""
    if hasattr(self, "_log"):
      self._log.critical(msg)
    else:
      sys.stderr.write("%s\n" % msg)
    sys.exit(1)

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
      self.error("Parse error while reading the configuration file.")
    except ConfigParser.InterpolationError:
      self.error("Variable interpolation error while reading the configuration file.")

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
      logging.info("Logging initialized in debug mode")
    else:

      log_levels = { 'error': logging.ERROR,
                     'warn': logging.WARN,
                     'info': logging.INFO,
                     'debug': logging.DEBUG }

      # Check configuration
      if not self.config.has_section('logging'):
        self.error("Section [logging] is missing from the configuration.")
      elif not self.options.debug and (not self.config.has_option('logging', 'level') or
                                       not self.config.has_option('logging', 'file')):
        self.error("Missing configuration attributes for logging.")

      level_str = self.config.get('logging', 'level')
      if level_str not in log_levels.keys():
        self.error("Log level must be one of: %s" % ', '.join(log_levels.keys()))

      # Set up logging according to the configuration
      logging.basicConfig(format=log_format,
                          datefmt=date_format,
                          level=log_levels[level_str],
                          filename=self.config.get('logging', 'file'))


  def run(self):
    self._parse_args()
    self._load_config()
    self._setup_logging()
