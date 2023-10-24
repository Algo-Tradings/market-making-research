from research.async_prices import AsyncPrices
from research.sync_prices import SyncPrices


class Prices:
    """Class for interacting with exchanges."""
    def __init__(self, connection):
        if connection.is_async:
            self._prices = AsyncPrices(connection)
        else:
            self._prices = SyncPrices(connection)

    def __getattr__(self, name):
        # Delegate attribute access to the initialized connection
        return getattr(self._prices, name)
