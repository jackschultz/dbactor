from .db import DBActor
from .sqa import DBSqlAlchemyActor
from .jjsql import DBJinjaSqlActor
from .pdsqla import DBPandasActor


class DBActorAll(DBSqlAlchemyActor, DBPandasActor):
    pass


class DBActorAlcJJ(DBSqlAlchemyActor, DBJinjaSqlActor):
    pass
