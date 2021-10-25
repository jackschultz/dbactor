import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from contextlib import contextmanager


class DBActor(object):

    def __init__(self, url=None, database=None, user=None, password=None, host=None, port=None, min_conns=1, max_conns=15):
        if url:
            self.db_url = url
        else:
            self.db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.tcp = ThreadedConnectionPool(min_conns, max_conns, self.db_url)

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

    def call_create_or_update(self, sql_fn, params):
        return self._create_or_update_db(sql_fn, params)

    def create_or_update(self, sql_fn, qparams={}):
        if qparams is None:
            qparams = {}
        return self._create_or_update_db(sql_fn, qparams)

    def call_all(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        return self._call_db_all(qstr, qparams)

    def _call_all_dict(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        res = self._call_db_all(qstr, qparams)
        return [dict(qr) for qr in res]

    def call_all_dict(self, qstr, qparams=None):
        return self._call_all_dict(qstr, qparams=qparams)

    def call_one(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        return self._call_db_one(qstr, qparams)

    def _call_one_dict(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        return dict(self.call_one(qstr, qparams=qparams))

    def call_one_dict(self, qstr, qparams=None):
        return self._call_one_dict(qstr, qparams=qparams)
