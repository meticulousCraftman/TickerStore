from dotenv import load_dotenv, find_dotenv
from influxdb import InfluxDBClient
from upstox_api.api import *
from . import daemon as daemon
import datetime
import pathlib
import os
import time
import json

load_dotenv(find_dotenv())
client = InfluxDBClient(
    host=os.getenv("INFLUX_DB_HOST"), port=os.getenv("INFLUX_DB_PORT")
)

INTERVAL_TICK_BY_TICK = 1
INTERVAL_MINUTE_1 = 2
# INTERVAL_MINUTE_5 = 3
# INTERVAL_MINUTE_10 = 4
# INTERVAL_MINUTE_30 = 5
# INTERVAL_MINUTE_60 = 6
# INTERVAL_DAY = 7
# INTERVAL_WEEK = 8
# INTERVAL_MONTH = 9


def historical_data(ticker: str, _from_date: str, _to_date: str, interval: int) -> None:
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

    # Fetching data from Influx DB
    if {"name": os.getenv("INFLUX_DB_DATABASE")} in client.get_list_database():
        # Yes we have the database
        # Do further things here!
        # Check if required table exists
        # Select the timeframe and return data
        pass

    # Fetching the data from upstox
    else:
        package_folder_path = pathlib.Path(__file__).parent
        access_token_file = package_folder_path / "access_token.file"
        if access_token_file.exists():
            with open(access_token_file, "r") as file:
                data = json.load(file)
                access_token = data["access_token"]
                print("Found access_token.file (Contents)--->")
                print(data)
        else:
            access_token = daemon.auth_upstox()
            with open(access_token_file, "w") as file:
                json.dump(
                    {"access_token": access_token, "time": int(time.time())}, file
                )
        u = Upstox(os.getenv("UPSTOX_API_KEY"), access_token)
        u.get_master_contract("NSE_EQ")
        instrument = u.get_instrument_by_symbol("NSE_EQ", ticker)
        data = u.get_ohlc(instrument, OHLCInterval.Minute_1, from_date, to_date)
        return data
