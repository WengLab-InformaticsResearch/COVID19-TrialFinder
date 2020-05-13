# dquest-flask
dquest implementation using flask

### Install and deploy
###### Enviroment
1. python2.7
2. create env and dependency
```buildoutcfg
sudo pip install virtualenv 
sudo virtualenv venv
source venv/bin/activate 
pip install -r requirements.txt

```

###### Bug to fix before deploy
```buildoutcfg
Traceback (most recent call last):
  File "/Users/cl3720/Projects/dquest-flask/run.py", line 1, in <module>
    from app import app
  File "/Users/cl3720/Projects/dquest-flask/app/__init__.py", line 9, in <module>
    cache.init_app (app)
  File "/Users/cl3720/Projects/dquest-flask/env/lib/python2.7/site-packages/flask_cache/__init__.py", line 156, in init_app
    from .jinja2ext import CacheExtension, JINJA_CACHE_ATTR_NAME
  File "/Users/cl3720/Projects/dquest-flask/env/lib/python2.7/site-packages/flask_cache/jinja2ext.py", line 33, in <module>
    from flask.ext.cache import make_template_fragment_key
ImportError: No module named ext.cache
```
1. find jinja2ext.py
2. locate line 33 and change to 
```buildoutcfg
from flask_cache import make_template_fragment_key
```
###### Change configuration
```
# vi app/lib/config.py
CRITERIA_HOST = 'elixr.XXX'
CRITERIA_DATABASE = 'trial_knowledge_base'
CRITEIRA_USERNAME = 'XXX'
CRITERIA_PASSWORD = 'XXX'
CRITERIA_DRIVER = '{ODBC Driver 17 for SQL Server}' # make sure the driver is installed on the server
CRITERIA_PORT  = XXX

AACT_HOST = 'aact-db.ctti-clinicaltrials.org'
AACT_PORT = 5432
AACT_DATABASE = 'aact'
AACT_USERNAME = 'XXX'
AACT_PASSWORD = 'XXX'

CSRF_ENABLED = True
SECRET_KEY = 'XXX'
```
make sure the correct version of ODBC version is available on server
```buildoutcfg
odbcinst -j
``` 
###### Deploy in Ubuntu with Apache2
Install and Enable mod_wsgi
```buildoutcfg
sudo apt-get install libapache2-mod-wsgi python-dev
sudo a2enmod wsgi
cd /var/www 
git clone https://github.com/stormliucong/dquest-flask.git
```

Add the following lines of code to the file to configure the virtual host. Be sure to change the ServerName to your domain or cloud server's IP address:
```buildoutcfg
# sudo vi  /etc/apache2/sites-available/dquest-flask.conf
<VirtualHost *:80>
		ServerName mywebsite.com
		ServerAdmin admin@mywebsite.com
		WSGIScriptAlias /dquest /var/www/dquest-flask/app.wsgi
		<Directory /var/www/FlaskApp/FlaskApp/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
Enable the virtual host and restart apache2
```buildoutcfg
sudo a2ensite dquest-flask
sudo service apache2 restart 
```
browser the website
```buildoutcfg
http://mywebsite.com/dquest-flask
```
Change different algorithms for question ranking by selecting one of the following three.
1. question_info_entropy using information entropy to rank questions.
2. question using raw entity_text (without omop mapping) to rank questions.
3. question_cluster using frequency to rank questions.
```
import lib.question_info_entropy as qst
import lib.question as qst
import lib.question_cluster as qst
```

change log file path
```
# app/lib/log.py
hfile_info = logging.FileHandler("app/log/dquest-info.log")
hfile_error = logging.FileHandler("app/log/dquest-error.log")
```

check path
```
# app/view.py
@app.route('/')
def index ():
```
## Versioning
0.0.1

## New features under development
https://docs.google.com/document/d/1h4PVeiIdWwsHzuxIovAnBbqT4RD-xk59A3ZOaJHKng8/edit

## Publications
Uder revision
## Authors
Cong Liu, Chi Yuan, Alex Butler, Chunhua Weng
stormliucong@gmail.com



