from os import environ
from typing import Final


class Keys:
    TG_TOKEN: Final = environ.get('TG_TOKEN', '0987654321')
    TG_BOT_ID: Final = environ.get('TG_BOT_ID', '0987654321')
    VK_TOKEN: Final = environ.get('VK_TOKEN', '0987654321')
    VK_TOKEN_VERSION: Final = environ.get('VK_TOKEN_VERSION', '5.131')
    VK_BOT_ID: Final = environ.get('VK_BOT_ID', '217198885')


class DataBase:
    SETTINGS: Final = environ.get('SETTINGS', {'user': "ypec",
                                               'password': "0987654321",
                                               'host': "localhost",
                                               'port': 5432,
                                               'database': "ypec_bot"})


class Qiwi:
    NUMBER_PHONE: Final = environ.get('NUMBER_PHONE', '0987654321')
    TOKEN: Final = environ.get('TOKEN', '0987654321')


class Donate:
    TINKOFF: Final = environ.get('TINKOFF', "https://www.tinkoff.ru/cf/1zq1XGcQNXM")
    QIWI: Final = environ.get('QIWI', "https://qiwi.com/p/0987654321")
    SBERBANK: Final = environ.get('SBERBANK', "https://www.sberbank.ru/ru/person/dl/0987654321")
    YOOMONEY: Final = environ.get('YOOMONEY', "https://sobe.ru/na/B2W2x1U0o2L6")
    BOOSTY: Final = environ.get('BOOSTY', "https://boosty.to/ypec_bot")
    BITCOIN: Final = environ.get('BTC', "bc1qpzcvyg4v37yzz99rkgphdcqjfw8s05sgjcplvz")
    ETHERIUM: Final = environ.get('ETH', "0x5a9629d8974F9D36f362eFC09E184f231043Ff8a")


class Communicate:
    TG_BOT: Final = environ.get('TG_BOT', "https://t.me/ypec_bot")
    VK_BOT: Final = environ.get('VK_BOT', "https://vk.com/ypec_bot")
    DEVELOPER: Final = environ.get('DEVELOPER', "https://vk.com/id264311526")
    INSTAGRAM: Final = environ.get('INSTAGRAM', "https://www.instagram.com/your.oldfr1end")
    OFFICIAL_SITE: Final = environ.get('OFFICIAL_SITE', "https://www.ypec.ru/")
    OFFICIAL_VK_GROUP: Final = environ.get('OFFICIAL_VK_GROUP', "https://vk.com/ypecnews")

class GoogleDrive:
    SAMPLES: Final = environ.get('SAMPLES', "https://drive.google.com/drive/folders/1WI_PiaWfNFRwZLJvi2m18M5lACA4T9wp?usp=sharing")
