"""
SFTP Storage object.
"""
import os
import tempfile
from django.conf import settings
from pysftp import Connection

from .base import BaseStorage, StorageError
from .. import settings as dbbackup_settings


class Storage(BaseStorage):
    """ SFTP Storage """
    name = 'SFTP'
    SFTP_HOST = getattr(settings, 'DBBACKUP_SFTP_HOST', None)
    SFTP_USER = getattr(settings, 'DBBACKUP_SFTP_USER', None)
    SFTP_PASSWORD = getattr(settings, 'DBBACKUP_SFTP_PASSWORD', None)
    SFTP_PATH = getattr(settings, 'DBBACKUP_SFTP_PATH', ".")
    SFTP_PATH = '/%s/' % SFTP_PATH.strip('/')
    SFTP_PASSIVE_MODE = getattr(settings, 'DBBACKUP_SFTP_PASSIVE_MODE', False)

    def __init__(self, server_name=None):
        self._check_settings()
        self.sftp = Connection(host=self.SFTP_HOST, username=self.SFTP_USER,
                               password=self.SFTP_PASSWORD)

    def _check_settings(self):
        """Check we have all the required settings defined."""
        if not self.SFTP_HOST:
            msg = '%s storage requires DBBACKUP_SFTP_HOST to be defined in settings.' % self.name
            raise StorageError(msg)

    @property
    def backup_dir(self):
        return self.SFTP_PATH

    def delete_file(self, filepath):
        """Delete the specified filepath."""
        self.sftp.remove(filepath)

    def list_directory(self, raw=False):
        """List all stored backups for the specified."""
        return sorted(self.sftp.listdir(self.SFTP_PATH))

    def write_file(self, filehandle, filename):
        """Write the specified file."""
        filehandle.seek(0)
        backuppath = os.path.join(self.SFTP_PATH, filename)
        self.sftp.putfo(filehandle, backuppath)

    def read_file(self, filepath):
        """Read the specified file and return it's handle."""
        outputfile = tempfile.SpooledTemporaryFile(
            max_size=dbbackup_settings.TMP_FILE_MAX_SIZE,
            dir=dbbackup_settings.TMP_DIR)
        self.sftp.getfo(filepath, outputfile)
        return outputfile
