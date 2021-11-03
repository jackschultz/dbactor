from .db import DBActor

from contextlib import contextmanager


class DBSqlAlchemyActor(DBActor):

    def __init__(self, *args, echo=False, expire_on_commit=False, pool_pre_ping=False, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
        except ImportError:
            raise ImportError(f'SqlAlchemy needs to be installed to use DBSqlAlchemyActor.')
        self.engine = create_engine(self.db_url,
                                    creator=self.tcp.getconn,
                                    isolation_level="AUTOCOMMIT",
                                    echo=echo,
                                    pool_pre_ping=pool_pre_ping)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=expire_on_commit)

    @contextmanager
    def _get_session(self):
        try:
            session = self.Session()
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.commit()

    def get_session(self):
        with self._get_session() as given_session:
            return given_session

    def create_model(self, model, values: dict):
        """Logic for creating or updating using sqlalchemy model"""
        obj = model()
        return self.update_object(obj, values)

    def create_or_update_model(self, model, keys: dict, values: dict):
        """Logic for creating or updating using sqlalchemy model"""
        session = self.get_session()
        obj = session.query(model).filter_by(**keys).first()
        if not obj:
            obj = model(**keys)
        return self.update_object(obj, values, session=session)

    def update_object(self, obj, values: dict, session=None):
        if not session:
            session = self.get_session()
        for key, value in values.items():
            setattr(obj, key, value)
        session.add(obj)
        session.commit()
        return obj
