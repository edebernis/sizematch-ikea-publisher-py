#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from importlib import import_module
import json
import requests


class Item:
    def __init__(self, source, urls, lang):
        self.source = source
        self.urls = urls
        self.lang = lang


class ItemEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return {
                "source": obj.source,
                "urls": obj.urls,
                "lang": obj.lang
            }

        return json.JSONEncoder.default(self, obj)


class Scraper:
    @staticmethod
    def create(name, args):
        scraper_class = _load_scraper(name)
        if scraper_class is not None:
            return scraper_class(args)

    def _get_session(self, protocol, retries):
        session = requests.Session()

        if retries:
            retry_obj = Retry(total=retries,
                              read=retries,
                              connect=retries,
                              backoff_factor=0.3)
            session.mount('{}://'.format(protocol),
                          HTTPAdapter(max_retries=retry_obj))

        return session

    def do_request(self, method, url, timeout=3, retries=3):
        protocol = url.split(':', 1)[0]
        session = self._get_session(protocol, retries)
        try:
            return getattr(session, method.lower())(url, timeout=timeout)
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError):
            return None

    def scrape(self):
        raise NotImplementedError()

    def result(self):
        raise NotImplementedError()


def _load_scraper(name):
    return {
        'ikea': getattr(import_module('item_scrapers.scrapers.ikea'), 'IKEA'),
    }.get(name)