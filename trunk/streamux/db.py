# Streamux database interface component.
#

import logging
import sys

import sqlalchemy as sqla

import streamux.main

class StreamuxDatabase(object):
  """The database component holds a reference to SqlAlchemy metadata,
  which components may request to store their data."""

  def __init__(self, config):
    """Verify configuration and initialize a connection to the
    database."""

    if not config.has_section('db'):
      streamux.main.error_and_exit("Section [db] is missing "
                                   "from the configuration.")
    elif not config.has_option('db', 'url'):
      streamux.main.error_and_exit("Missing database URL "
                                   "from the db configuration.")

    self._db_url = config.get('db', 'url')
    self._db = sqla.create_engine(self._db_url)
    self._meta = sqla.BoundMetaData(self._db)
    self._log = logging.getLogger("db")
    self._log.info("Database initialized")

  def get_db(self):
    """Return the DB metadata object to the caller, so that he can
    attach schemas and objects to it."""
    return self._meta
