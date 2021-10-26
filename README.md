# DBActor

Simple class that interacts with Postgres to avoid ORM specifics.

### Instillation

DBActor supports multiple types of integrations. In many cases, you're looking to use it for a specific purpose. Sepcific extras installations allows for this.

Examples of what the different extras allows you to do are below.

```bash
$ pip install dbactor
$ pip install dbactor['jinjasql']
$ pip install dbactor['sqlalchemy']
$ pip install dbactor['pandas']
$ pip install dbactor['all']
```

### Initialize

Preference for DBActor location is in `db/__init__.py`.

```python
import os
from dbactor import DBActor

db_name = os.environ.get('DB_NAME', 'dbname')
db_user = os.environ.get('DB_USER', 'dbuser')
db_password = os.environ.get('DB_PASSWORD', 'dbpassword')
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432')

actor = DBActor(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)

# Or initialize with the url
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

actor = DBActor(url=db_url)
```

Then, to use in any file import with,

```python
from db import actor
```

## Examples

In examples below, the following table.

**Product**

`__tablename__ == products`

| column_name | data_type |
| ----------- | --------- |
| id          | int4      |
| name        | varchar   |
| cost        | numeric

Statements for initial creation without using DBActor.

```sql
-- products.sql
-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS products_id_seq;

-- Table Definition
CREATE TABLE "public"."products" (
    "id" int4 NOT NULL DEFAULT nextval('products_id_seq'::regclass),
    "name" varchar,
    "cost" numeric,
    PRIMARY KEY ("id")
);

INSERT INTO "public"."products" ("id", "name", "cost") VALUES
('1', 'mug', '4'),
('2', 'fork', '1'),
('3', 'spoon', '1'),
('4', 'knife', '1'),
('5', 'pan', '8');
```

## Actions

```python
from db import actor

qstr = 'select count(*) from products'
res = actor.call_one(qstr)
print(res)
# RealDictRow([('count', 5)])

qstr = 'select * from products;'

# If wanting RealDict
res = actor.call_all(qstr)
print(res)
# [RealDictRow([('id', 1), ('name', 'mug'), ('cost', Decimal('4'))]), RealDictRow([('id', 2), ('name', 'fork'), ('cost', Decimal('1'))]), RealDictRow([('id', 3), ('name', 'spoon'), ('cost', Decimal('1'))]), RealDictRow([('id', 4), ('name', 'knife'), ('cost', Decimal('1'))]), RealDictRow([('id', 5), ('name', 'pan'), ('cost', Decimal('8'))])]

# If wanting python dict rather than RealDict:
res = actor.call_all_dict(qstr)
print(res)
# [{'id': 1, 'name': 'mug', 'cost': Decimal('4')}, {'id': 2, 'name': 'fork', 'cost': Decimal('1')}, {'id': 3, 'name': 'spoon', 'cost': Decimal('1')}, {'id': 4, 'name': 'knife', 'cost': Decimal('1')}, {'id': 5, 'name': 'pan', 'cost': Decimal('8')}]
```

## JinjaSql

In cases where you may or may not have paramaters, JinjaSql is a great way to design queries, and DBActor allows for those in all cases.

```python
from dbactor import DBJinjaSqlActor
from db import db_url

actor = DBJinjaSqlActor(url=db_url)

qstr = '''
    SELECT
        *
    FROM
        products
    WHERE
        1 = 1
        {% if min_cost %}
        AND asdf >= min_cost
        {% endif %}
        {% if max_cost %}
        AND asdf <= max_cost
        {% endif %}
    ;
'''

qparams = dict(min_cost=3, max_cost=4)
res = actor.call_all_dict(qstr, qparams=qparams)
print(res)
# [{'id': 1, 'name': 'mug', 'cost': Decimal('4')}]
```


## SqlAlchemy

DBActor is made to avoid using ORMs for the most part. However, when inserting or updating rows, ORMs prove to be simpler. with `DBSqlalchemyActor`, you can either create or update with sql strings alone, or also with SQLAlchemy models.


```python
# db/models.py
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(Integer)
    price = Column(Float)
```

A perfect use case for this might be importing csvs.

Imagine a case where every day, someone creates a new csv with updated prices for the Things. In this case, there might be a daily job of looping through the csv and wanting to create or update an object for each row.

products.csv
```csv
name,price
mug, 10
cup, 5
plate, 3
bowl, 6
```

```python
import csv
from dbactor import DBSqlAlchemyActor
from db import db_url
from db.models import Product

actor = DBSqlAlchemyActor(url=db_url)

with open('products.csv', 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        keys = dict(name=row['name'])
        values = dict(price=row['price'])
        actor.create_or_update_model(Product, keys=keys, values=values)
        
qstr = 'select * from products'
res = actor.call_all_dict(qstr)
print(res)
# [{'id': 2, 'name': 'fork', 'cost': Decimal('1')}, {'id': 3, 'name': 'spoon', 'cost': Decimal('1')}, {'id': 4, 'name': 'knife', 'cost': Decimal('1')}, {'id': 5, 'name': 'pan', 'cost': Decimal('8')}, {'id': 1, 'name': 'mug', 'cost': Decimal('10')}, {'id': 6, 'name': 'cup', 'cost': Decimal('5')}, {'id': 7, 'name': 'plate', 'cost': Decimal('3')}, {'id': 8, 'name': 'bowl', 'cost': Decimal('6')}]

qstr = 'select count(*) from products'
res = actor.call_one(qstr)
print(res)
# RealDictRow([('count', 8)])
```

### Pandas

When using `DBPandasActor`, you'll have the ability to `call_df` using the same connection. This is done with JinjaSQL templates.

```python
from dbactor import DBPandasActor
from db import db_url

actor = DBPandasActor(url=db_url)

qstr = '''
select * from products where cost > {{min_cost}};
'''
qparams = dict(min_cost=4)

df = actor.call_df(qstr, qparams=qparams)
print(type(df))
# <class 'pandas.core.frame.DataFrame'>
print(df)
#    id   name  cost
# 0   2   fork   1.0
# 1   3  spoon   1.0
# 2   4  knife   1.0
# 3   5    pan   8.0
# 4   1    mug  10.0
# 5   6    cup   5.0
# 6   7  plate   3.0
# 7   8   bowl   6.0

```