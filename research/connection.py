from research.sync_connection import SyncConnection
from research.async_connection import AsyncConnection


class Connection:
    """Class for interacting with exchanges."""
    def __init__(self, is_async_mode=True):
        self.is_async = is_async_mode

        if self.is_async:
            self.__connection = AsyncConnection()
        else:
            self.__connection = SyncConnection()

    def __getattr__(self, name):
        # Delegate attribute access to the initialized connection
        return getattr(self.__connection, name)
