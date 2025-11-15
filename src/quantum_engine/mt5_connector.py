"""MetaTrader 5 connector for real-time market data."""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    logger.warning("MetaTrader5 not installed - using mock data")
    MT5_AVAILABLE = False


class MT5Connector:
    """
    MetaTrader 5 connection manager for market data streaming.

    Handles connection, data retrieval, and error recovery.
    """

    def __init__(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        timeout: int = 60000,
    ):
        """
        Initialize MT5 connector.

        Args:
            login: MT5 account number
            password: MT5 account password
            server: Broker server name
            timeout: Connection timeout in milliseconds

        Example:
            >>> connector = MT5Connector(login=12345, password="pass", server="Broker-Server")
            >>> connector.connect()
        """
        self.login = login
        self.password = password
        self.server = server
        self.timeout = timeout
        self.connected = False

        logger.info("MT5Connector initialized", extra={"mt5_available": MT5_AVAILABLE})

    def connect(self) -> bool:
        """
        Connect to MT5 terminal.

        Returns:
            True if connection successful, False otherwise

        Example:
            >>> if connector.connect():
            ...     print("Connected!")
        """
        if not MT5_AVAILABLE:
            logger.warning("MT5 not available - using mock mode")
            self.connected = False
            return False

        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False

            # Login if credentials provided
            if self.login and self.password and self.server:
                authorized = mt5.login(
                    login=self.login,
                    password=self.password,
                    server=self.server,
                    timeout=self.timeout,
                )

                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False

                logger.info(
                    f"MT5 connected: {self.login}@{self.server}",
                    extra={"login": self.login, "server": self.server},
                )
            else:
                logger.info("MT5 initialized without login")

            self.connected = True
            return True

        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """
        Disconnect from MT5 terminal.

        Example:
            >>> connector.disconnect()
        """
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 disconnected")

    def get_rates(
        self,
        symbol: str,
        timeframe: str = "H1",
        count: int = 100,
    ) -> Optional[pd.DataFrame]:
        """
        Get historical rates for symbol.

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D1)
            count: Number of bars to retrieve

        Returns:
            DataFrame with OHLCV data or None

        Example:
            >>> df = connector.get_rates("EURUSD", "H1", 100)
            >>> print(df[['close']].tail())
        """
        if not MT5_AVAILABLE or not self.connected:
            logger.warning("MT5 not connected - returning mock data")
            return self._generate_mock_data(symbol, count)

        try:
            # Map timeframe string to MT5 constant
            timeframe_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
            }

            tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)

            # Get rates
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)

            if rates is None or len(rates) == 0:
                logger.error(f"No rates for {symbol}: {mt5.last_error()}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")

            logger.info(
                f"Retrieved {len(df)} bars for {symbol} {timeframe}",
                extra={"symbol": symbol, "timeframe": timeframe, "count": len(df)},
            )

            return df

        except Exception as e:
            logger.error(f"Error getting rates for {symbol}: {e}")
            return None

    def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Get current bid/ask prices.

        Args:
            symbol: Trading symbol

        Returns:
            Dict with bid, ask, and spread

        Example:
            >>> price = connector.get_current_price("EURUSD")
            >>> print(f"Bid: {price['bid']}, Ask: {price['ask']}")
        """
        if not MT5_AVAILABLE or not self.connected:
            logger.warning("MT5 not connected - returning mock price")
            return {"bid": 1.1000, "ask": 1.1002, "spread": 0.0002}

        try:
            tick = mt5.symbol_info_tick(symbol)

            if tick is None:
                logger.error(f"No tick for {symbol}: {mt5.last_error()}")
                return None

            return {
                "bid": tick.bid,
                "ask": tick.ask,
                "spread": tick.ask - tick.bid,
                "time": datetime.fromtimestamp(tick.time),
            }

        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

    def get_symbols(self) -> List[str]:
        """
        Get list of available symbols.

        Returns:
            List of symbol names

        Example:
            >>> symbols = connector.get_symbols()
            >>> print(symbols[:5])
        """
        if not MT5_AVAILABLE or not self.connected:
            return ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                logger.error(f"Failed to get symbols: {mt5.last_error()}")
                return []

            return [s.name for s in symbols]

        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []

    def _generate_mock_data(self, symbol: str, count: int) -> pd.DataFrame:
        """
        Generate mock price data for testing.

        Args:
            symbol: Trading symbol
            count: Number of bars

        Returns:
            DataFrame with mock OHLCV data
        """
        import numpy as np

        # Generate realistic price movement
        base_price = 1.1000 if "EUR" in symbol else 1.2500
        volatility = 0.001

        times = pd.date_range(end=datetime.now(), periods=count, freq="H")
        returns = np.random.normal(0, volatility, count)
        prices = base_price * (1 + returns).cumprod()

        df = pd.DataFrame(
            {
                "time": times,
                "open": prices * (1 + np.random.uniform(-0.0001, 0.0001, count)),
                "high": prices * (1 + np.random.uniform(0, 0.0005, count)),
                "low": prices * (1 + np.random.uniform(-0.0005, 0, count)),
                "close": prices,
                "tick_volume": np.random.randint(100, 1000, count),
            }
        )

        logger.debug(f"Generated {count} mock bars for {symbol}")
        return df

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
