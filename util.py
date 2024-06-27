import base64
import hashlib
import hmac
import json
import time
import urllib.request

API_ENDPOINT = "https://api.kraken.com"
USER_AGENT = "kraken_dca_agent"


class Authentication:
    def __init__(self, json_file):
        with open(json_file) as file:
            data = json.load(file)
            self.api_key_public = data["kraken"]["apiKey"]
            self.api_key_private = data["kraken"]["privateKey"]


class Settings:
    def __init__(self, json_file):
        with open(json_file) as file:
            self._data = json.load(file)
            self.trade_symbol = self._data["settings"]["tradeSymbol"]
            self.trade_interval = self._data["settings"]["tradeInterval"]
            self.dummy_mode = self._data["settings"]["dummyMode"]

    @property
    def data(self):
        return self._data


def make_api_call(authentication: Authentication, path: str, arguments: dict = {}):
    nonce = str(int(time.time() * 1000))
    params = f"nonce={nonce}"

    for key, value in arguments.items():
        params += f"&{key}={value}"

    api_sha256 = hashlib.sha256(nonce.encode("utf8") + params.encode("utf8"))
    api_hmac = hmac.new(
        base64.b64decode(authentication.api_key_private),
        path.encode("utf8") + api_sha256.digest(),
        hashlib.sha512,
    )
    api_signature = base64.b64encode(api_hmac.digest())

    try:
        api_request = urllib.request.Request(
            f"{API_ENDPOINT}{path}", params.encode("utf8")
        )
        api_request.add_header("API-Key", authentication.api_key_public)
        api_request.add_header("API-Sign", api_signature)
        api_request.add_header("User-Agent", USER_AGENT)
        api_response = urllib.request.urlopen(api_request).read().decode()
        api_data = json.loads(api_response)
    except Exception as error:
        print(f"Failed: {error}")
        raise error
    else:
        error = api_data["error"]

        if len(error) == 0:
            return api_data["result"]
        else:
            print(f"Error: {error}")
            raise Exception(error)
