from dotenv import load_dotenv, find_dotenv
from upstox_api.api import *
from . import daemon as daemon
import nsepy
import datetime
import pathlib
import os
import time
import json
import math


class TickerStore:
    UPSTOX = "upstox"
    YAHOO = "yahoo"
    NSE = "nse"

    INTERVAL_TICK_BY_TICK = 1
    INTERVAL_MINUTE_1 = 2
    INTERVAL_MINUTE_5 = 3
    INTERVAL_MINUTE_10 = 4
    INTERVAL_MINUTE_30 = 5
    INTERVAL_MINUTE_60 = 6
    INTERVAL_DAY_1 = 7
    INTERVAL_WEEK_1 = 8
    INTERVAL_MONTH_1 = 9

    def __init__(self, **kwargs):
        self.fetch_order = [
            TickerStore.UPSTOX,
            TickerStore.YAHOO,
            TickerStore.NSE,
        ]  # Default fetch order

        if "env_file" in kwargs:
            # Load everything from the environment file
            pass

    def set_fetch_order(self, fetch_order):
        if self.fetch_order is not None:
            self.fetch_order = fetch_order

    def historical_data(self, ticker, start_date, end_date, interval):
        for source in self.fetch_order:
            if source == TickerStore.UPSTOX:
                return self.upstox_historical_data(
                    ticker, start_date, end_date, interval
                )
            elif source == TickerStore.NSE:
                return self.nse_historical_data(ticker, start_date, end_date, interval)
            elif source == TickerStore.YAHOO:
                pass

    def upstox_historical_data(self, ticker, _from_date, _to_date, interval):
        """
        Fetches data from Influx DB.

        First it checks whether the data is present in DB or not.
        If yes, it simply returns the data. Else, it requests the
        ticker reporter to fetch the data from Upstox or Zerodha.

        Parameters
        ---------
            ticker: str
                A string of the form "<EXCHANGE>:<SYMBOL>" eg. NSE:RELIANCE
            _from_date: str
                Date from where historical data needs to be fetched. It should
                be of the form DD/MM/YYYY eg. 01/12/2018.
            _to_date: str
                Date uptil when you want the historical data. It should be of
                the form DD/MM/YYYY eg. 3/12/2018
            interval: int
                Make use of INTERVAL_* variables in tickerstore module to specify the
                time interval in which to operate on.

        Returns
        -------
        JSON
            A list of dictionaries is return. Each dictionary represents
            each time interval.

        """
        from_date = datetime.datetime.strptime(_from_date, "%d/%m/%Y").date()
        to_date = datetime.datetime.strptime(_to_date, "%d/%m/%Y").date()

        package_folder_path = pathlib.Path(__file__).parent
        access_token_file = package_folder_path / "access_token.file"

        # Access toke file exists
        if access_token_file.exists():
            with open(access_token_file, "r") as file:
                data = json.load(file)
                access_token_time = datetime.datetime.fromtimestamp(data["time"])
                present_time = datetime.datetime.fromtimestamp(int(time.time()))

                # Content in file is old, re-fetch access token
                if math.fabs(access_token_time.day - present_time.day) > 0:
                    # Again fetch the access_token
                    access_token = daemon.auth_upstox()
                    with open(access_token_file, "w") as z:
                        json.dump(
                            {"access_token": access_token, "time": int(time.time())}, z
                        )

                # Contents of file is new
                else:
                    access_token = data["access_token"]
                    print("Found access_token.file (Contents)--->")
                    print(data)

        # No access token file found
        else:
            access_token = daemon.auth_upstox()
            with open(access_token_file, "w") as file:
                json.dump(
                    {"access_token": access_token, "time": int(time.time())}, file
                )

        # Fetch the actual data
        u = Upstox(os.getenv("UPSTOX_API_KEY"), access_token)
        u.get_master_contract("NSE_EQ")
        instrument = u.get_instrument_by_symbol("NSE_EQ", ticker)

        # Fetching data depending on the interval specified
        data = None
        if interval == TickerStore.INTERVAL_MINUTE_1:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_1, from_date, to_date)
        elif interval == TickerStore.INTERVAL_MINUTE_5:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_5, from_date, to_date)
        elif interval == TickerStore.INTERVAL_MINUTE_10:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_10, from_date, to_date)
        elif interval == TickerStore.INTERVAL_MINUTE_30:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_30, from_date, to_date)
        elif interval == TickerStore.INTERVAL_MINUTE_60:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_60, from_date, to_date)
        elif interval == TickerStore.INTERVAL_DAY_1:
            data = u.get_ohlc(instrument, OHLCInterval.Day_1, from_date, to_date)
        elif interval == TickerStore.INTERVAL_WEEK_1:
            data = u.get_ohlc(instrument, OHLCInterval.Week_1, from_date, to_date)
        elif interval == TickerStore.INTERVAL_MONTH_1:
            data = u.get_ohlc(instrument, OHLCInterval.Month_1, from_date, to_date)

        return data

    def nse_historical_data(self, ticker, start_date, end_date, interval):
        start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y").date()
        end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").date()
        data = nsepy.get_history(symbol=ticker, start=start_date, end=end_date)
        return data
