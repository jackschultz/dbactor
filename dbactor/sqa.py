from .db import DBActor

from contextlib import contextmanager


class DBSqlAlchemyActor(DBActor):

    def __init__(self, *args, echo=False, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
        except ImportError:
            raise ImportError(f'SqlAlchemy needs to be installed to use DBSqlAlchemyActor.')
        self.engine = create_engine(self.db_url, isolation_level="AUTOCOMMIT", echo=echo)
        self.Session = sessionmaker(bind=self.engine)
        self.internal_session = self.Session()

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
    def session(self):
        with self._get_session() as given_session:
            return given_session

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
