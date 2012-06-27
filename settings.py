import os

APP_SECRET_KEY = "1Z|=IYyJu;WFCPHzoYN6^ ErI(*kyoa[<FIY1bV/M4E}WN$9,vcC)tT-:=8,0s8+"
APP_DEBUG_ENABLED = True
APP_PORT = 5000
APP_RELOADER_ENABLED = True

BCRYPT_WORK_FACTOR = 12

MONGODB_HOST = os.environ.get('MONGOHQ_URL') or "localhost"

ITEMS_PER_PAGE = 5

ADMIN_USERS = frozenset(['pmn', 'icey',])
