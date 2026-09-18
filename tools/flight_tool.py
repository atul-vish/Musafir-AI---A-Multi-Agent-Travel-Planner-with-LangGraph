import os
import re
import certifi
import airportsdata
import pycountry
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Default origin when user says only destination. e.g -> "Japan trip"
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "DEL")
