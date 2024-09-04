from functools import cached_property
from typing import Optional, Union, Dict, NoReturn
from urllib.parse import urljoin

import requests
from requests import Session
from retry import retry


class HttpClient:
    """
    Base class for connection to any web-resources. Uses HTTP requests.
    """

    def __init__(self,
                 base_url: str,
                 auth: Optional[tuple[str, str]] = None):
        self._url = base_url
        self._auth = auth

    @cached_property
    def session(self) -> Session:
        session = requests.session()
        session.headers.update({'Content-Type': 'application/json'})
        if self._auth:
            session.headers = {
                'Authorization': f'{self._auth[0]} {self._auth[1]}'
            }

        return session

    @retry(tries=3, exceptions=(requests.HTTPError, requests.ConnectionError), delay=5)
    def __request(self, method: str, uri: str, **kwargs) -> (
            Union)[Dict, NoReturn]:
        url = urljoin(self._url, uri)

        response = self.session.request(method, url, **kwargs)
        if not response.text:
            return None
        return response.json()

    def get(self, uri: str, **kwargs) -> Union[Optional[Dict], None]:
        return self.__request('GET', uri, **kwargs)

    def post(self, uri: str, **kwargs) -> Union[Optional[Dict], None]:
        return self.__request('POST', uri, **kwargs)

    def patch(self, uri: str, **kwargs) -> Union[Optional[Dict], None]:
        return self.__request('PATCH', uri, **kwargs)

    def close_session(self) -> None:
        self.session.close()
