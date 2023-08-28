from urllib.parse import urlparse
import requests
from FlowerShop.settings import BITLY_TOKEN

API_URL = 'https://api-ssl.bitly.com/v4'


def is_bitlink(url, fragment=None):
    parsed_url = urlparse(url)
    url = f"{parsed_url.netloc}{parsed_url.path}"
    if fragment:
        url += f'#{fragment}'
    api_method_url = f'{API_URL}/bitlinks/{url}'
    headers = {
        'Authorization': f'Bearer {BITLY_TOKEN}'
    }

    response = requests.get(api_method_url, headers=headers)
    return response.ok


def shorten_link(url, fragment=None):
    if fragment:
        url += f'#{fragment}'
    api_method_url = f"{API_URL}/bitlinks"
    headers = {
        'Authorization': f'Bearer {BITLY_TOKEN}'
    }
    payload = {
        'long_url': url
    }

    try:
        response = requests.post(api_method_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['id']
    except requests.exceptions.HTTPError as err:
        return
    # id:   bit.ly/3nqqxey
    # link: https://bit.ly/3nqqxey


def count_clicks(bitlink, period='month'):
    parsed_bitlink = urlparse(bitlink)
    bitlink = f'{parsed_bitlink.netloc}{parsed_bitlink.path}'
    api_method_url = f"{API_URL}/bitlinks/{bitlink}/clicks/summary"
    headers = {
        'Authorization': f'Bearer {BITLY_TOKEN}'
    }
    payload = {
        'unit': period
    }

    response = requests.get(api_method_url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()['total_clicks']
