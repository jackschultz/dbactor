import csv

import testing.postgresql
import pytest
from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(Integer)
    cost = Column(Float)


product_count_qstr = "SELECT count(*) from products"


@pytest.fixture
def test_actor(sqa_actor):
    with sqa_actor.transaction() as actor:
        yield actor
        # rollback the test
        actor._conn.rollback()


def test_create_and_insert(test_actor):
    count_before = test_actor.call_one(product_count_qstr)
    assert count_before['count'] == 0
    with open('tests/products.csv', 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            print(row)
            keys = dict(name=row['name'])
            values = dict(cost=row['cost'])
            test_actor.create_or_update_model(Product, keys=keys, values=values)
    count_after = test_actor.call_one(product_count_qstr)
    assert count_after['count'] == 4


