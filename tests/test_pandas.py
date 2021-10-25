import testing.postgresql
import pytest
import pandas as pd

from dbactor import DBPandasActor


create_products_str = 'CREATE TABLE products(id int4, name varchar(256), cost int4)'
public_table_list_qstr = "SELECT * FROM information_schema.tables where table_schema='public';"
product_insert_qstr  = '''
INSERT INTO "public"."products" ("id", "name", "cost") VALUES
    ('1', 'mug', '4'),
    ('2', 'fork', '1'),
    ('3', 'spoon', '1'),
    ('4', 'knife', '1'),
    ('5', 'pan', '8')
'''
product_select_where_cost_qstr = "SELECT * from products where cost > {{ min_cost }}"


@pytest.fixture()
def test_actor():
    with testing.postgresql.Postgresql() as postgresql:
        db_url = postgresql.url()
        actor = DBPandasActor(url=db_url)
        actor.create_or_update(create_products_str)
        actor.create_or_update(product_insert_qstr)
        yield actor


def test_pd_qparams(test_actor):
    qparams = dict(min_cost=2)
    products = test_actor.call_df(product_select_where_cost_qstr, qparams=qparams)
    assert type(products) == pd.DataFrame
    assert len(products) == 2
