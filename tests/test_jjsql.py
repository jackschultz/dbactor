import testing.postgresql
import pytest

from dbactor import DBJinjaSqlActor


public_table_list_qstr = "SELECT * FROM information_schema.tables where table_schema='public';"

product_insert_qstr = '''
INSERT INTO "public"."products" ("name", "cost") VALUES
    ('mug', '4'),
    ('fork', '1'),
    ('spoon', '1'),
    ('knife', '1'),
    ('pan', '8')
'''
product_select_where_cost_qstr = "SELECT * from products where cost > {{ min_cost }}"


@pytest.fixture
def test_actor(overall_actor):
    with overall_actor.transaction() as actor:
        actor.create_or_update(product_insert_qstr)
        yield actor
        # rollback the test
        actor._conn.rollback()


def test_jj_qparams(test_actor):
    qparams = dict(min_cost=2)
    products = test_actor.call_all_dict(product_select_where_cost_qstr, qparams=qparams)
    assert all([type(product) == dict for product in products])
    assert len(products) == 2
