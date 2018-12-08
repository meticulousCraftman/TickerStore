from upstox_api.api import *
from . import tempserver as ts
import multiprocessing as mp
import webbrowser
import os
import datetime
import schedule
import time

SUBSCRIBED_INSTRUMENTS = ["RELIANCE", "ONGC", "SAIL", "IOC"]


def auth_upstox() -> str:
    """Helps in authorizing Upstox user and returns the access_token.

    Returns
    -------
    str
        Returns the access token for the verified individual.

    """

    def start_server(queue):
        ts.app.queue = queue
        ts.app.run()

    queue = mp.Queue()
    p = mp.Process(target=start_server, args=(queue,))
    print("Starting process. Opening Authentication page...")
    webbrowser.open_new(os.getenv("TEMP_SERVER_AUTH_PAGE"))
    p.start()
    p.join()
    access_token = queue.get()
    print(f"Access Token : {access_token}")
    return access_token


def fetch_1minute(upstox):
    from_date = datetime.datetime.strptime("01/07/2017", "%d/%m/%Y").date()
    to_date = datetime.datetime.strptime("07/07/2017", "%d/%m/%Y").date()
    interval = OHLCInterval.Minute_1
    for ticker in SUBSCRIBED_INSTRUMENTS:
        instrument = upstox.get_instrument_by_symbol("NSE_EQ", ticker)
        data = upstox.get_ohlc(instrument, interval, from_date, to_date)
        if len(data) == 0:
            # No data for this day!
            pass
        else:
            # We have some data, let's store it in Influx DB
            pass


if __name__ == "__main__":
    access_token = auth_upstox()
    u = Upstox(os.getenv("UPSTOX_API_KEY"), access_token)
    u.get_master_contract("NSE_EQ")
    # fetch_1minute(u)
