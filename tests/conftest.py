import pytest
import testing.postgresql

from dbactor import DBActor, DBActorAll


@pytest.fixture(scope="module")
def overall_actor():
    with testing.postgresql.Postgresql() as postgresql:
        db_url = postgresql.url()
        actor = DBActorAll(url=db_url)
        # run the schema file
        actor.run_file("tests/structure.sql")
        yield actor


@pytest.fixture
def test_actor(overall_actor):
    with overall_actor.transaction() as actor:
        yield actor
        # rollback the test
        actor._conn.rollback()

