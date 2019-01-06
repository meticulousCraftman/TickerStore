from . import tempserver as ts
import multiprocessing as mp
import webbrowser
import os


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
