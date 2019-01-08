from upstox_api.api import *
from . import daemon as daemon
from tickerstore.errors import SourceError
from tickerstore.errors import TickerStoreError
from dotenv import load_dotenv
import nsepy
import datetime
import pathlib
import pandas
import os
import time
import json
import math
import crayons


class TickerStore:
    UPSTOX = "upstox"
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
        self.fetch_order = [TickerStore.UPSTOX, TickerStore.NSE]  # Default fetch order

        # Load the values from .env files to Enviroment variable
        if "dotenv_path" in kwargs:
            load_dotenv(dotenv_path=kwargs["dotenv_path"])

        if (
            "upstox_api_key" in kwargs.keys()
            and "upstox_api_secret" in kwargs.keys()
            and "upstox_redirect_uri" in kwargs.keys()
            and "temp_server_auth_page" in kwargs.keys()
        ):
            os.environ["UPSTOX_API_KEY"] = kwargs["upstox_api_key"]
            os.environ["UPSTOX_API_SECRET"] = kwargs["upstox_api_secret"]
            os.environ["UPSTOX_REDIRECT_URI"] = kwargs["upstox_redirect_uri"]
            os.environ["TEMP_SERVER_AUTH_PAGE"] = kwargs["temp_server_auth_page"]

    def set_fetch_order(self, fetch_order):
        """
        Fetches data from multiple sources.

        Parameters
        ---------
            fetch_order: list
                Pass a list containing the order in which the historical data would be fetched.

        Returns
        -------
        None

        """
        if self.fetch_order is not None:
            self.fetch_order = fetch_order

    def get_fetch_order(self):
        """Returns the fetch order of historical data."""
        return self.fetch_order

    def historical_data(self, ticker, start_date, end_date, interval):
        """
        Fetches data from multiple sources.

        Parameters
        ---------
            ticker: str
                A string of the form "<EXCHANGE>:<SYMBOL>" eg. NSE:RELIANCE
            start_date: datetime.date
                Date from where historical data needs to be fetched. Eg. date(2018,1,1)
            end_date: datetime.date
                Date uptil which you want the historical data to be fetched. Eg. date(2018,6,1)
            interval: int
                Make use of INTERVAL_* variables in TickerStore class to specify the
                time interval in which to operate on.

        Returns
        -------
        JSON
            A list of dictionaries is return. Each dictionary represents
            each time interval.
        """
        historical_data = None
        for source in self.fetch_order:

            # Source: Upstox
            if source == TickerStore.UPSTOX:
                try:
                    historical_data = self.upstox_historical_data(
                        ticker, start_date, end_date, interval
                    )
                    break
                except SourceError as e:
                    print(crayons.red("Upstox source error: %s" % e, bold=True))

            # Source: NSE
            elif source == TickerStore.NSE:
                try:
                    historical_data = self.nse_historical_data(
                        ticker, start_date, end_date, interval
                    )
                    break
                except SourceError as e:
                    print(crayons.red("NSE source error: %s" % e, bold=True))

        if historical_data is None:
            raise TickerStoreError(
                "No source provided data for the requested time interval!"
            )

        return historical_data

    def upstox_historical_data(self, ticker, start_date, end_date, interval):
        """
        Fetches data from Upstox API

        Parameters
        ---------
            ticker: str
                A string of the form "<EXCHANGE>:<SYMBOL>" eg. NSE:RELIANCE
            start_date: datetime.date
                Date from where historical data needs to be fetched. Eg. date(2018,1,1)
            end_date: datetime.date
                Date uptil which you want the historical data to be fetched. Eg. date(2018,6,1)
            interval: int
                Make use of INTERVAL_* variables in tickerstore module to specify the
                time interval in which to operate on.

        Returns
        -------
        JSON
            A list of dictionaries is return. Each dictionary represents
            each time interval.

        """

        def verify_credentails():
            """Verify the given Upstox credentials and then proceed to fetch historical data."""

            api_key = os.getenv("UPSTOX_API_KEY", "temp")
            redirect_uri = os.getenv("UPSTOX_REDIRECT_URI", "temp")
            api_secret = os.getenv("UPSTOX_API_SECRET", "temp")

            if (
                api_key is not "temp"
                or redirect_uri is not "temp"
                or api_secret is not "temp"
            ):
                s = Session(os.getenv("UPSTOX_API_KEY"))
                s.set_redirect_uri(os.getenv("UPSTOX_REDIRECT_URI"))
                s.set_api_secret(os.getenv("UPSTOX_API_SECRET"))
                url = s.get_login_url()

                req = requests.get(url)
                print(req.status_code)
                if req.status_code != 200:
                    # Something, wrong with the API or credentials provided
                    info = req.json()
                    raise SourceError(str(info))
            else:
                raise SourceError("Invalid Upstox API Key and API Secret.")

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
                    verify_credentails()
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
            # If everything is fine, proceed to get the access token
            verify_credentails()
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
            data = u.get_ohlc(instrument, OHLCInterval.Minute_1, start_date, end_date)
        elif interval == TickerStore.INTERVAL_MINUTE_5:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_5, start_date, end_date)
        elif interval == TickerStore.INTERVAL_MINUTE_10:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_10, start_date, end_date)
        elif interval == TickerStore.INTERVAL_MINUTE_30:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_30, start_date, end_date)
        elif interval == TickerStore.INTERVAL_MINUTE_60:
            data = u.get_ohlc(instrument, OHLCInterval.Minute_60, start_date, end_date)
        elif interval == TickerStore.INTERVAL_DAY_1:
            data = u.get_ohlc(instrument, OHLCInterval.Day_1, start_date, end_date)
        elif interval == TickerStore.INTERVAL_WEEK_1:
            data = u.get_ohlc(instrument, OHLCInterval.Week_1, start_date, end_date)
        elif interval == TickerStore.INTERVAL_MONTH_1:
            data = u.get_ohlc(instrument, OHLCInterval.Month_1, start_date, end_date)

        # Data formatting
        formatted_data = pandas.DataFrame(data)
        formatted_data["timestamp"] = formatted_data["timestamp"] / 1000
        formatted_data["timestamp"] = formatted_data["timestamp"].apply(
            datetime.datetime.fromtimestamp
        )
        formatted_data = formatted_data.set_index("timestamp")
        formatted_data["Symbol"] = ticker
        formatted_data = formatted_data.rename(
            columns={
                "close": "Close",
                "high": "High",
                "low": "Low",
                "open": "Open",
                "volume": "Volume",
            }
        )
        formatted_data = formatted_data.drop(columns=["cp"])

        return formatted_data

    def nse_historical_data(self, ticker, start_date, end_date, interval):
        """
        Fetches data from Upstox API

        Parameters
        ---------
            ticker: str
                String representing the ticker symbol. eg. "SBIN"
            start_date: datetime.date
                Date from where historical data needs to be fetched. Eg. date(2018,1,1)
            end_date: datetime.date
                Date uptil which you want the historical data to be fetched. Eg. date(2018,6,1)
            interval: int
                Make use of INTERVAL_* variables in tickerstore module to specify the
                time interval in which to operate on.

        Returns
        -------
        JSON
            A list of dictionaries is return. Each dictionary represents
            each time interval.
        """
        if interval == TickerStore.INTERVAL_DAY_1:
            data = nsepy.get_history(symbol=ticker, start=start_date, end=end_date)
            formatted_data = data.copy(deep=True)
            formatted_data = formatted_data.drop(
                columns=[
                    "Series",
                    "Prev Close",
                    "VWAP",
                    "Turnover",
                    "Trades",
                    "Deliverable Volume",
                    "%Deliverble",
                    "Last",
                ]
            )
            return formatted_data
        else:
            raise SourceError("not available for requested time interval.")
