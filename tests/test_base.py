import testing.postgresql
import pytest

from dbactor import DBActor


@pytest.fixture()
def test_actor():
    with testing.postgresql.Postgresql() as postgresql:
        db_url = postgresql.url()
        yield DBActor(url=db_url)


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
product_count_qstr = "SELECT count(*) from products"
product_select_qstr = "SELECT * from products;"
product_select_where_cost_qstr = "SELECT * from products where cost > 2"


def test_create_table(test_actor):
    public_tables_before = test_actor.call_all(public_table_list_qstr)
    assert len(public_tables_before) == 0
    test_actor.create_or_update(create_products_str)
    public_tables_after = test_actor.call_all(public_table_list_qstr)
    assert len(public_tables_after) == 1


def test_insert(test_actor):
    test_actor.create_or_update(create_products_str)
    count_before = test_actor.call_one(product_count_qstr)
    assert count_before['count'] == 0
    test_actor.create_or_update(product_insert_qstr)
    count_after = test_actor.call_one(product_count_qstr)
    assert count_after['count'] == 5


def test_dicts(test_actor):
    test_actor.create_or_update(create_products_str)
    test_actor.create_or_update(product_insert_qstr)
    products = test_actor.call_all_dict(product_select_qstr)
    assert len(products) == 5
    assert type(products) == list
    assert all([type(product) == dict for product in products])
    products_where_cost = test_actor.call_all_dict(product_select_where_cost_qstr)
    assert len(products_where_cost) == 2
