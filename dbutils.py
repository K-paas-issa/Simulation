from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os

mysql_username = os.getenv('MYSQL_USERNAME')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_port = os.getenv('MYSQL_PORT')
dbname = 'bklocal'

DB_URL = f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{dbname}'

class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()
