from .jjsql import DBJinjaSqlActor


class DBPandasActor(DBJinjaSqlActor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(f'Pandas needs to be installed to use DBPandasActor.')
        self.pd = pd

    def call_df(self, qstr, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = self.j.prepare_query(qstr, qparams)
        return self.pd.read_sql_query(query, self.conn, params=bind_params)
