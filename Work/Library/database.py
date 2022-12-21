import sqlalchemy
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean
from datetime import datetime, timedelta
import pymysql
from Scripts.config import username, password, host, database


class Database:
    metadata = MetaData()

    news = Table('news', metadata, 
        Column('id', Integer(), primary_key=True),
        Column('title', String(300), nullable=False),
        Column('url', String(200),  nullable=False),
        Column('type', String(200), nullable=True),
        Column('published', DateTime(), nullable=False)
    )

    def __init__(self):
        self.engine = sqlalchemy.create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database}")
        self.conn = self.engine.connect()
        self.metadata.create_all(self.engine)

    def add_record(self, _id, title, url, _type, published):
        try:
            ins = self.news.insert().values(
                id = _id,
                title = title,
                url = url,
                type = _type,
                published = published
            )

            r = self.conn.execute(ins)
        except sqlalchemy.exc.IntegrityError:
            pass

    def get_all(self):
        s = self.news.select()
        r = self.conn.execute(s)
        return r.fetchall()

    def get_interval(self, date, length):
        date = [int(i) for i in date.split('.')]
        date_start = datetime(day=date[0], month=date[1], year=date[2])
        date_end = date_start + timedelta(days=length)
        s = sqlalchemy.select([self.news]).where(
            self.news.c.published >= date_start,
            self.news.c.published < date_end
        )
        r = self.conn.execute(s)
        return r.fetchall()
