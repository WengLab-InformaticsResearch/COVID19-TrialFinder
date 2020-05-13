from flask_cache import Cache
from log import slogger
import file as ufile
import sys

log = slogger ('dquest-ext')

cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DEFAULT_TIMEOUT': 86400, 'CACHE_THRESHOLD': 500, 'CACHE_DIR': 'app/resources/cache'})
