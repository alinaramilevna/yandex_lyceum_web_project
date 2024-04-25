import requests
from data.config import YANDEX_SEARCH_MAPS_APIKEY


# ----------------------------------------------------------------------------------------------------------------------

def check_phone_number(phone_number: str):
    phone_number = phone_number.replace(' ', '').replace('\n', '').replace('\t', '')
    if '--' in phone_number or phone_number[0] == '-' or phone_number[-1] == '-':
        return False
    phone_number = phone_number.replace('-', '')
    if phone_number.count('(') > 0:
        p1 = phone_number.find('(')
        p2 = phone_number.find(')')
        if phone_number.count('(') == 1 and phone_number.count(')') == 1 and p1 < p2:
            phone_number = phone_number.replace('(', '')
            phone_number = phone_number.replace(')', '')
        else:
            return False
    elif ')' in phone_number:
        return False
    if phone_number.startswith('8'):
        phone_number = '+7' + phone_number[1:]
    if phone_number.startswith('+7') and phone_number[1:].isdigit():
        pass
    else:
        return False
    if len(phone_number) != 12:
        return False

    return phone_number


# ----------------------------------------------------------------------------------------------------------------------

def search_toponym(toponym_to_find):
    '''Search toponym to get full address of organization in the future'''

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = YANDEX_SEARCH_MAPS_APIKEY
    search_params = {
        "apikey": api_key,
        "text": toponym_to_find,
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)

    if not response:
        return ""

    json_response = response.json()
    # print(json_response)
    organization = json_response["features"][0]
    return organization


def get_address(toponym):
    return toponym["properties"]["CompanyMetaData"]['address']


def search_object(object):
    toponym = search_toponym(object)
    # print(toponym)
    if toponym:
        return get_address(toponym)
    raise IndexError

# ----------------------------------------------------------------------------------------------------------------------
