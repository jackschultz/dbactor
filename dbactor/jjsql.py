from .db import DBActor


class DBJinjaSqlActor(DBActor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from jinjasql import JinjaSql
        except ImportError:
            raise ImportError(f'JinjaSql needs to be installed to use DBJinjaSqlActor.')

        self.j = JinjaSql()

    def call_all_template_dict(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = self.j.prepare_query(template, qparams)
        return self.call_all_dict(query, bind_params)

    def call_one_template(self, template, qparams=None):
        if qparams is None:
            qparams = {}
        query, bind_params = self.j.prepare_query(template, qparams)
        return self.call_one(query, qparams=bind_params)
