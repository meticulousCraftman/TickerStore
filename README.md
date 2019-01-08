
<p align="center"><img src="screenshots/tickerstore-logo.png"></p>



## Super simple to use

TickerStore is an easy to use python library used to get historical 
data of financial instruments from NSE.


## Install
```bash
$ pip install tickerstore
```

## Basic Usage

Using TickerStore you can specify the source from where the data needs
to be fetched. At present, there are 2 sources of data **Upstox** and 
**NSE**. EOD (End of Day) data can be used simple by using the following piece
of code. 

```python
from tickerstore.store import TickerStore
from datetime import date

fetcher = TickerStore()
fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```  

## How it works?
TickerStore tries to make historical stock market data more easy to
use in your python projects. TickerStore has multiple sources from
where the data is fetched. At present we have 2 sources, **NSE** and **Upstox**.
Data from these 2 sources are fetched in a predefined order. 

The default order is:
  1. Upstox
  2. NSE

If one fails, the next one is tried in order. You can change the order using a **set_fetch_order()** method.
To view the present fetch order use the **get_fetch_order()** method.


## Using with .env file (python-dotenv)

Create a **.env** file in the present working directory and enter your 
Upstox API key and API secret and leave all other fields as it is.

```dotenv
UPSTOX_API_KEY=<YOUR_UPSTOX_API_KEY>
UPSTOX_API_SECRET=<YOUR_UPSTOX_API_SECRET>
UPSTOX_REDIRECT_URI=http://127.0.0.1:5000/callback
TEMP_SERVER_SHUTDOWN_URL=http://127.0.0.1:5000/shutdown
TEMP_SERVER_AUTH_PAGE=http://127.0.0.1:5000/
```

On python end, use the **find_dotenv** function from the python-dotenv
package and pass it to the TickerStore. The information from the dotenv 
file will be available as environment variables.
```python
from tickerstore.store import TickerStore
from dotenv import find_dotenv
from datetime import date

fetcher = TickerStore(dotenv_path=find_dotenv())
fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```


## Using with Upstox
Using only with **Upstox**:

```python
from tickerstore.store import TickerStore
from datetime import date

fetcher = TickerStore(
    upstox_api_key="<YOUR_UPSTOX_API_KEY>",
    upstox_api_secret="<YOUR_UPSTOX_API_SECRET>",
    upstox_redirect_uri="http://localhost:5000/callback",
    temp_server_auth_page="http://localhost:8000/"
    )

fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```


## Change fetch order
Order in which the data is fetched from different sources can be changed.

```python
from tickerstore.store import TickerStore
from dotenv import find_dotenv
from datetime import date

fetcher = TickerStore(dotenv_path=find_dotenv())
fetcher.set_fetch_order([TickerStore.NSE, TickerStore.UPSTOX])

fetcher.historical_data("SBIN", date(2018,1,1), date(2018,1,30), TickerStore.INTERVAL_DAY_1)

```
TickerStore now first fetches data from NSE and then from UPSTOX. You can
even specify a single source and data will only be fetched from there.  

## API
Coming soon :)
