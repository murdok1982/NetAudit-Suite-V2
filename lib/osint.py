import requests
from loguru import logger

class OSINTLookup:
    def __init__(self, shodan_api_key=None):
        self.shodan_api_key = shodan_api_key

    def check_shodan(self, ip):
        if not self.shodan_api_key:
            return None
            
        logger.info(f"Checking Shodan for IP: {ip}")
        try:
            url = f"https://api.shodan.io/shodan/host/{ip}?key={self.shodan_api_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Shodan lookup failed: {e}")
            return None

    def get_geoip(self, ip):
        # Using a free public API for demo purposes
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"GeoIP failed: {e}")
            return None
