from upstox_api.api import *
from . import daemon as daemon
from tickerstore.errors import SourceError
from tickerstore.errors import TickerStoreError
from dotenv import load_dotenv
from loguru import logger
import nsepy
import datetime
import pathlib
import pandas
import os
import time
import json
import math
import crayons
import urllib3
import pandas as pd

logger.add("TickerStore.log", rotation="50 MB")


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
        logger.info("Creating TickerStore instance object")

        # Initializing object with default values
        self.fetch_order = [TickerStore.UPSTOX, TickerStore.NSE]  # Default fetch order
        self.upstox_credentials_verified = (
            False
        )  # To make sure upstox credentials are correct
        self.upstox_access_token = None  # For storing the upstox access token
        self.access_token_file_path = None  # path for access token file

        # Load the values from .env files to Enviroment variable
        if "dotenv_path" in kwargs:
            logger.info("dotfile path was passed. Loading dotfile")
            load_dotenv(dotenv_path=kwargs["dotenv_path"])
            self.__upstox_verify_credentails()
            logger.info("dotfile loaded")

        if (
            "upstox_api_key" in kwargs.keys()
            and "upstox_api_secret" in kwargs.keys()
            and "upstox_redirect_uri" in kwargs.keys()
            and "temp_server_auth_page" in kwargs.keys()
        ):
            logger.info("making upstox API key, secret as enviroment variables.")
            os.environ["UPSTOX_API_KEY"] = kwargs["upstox_api_key"]
            os.environ["UPSTOX_API_SECRET"] = kwargs["upstox_api_secret"]
            os.environ["UPSTOX_REDIRECT_URI"] = kwargs["upstox_redirect_uri"]
            os.environ["TEMP_SERVER_AUTH_PAGE"] = kwargs["temp_server_auth_page"]
            self.__upstox_verify_credentails()

        if "access_token_file_path" in kwargs.keys():
            self.access_token_file_path = kwargs["access_token_file_path"]
            logger.debug(
                f"Specified a custom path for access_token.file: {self.access_token_file_path}"
            )

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
        logger.info("Starting to fetch historical data")
        historical_data = None
        for source in self.fetch_order:

            # Source: Upstox
            if source == TickerStore.UPSTOX and self.upstox_credentials_verified:

                # Fetching data from upstox
                logger.info("Trying source UPSTOX for fetching historical data")
                try:
                    logger.info("Calling upstox_historical_data")
                    historical_data = self.upstox_historical_data(
                        ticker, start_date, end_date, interval
                    )
                    logger.info("upstox_historical_data method returned")

                    break
                except SourceError as e:
                    logger.error("Upstox SourceError : %s" % e)
                    print(crayons.red("Upstox source error: %s" % e, bold=True))

            # Source: NSE
            elif source == TickerStore.NSE:

                # Fetching data from NSE
                logger.info("Trying source NSE for fetching historical data")
                try:
                    logger.info("Calling nse_historical_data")
                    historical_data = self.nse_historical_data(
                        ticker, start_date, end_date, interval
                    )
                    logger.info("nse_historical_data method returned")

                    break
                except SourceError as e:
                    logger.error("NSE SourceError : %s" % e)
                    print(crayons.red("NSE source error: %s" % e, bold=True))

        if historical_data is None:
            logger.error("None of the source provided any data")
            # Returning back an empty data frame
            return None
            # raise TickerStoreError(
            #     "No data returned. No data source provided data for the requested time interval!"
            # )

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

        # Fetching upstox access token
        self.__upstox_get_access_token()

        # Fetching data depending on the interval specified
        data = None

        ##########################################
        # Credentails have been verfied
        # Creating upstox object to connect with
        # the API
        ##########################################
        try:
            logger.info("Creating Upstox object")
            u = Upstox(os.getenv("UPSTOX_API_KEY"), self.upstox_access_token)
            logger.info("Fetching the master contracts")
            u.get_master_contract("NSE_EQ")

            logger.info("Fetch all equity symbols")
            instrument = u.get_instrument_by_symbol("NSE_EQ", ticker)
            logger.info("All equity symbols fetched")

            # 1 minute interval
            if interval == TickerStore.INTERVAL_MINUTE_1:
                logger.info("fetching data for 1 minute interval")
                data = u.get_ohlc(
                    instrument, OHLCInterval.Minute_1, start_date, end_date
                )

            # 5 minute interval
            elif interval == TickerStore.INTERVAL_MINUTE_5:
                logger.info("fetching data for 5 minute interval")
                data = u.get_ohlc(
                    instrument, OHLCInterval.Minute_5, start_date, end_date
                )

            # 10 minute interval
            elif interval == TickerStore.INTERVAL_MINUTE_10:
                logger.info("fetching data for 10 minute interval")
                data = u.get_ohlc(
                    instrument, OHLCInterval.Minute_10, start_date, end_date
                )

            # 30 minute interval
            elif interval == TickerStore.INTERVAL_MINUTE_30:
                logger.info("fetching data for 30 minute interval")
                data = u.get_ohlc(
                    instrument, OHLCInterval.Minute_30, start_date, end_date
                )

            # 60 minute interval
            elif interval == TickerStore.INTERVAL_MINUTE_60:
                logger.info("fetching data for 60 minute interval")
                data = u.get_ohlc(
                    instrument, OHLCInterval.Minute_60, start_date, end_date
                )

            # 1 day interval
            elif interval == TickerStore.INTERVAL_DAY_1:
                logger.info("fetching data for 1 day interval")
                data = u.get_ohlc(instrument, OHLCInterval.Day_1, start_date, end_date)

            # 1 week interval
            elif interval == TickerStore.INTERVAL_WEEK_1:
                logger.info("fetching data for 1 week interval")
                data = u.get_ohlc(instrument, OHLCInterval.Week_1, start_date, end_date)

            # 1 month interval
            elif interval == TickerStore.INTERVAL_MONTH_1:
                logger.info("fetching data for 1 month interval")
                data = u.get_ohlc(
                    instrument, OHLCInterval.Month_1, start_date, end_date
                )

        except requests.HTTPError as e:
            logger.error(f"Exception occured (requests.HTTPError) : {e}")
            return None

        except requests.ConnectionError as e:
            logger.exception("Exception Occured! (requests.ConnectionError)")
            return None

        # Data formatting
        logger.info("Creating pandas dataframe")

        # If there was no data, return None
        if len(data) > 0:
            formatted_data = pandas.DataFrame(data)

            # setting dtypes for columns
            formatted_data.close = formatted_data.close.astype(float)
            formatted_data.high = formatted_data.high.astype(float)
            formatted_data.low = formatted_data.low.astype(float)
            formatted_data.open = formatted_data.open.astype(float)
            formatted_data.timestamp = formatted_data.timestamp.astype(int)
            formatted_data.volume = formatted_data.volume.astype(int)

            # Formatting dataframe for consumption
            logger.info("Formatting timestamp information in dataframe")
            formatted_data["timestamp"] = formatted_data["timestamp"] / 1000
            formatted_data["timestamp"] = formatted_data["timestamp"].apply(
                datetime.datetime.fromtimestamp
            )
            formatted_data = formatted_data.set_index("timestamp")
            formatted_data["Symbol"] = ticker

            logger.info("Renaming column name")
            formatted_data = formatted_data.rename(
                columns={
                    "close": "Close",
                    "high": "High",
                    "low": "Low",
                    "open": "Open",
                    "volume": "Volume",
                }
            )

            logger.info("returning formatted data frame")
            return formatted_data
        else:
            return None

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

    def __upstox_verify_credentails(self):
        """Verify the given Upstox credentials."""

        logger.info("Verifying API key and secret credentials")
        api_key = os.getenv("UPSTOX_API_KEY", "temp")
        redirect_uri = os.getenv("UPSTOX_REDIRECT_URI", "temp")
        api_secret = os.getenv("UPSTOX_API_SECRET", "temp")

        if (
            api_key is not "temp"
            or redirect_uri is not "temp"
            or api_secret is not "temp"
        ):
            logger.info("api_key, redirect_uri and api_secret are not temp")
            logger.info("creating an Upstox Session")
            try:
                s = Session(os.getenv("UPSTOX_API_KEY"))
                s.set_redirect_uri(os.getenv("UPSTOX_REDIRECT_URI"))
                s.set_api_secret(os.getenv("UPSTOX_API_SECRET"))
                url = s.get_login_url()

                req = requests.get(url)
                logger.debug(
                    f"Status code for the login url request is {req.status_code}"
                )

                if req.status_code != 200:
                    # Something, wrong with the API or credentials provided
                    info = req.json()
                    logger.debug(f"Unable to verify credentials. Error: {info}")
                    return  # Don't continue execution if there was an error

                # Upstox credentials are verified
                self.upstox_credentials_verified = True

            except ConnectionError:
                logger.exception(
                    "ConnectionError(HTTPSConnectionPool) error while creating upstox session object."
                )

        else:
            logger.error(
                "Unable to access values of UPSTOX_API_KEY, UPSTOX_API_SECRET or UPSTOX_REDIRECT_URI"
            )
            return

    def __upstox_get_access_token(self):
        """Fetch access token for given API creds"""

        logger.info("Getting Upstox access token")

        # Choose access_token_file_path or the __file__ for storing access_token on disk
        if self.access_token_file_path:
            package_folder_path = pathlib.Path(self.access_token_file_path)
        else:
            package_folder_path = pathlib.Path(__file__).parent

        access_token_file = package_folder_path / "access_token.file"

        logger.debug(f"Path for access_token file: {access_token_file}")

        # Access toke file exists
        if access_token_file.exists():
            logger.info("access_token.file already exists")

            # Open access token file
            with open(access_token_file, "r") as file:

                # Load and parse data from file
                logger.info("Opening access_token.file")
                data = json.load(file)
                access_token_time = datetime.datetime.fromtimestamp(data["time"])
                present_time = datetime.datetime.fromtimestamp(int(time.time()))

                # Content in file is old, re-fetch access token
                if math.fabs(access_token_time.day - present_time.day) > 0:

                    # Again fetch the access_token
                    logger.info(
                        "access_token.file contains stale credentials. Getting new credentials"
                    )
                    self.upstox_access_token = daemon.auth_upstox()
                    logger.debug(f"Access Token fetched")

                    # Writing new access token to file
                    with open(access_token_file, "w") as z:
                        logger.info("Writing new access token to file")
                        json.dump(
                            {
                                "access_token": self.upstox_access_token,
                                "time": int(time.time()),
                            },
                            z,
                        )

                # Contents of file is new
                else:
                    logger.info("Contents of access token file is usable")
                    self.upstox_access_token = data["access_token"]

        # No access token file found
        else:

            # No access token file found, authorizing user and creating access token file
            logger.info("access_token.file not found, fetching new access token")
            self.upstox_access_token = daemon.auth_upstox()
            logger.debug(f"access token fetched: {self.upstox_access_token}")

            # Writing the access token to file
            with open(access_token_file, "w") as file:
                logger.info("Writing the new access token to file")
                json.dump(
                    {
                        "access_token": self.upstox_access_token,
                        "time": int(time.time()),
                    },
                    file,
                )
