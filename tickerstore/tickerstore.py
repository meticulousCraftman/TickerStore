from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

print(os.getenv('UPSTOX_API_KEY'))