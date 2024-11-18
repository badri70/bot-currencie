import requests
from dotenv import load_dotenv
import os


API_URL = "https://openexchangerates.org/api/latest.json"
load_dotenv()


def get_exchange_rate():
    params = {
        "app_id": os.getenv('API_KEY')
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    return data['rates']