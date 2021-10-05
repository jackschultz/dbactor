import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jinjasql import JinjaSql
import pandas as pd

from contextlib import contextmanager

j = JinjaSql()


class DBActor(object):

    def __init__(self, database=None, user=None, password=None, host=None, port=None, min_conns=1, max_conns=15,
                 echo=False):
        self.db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.tcp = ThreadedConnectionPool(min_conns, max_conns, self.db_url)

        self.engine = create_engine(self.db_url, isolation_level="AUTOCOMMIT", echo=echo)
        self.Session = sessionmaker(bind=self.engine)
        self.internal_session = self.Session()

    @contextmanager
    def _get_cursor(self):
        conn = self.tcp.getconn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cursor, conn
        except Exception as e:
            print(f'DB Actor Error: {e}')
            conn.rollback()
        finally:
            conn.commit()
            self.tcp.putconn(conn)

    @contextmanager
    def _get_session(self):
        try:
            yield self.internal_session
        except Exception as e:
            self.internal_session.rollback()
            raise e
        finally:
            self.internal_session.commit()

    @property
    def conn(self):
        """
        Having to deal with times when getting a conn and using that yourself is a little better
        """
        with self._get_cursor() as (_, conn):
            return conn

    @property
    def cursor(self):
        with self._get_cursor() as (cursor, _):
            return cursor

    @property
    def session(self):
        with self._get_session() as given_session:
            return given_session

    def _call_db_one(self, qstr, qparams):
        with self._get_cursor() as (cursor, _):
            cursor.execute(qstr, qparams)
            return cursor.fetchone()

    def _call_db_all(self, qstr, qparams):
        with self._get_cursor() as (cursor, _):
            cursor.execute(qstr, qparams)
            return cursor.fetchall()

    def _create_or_update_db(self, command, cparams):
        with self._get_cursor() as (cursor, conn):
            cursor.execute(command, cparams)
            return conn.commit()

    def call_custom_create_or_update(self, sql_fn, params):
        return self._create_or_update_db(sql_fn, params)

    def create_or_update(self, sql_fn, params):
        return self._create_or_update_db(sql_fn, params)

    def call_custom_all(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        return self._call_db_all(qstr, qparams)

    def call_custom_all_dict(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        res = self._call_db_all(qstr, qparams)
        return [dict(qr) for qr in res]

    def call_custom_all_template_dict(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = j.prepare_query(template, qparams)
        return self.call_custom_all_dict(query, bind_params)

    def call_custom_one(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        return self._call_db_one(qstr, qparams)

    def call_custom_one_dict(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        return dict(self.call_custom_one(qstr, qparams=qparams))

    def create_model(self, model, values: dict):
        """Logic for creating or updating using sqlalchemy model"""
        obj = model()
        return self.update_object(obj, values)

    def create_or_update_model(self, model, keys: dict, values: dict):
        """Logic for creating or updating using sqlalchemy model"""
        obj = self.session.query(model).filter_by(**keys).first()
        if not obj:
            obj = model(**keys)
        return self.update_object(obj, values)

    def update_object(self, obj, values: dict):
        for key, value in values.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        return obj

    def call_df(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = j.prepare_query(qstr, qparams)
        return pd.read_sql_query(query, self.conn, params=bind_params)
