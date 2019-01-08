
<p align="center"><img src="screenshots/tickerstore-logo.png"></p>



## Super simple to use

Ticker Store is designed to be the simplest way possible to get historical data for financial instruments. It has multiple sources for fetching hsitorical data and a standard output for using the data.


## Install
```bash
$ pip install tickerstore
```

## Basic Usage

Using TickerStore you can specify the source from where the data needs
to be fetched. At present, there are 2 sources of data **Upstox** and 
**NSE**.

EOD (End of Day) data can be used simple by using the following piece
of code. 

```python
from tickerstore.store import TickerStore
from datetime import date

fetcher = TickerStore()
fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```

The default order in which the data is fetched:
  1. Upstox
  2. NSE  

If one fails, the next one is tried in order.  

Using with **python-dotenv**:

```dotenv
UPSTOX_API_KEY=<YOUR_UPSTOX_API_KEY>
UPSTOX_API_SECRET=<YOUR_UPSTOX_API_SECRET>
UPSTOX_REDIRECT_URI=http://127.0.0.1:5000/callback
TEMP_SERVER_SHUTDOWN_URL=http://127.0.0.1:5000/shutdown
TEMP_SERVER_AUTH_PAGE=http://127.0.0.1:5000/
```

```python
from tickerstore.store import TickerStore
from dotenv import find_dotenv
from datetime import date

fetcher = TickerStore(dotenv=find_dotenv())
fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```

Using only with **Upstox**:

```python
from tickerstore.store import TickerStore
from datetime import date

fetcher = TickerStore(
    upstox_api_key="<YOUR_UPSTOX_API_KEY>",
    upstox_api_secret="<YOUR_UPSTOX_API_SECRET>",
    upstox_redirect_uri="http://localhost:5000/callback",
    )

fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```

## API
Coming soon :)
