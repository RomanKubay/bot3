import os
API_KEY = os.environ['API_KEY']
MONGODB_HOST = os.environ['MONGODB_HOST']
CLIENT_API_ID = os.environ['CLIENT_API_ID']
CLIENT_API_HASH = os.environ['CLIENT_API_HASH']
PHONE_NUMBER = os.environ['PHONE_NUMBER']

TG_ID = 1041234545
CHECK_DELAY = 3.5

regions = [
    'Вінницька обл.',        'Вознесенська ТГ',
    'Волинська обл.',        'Дніпропетровська обл.',
    'Донецька обл.',         'Житомирська обл.',
    'Закарпатська обл.',     'Запорізька обл.',
    'Івано-Франківська обл.','м. Київ',
    'Київська обл.',         'Кіровоградська обл.',
    'Луганська обл.',        'Львівська обл.',
    'Миколаївська обл.',     'Нікопольська ТГ',
    'Одеська обл.',          'Полтавська обл.',
    'Рівненська обл.',       'Сумська обл.',
    'Тернопільська обл.',    'Харківська обл.',
    'Херсонська обл.',       'Хмельницька обл.',
    'Черкаська обл.',        'Чернівецька обл.',
    'Чернігівська обл.',     'АР Крим']

regions_short = [
    'Вінницька',        'Вознесенськ',
    'Волинська',        'Дніпропетровська',
    'Донецька',         'Житомирська',
    'Закарпатська',     'Запорізька',
    'Івано',            'м. Київ',
    'Київська',         'Кіровоградська',
    'Луганська',        'Львівська',
    'Миколаївська',     'Нікополь',
    'Одеська',          'Полтавська',
    'Рівненська',       'Сумська',
    'Тернопільська',    'Харківська',
    'Херсонська',       'Хмельницька',
    'Черкаська',        'Чернівецька',
    'Чернігівська',     'Крим']
