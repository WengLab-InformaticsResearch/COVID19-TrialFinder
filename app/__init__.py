from flask import Flask
from lib.extensions import cache
from DBUtils.PooledDB import PooledDB
import pyodbc
import psycopg2

app = Flask(__name__)

# cache.init_app (app)

app.config.from_object('app.lib.config')

# pool for knowledgebase
general_pool_criteria = PooledDB(creator=pyodbc,
# general_pool_criteria = PooledDB(creator=psycopg2,
                                 host=app.config.get('CRITERIA_HOST'),
                                 port=app.config.get('CRITERIA_PORT'),
                                 database=app.config.get('CRITERIA_DATABASE'),
                                 user=app.config.get('CRITERIA_USERNAME'),
                                 password=app.config.get('CRITERIA_PASSWORD'),
                                 driver=app.config.get('CRITERIA_DRIVER'),
                                 maxconnections=12,
                                 blocking=False)

# pool for nct details in AACT
general_pool_aact = PooledDB(creator=psycopg2,
                             host=app.config.get('AACT_HOST'),
                             port=app.config.get('AACT_PORT'),
                             database=app.config.get('AACT_DATABASE'),
                             user=app.config.get('AACT_USERNAME'),
                             password=app.config.get('AACT_PASSWORD'),
                             maxconnections=12,
                             blocking=False)

from app import views
