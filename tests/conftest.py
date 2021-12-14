import pytest
import testing.postgresql

from dbactor import DBActor, DBActorAll, DBPandasActor, DBJinjaSqlActor, DBSqlAlchemyActor


@pytest.fixture(scope="session")
def db_url():
    with testing.postgresql.Postgresql() as postgresql:
        db_url = postgresql.url()
        actor = DBActorAll(url=db_url)
        actor.run_file("tests/structure.sql")
        yield db_url


@pytest.fixture
def all_actor(db_url):
    # run the schema file
    actor = DBActorAll(url=db_url)
    yield actor


@pytest.fixture
def base_actor(db_url):
    # run the schema file
    actor = DBActor(url=db_url)
    yield actor


@pytest.fixture
def pd_actor(db_url):
    # run the schema file
    actor = DBPandasActor(url=db_url)
    yield actor


@pytest.fixture
def jj_actor(db_url):
    # run the schema file
    actor = DBJinjaSqlActor(url=db_url)
    yield actor


@pytest.fixture
def sqa_actor(db_url):
    # run the schema file
    actor = DBSqlAlchemyActor(url=db_url)
    yield actor
