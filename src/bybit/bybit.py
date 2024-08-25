import json
import logging


class Bybit:
    def __init__(self, api_key, secret_key, endpoints):
        self.api_key = api_key
        self.secret_key = secret_key
        self.endpoints = endpoints

    async def connect(self):
        ...
