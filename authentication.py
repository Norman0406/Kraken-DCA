import json

from logger import create_logger

logger = create_logger("Authentication")


class Authentication:
    def __init__(self, json_file):
        logger.info(f"Reading authentication from {json_file}")

        with open(json_file) as file:
            data = json.load(file)
            self.api_key_public = data["kraken"]["apiKey"]
            self.api_key_private = data["kraken"]["privateKey"]
