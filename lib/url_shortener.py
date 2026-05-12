# Written by Bohdan Shtepan <bohdan@shtepan.com>, February 2025

import threading
import hashlib
import base64
import itertools
import random
import string
import re
from abc import ABC, abstractmethod
from urllib.parse import urlparse


# Abstract base class for URL shortening strategies
class ShorteningStrategy(ABC):
    @abstractmethod
    def generate_short_url(self, long_url):
        pass


# Counter-based strategy
class CounterStrategy(ShorteningStrategy):
    def __init__(self):
        self.counter = itertools.count(1)
        self.lock = threading.Lock()

    def generate_short_url(self, long_url):
        with self.lock:
            return str(next(self.counter))


# Base64 encoding strategy
class Base64Strategy(ShorteningStrategy):
    def generate_short_url(self, long_url):
        return base64.urlsafe_b64encode(long_url.encode()).decode()[:8]


# MD5 hash strategy
class MD5Strategy(ShorteningStrategy):
    def generate_short_url(self, long_url):
        return hashlib.md5(long_url.encode()).hexdigest()[:8]


# Randomized strategy
class RandomStrategy(ShorteningStrategy):
    def generate_short_url(self, long_url):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# URL Shortener class
class URLShortener:
    def __init__(self, strategy: ShorteningStrategy):
        self.__lock = threading.Lock()
        self._url_to_shorturl_map = {}
        self._shorturl_to_url_map = {}
        self.strategy = strategy

    def encode_url(self, long_url) -> str:
        if not self._is_valid_url(long_url):
            raise ValueError("Invalid URL format")

        with self.__lock:
            if long_url in self._url_to_shorturl_map:
                return self._url_to_shorturl_map[long_url]
            short_url = self.strategy.generate_short_url(long_url)
            self._url_to_shorturl_map[long_url] = short_url
            self._shorturl_to_url_map[short_url] = long_url
            return short_url

    def decode_url(self, short_url) -> str:
        with self.__lock:
            return self._shorturl_to_url_map.get(short_url, None)

    def _is_valid_url(self, url) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

