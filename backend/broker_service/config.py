import mysql.connector
import os
from dotenv import load_dotenv
# pip install python-dotenv
from app import app
from flaskext.mysql import MySQL
load_dotenv()

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_ROOT_USERNAME')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_HOST')
mysql.init_app(app)