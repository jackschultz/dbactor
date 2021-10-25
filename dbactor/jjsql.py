from .db import DBActor


class DBJinjaSqlActor(DBActor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from jinjasql import JinjaSql
        except ImportError:
            raise ImportError(f'JinjaSql needs to be installed to use DBJinjaSqlActor.')

        self.j = JinjaSql()

    def call_all(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        qstr, bind_params = self.j.prepare_query(template, qparams)
        return self._call_db_all(qstr, qparams=bind_params)

    def call_all_dict(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        qstr, bind_params = self.j.prepare_query(template, qparams)
        return self._call_all_dict(qstr, qparams=bind_params)

    def call_one(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = self.j.prepare_query(template, qparams)
        return self._call_db_one(query, qparams=bind_params)

    def call_one_dict(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = self.j.prepare_query(template, qparams)
        return self._call_one_dict(query, qparams=bind_params)
