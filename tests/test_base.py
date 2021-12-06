import pytest


@pytest.fixture
def test_actor(overall_actor):
    with overall_actor.transaction() as actor:
        yield actor
        # rollback the test
        actor._conn.rollback()


public_table_list_qstr = "SELECT * FROM information_schema.tables where table_schema='public';"
product_insert_qstr = '''
INSERT INTO "public"."products" ("name", "cost") VALUES
    ('mug', '4'),
    ('fork', '1'),
    ('spoon', '1'),
    ('knife', '1'),
    ('pan', '8')
'''
product_count_qstr = "SELECT count(*) from products"
product_select_qstr = "SELECT * from products;"
product_select_where_cost_qstr = "SELECT * from products where cost > 2"

create_table_string = "CREATE TABLE buys (id int4, bought bool);"


def test_create_table(test_actor):
    """Tests ability to create a new table"""
    public_tables_before = len(test_actor.call_all(public_table_list_qstr))
    test_actor.create_or_update(create_table_string)
    public_tables_after = test_actor.call_all(public_table_list_qstr)
    assert len(public_tables_after) == public_tables_before + 1


def test_insert(test_actor):
    count_before = test_actor.call_one(product_count_qstr)
    assert count_before['count'] == 0
    test_actor.create_or_update(product_insert_qstr)
    count_after = test_actor.call_one(product_count_qstr)
    assert count_after['count'] == 5


def test_dicts(test_actor):
    count_before = test_actor.call_one(product_count_qstr)
    assert count_before['count'] == 0
    test_actor.create_or_update(product_insert_qstr)
    products = test_actor.call_all_dict(product_select_qstr)
    assert len(products) == 5
    assert type(products) == list
    assert all([type(product) == dict for product in products])
    products_where_cost = test_actor.call_all_dict(product_select_where_cost_qstr)
    assert len(products_where_cost) == 2

