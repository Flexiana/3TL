---
title: "Examples"
---

## E-Commerce Platform

Complete schema for products, orders, and users.

```
#! User
#@ id:uint, name:str, email:str, role:enum(admin|user|moderator), active:bool, created:date
1, Alice, alice@example.com, admin, true, 2024-01-10
2, Bob, bob@example.com, user, true, 2024-02-15
3, Charlie, charlie@example.com, user, false, 2024-03-20

#! Product
#@ id:uint, name:str, price:decimal(10,2), category:enum(Electronics|Books|Toys), in_stock:bool, tags:str[]
1, Laptop, 999.99, Electronics, true, [portable, computer, work]
2, Python Book, 29.99, Books, true, [programming, education]
3, Robot Toy, 49.99, Toys, false, [kids, educational]

#! Order
#@ id:uint, user_id:ref(User.id), product_id:ref(Product.id), quantity:uint, total:decimal(10,2), status:enum(pending|paid|shipped|delivered), ordered_at:datetime
101, 1, 1, 1, 999.99, delivered, 2024-01-15T10:30:00
102, 2, 2, 3, 89.97, pending, 2024-02-20T14:15:00
103, 1, 3, 2, 99.98, shipped, 2024-03-01T09:00:00
```

**Features demonstrated:**
- Foreign keys: `user_id:ref(User.id)`
- Enums: `status:enum(pending|paid|shipped|delivered)`
- Decimals: `price:decimal(10,2)`
- Arrays: `tags:str[]`
- Dates and timestamps: `created:date`, `ordered_at:datetime`
- Multiple related tables

## Financial Transactions

Bank transactions with precise decimal handling.

```
#! Account
#@ id:uint, number:str, holder:str, balance:decimal(15,2), currency:enum(USD|EUR|GBP), type:enum(checking|savings)
1, ACC-001, Alice Johnson, 15250.50, USD, checking
2, ACC-002, Bob Smith, 8499.99, EUR, savings

#! Transaction
#@ id:uint, account_id:ref(Account.id), amount:decimal(15,2), fee:decimal(10,4), net:decimal(15,2), type:enum(debit|credit|transfer), category:str?, date:date
1, 1, 1250.50, 2.5000, 1248.00, debit, rent, 2024-01-15
2, 1, 3500.00, 0.0000, 3500.00, credit, salary, 2024-01-20
3, 2, 500.00, 1.2500, 498.75, transfer, savings, 2024-01-22
```

**Features demonstrated:**
- Precise decimals: `decimal(15,2)` for amounts, `decimal(10,4)` for fees
- Nullable fields: `category:str?`
- Financial enums: Clear transaction types
- Foreign key references to accounts

## Blog Platform

Multi-table blog with users, posts, and comments.

```
#! User
#@ id:uint, username:str, email:str, bio:text?, joined:date, verified:bool
1, alice, alice@example.com, Tech writer and developer, 2023-01-10, true
2, bob, bob@example.com, , 2023-02-15, false
3, charlie, charlie@example.com, Love coding!, 2023-03-20, true

#! Post
#@ id:uint, author_id:ref(User.id), title:str, slug:str, content:text, published:bool, views:uint, created:datetime, updated:datetime?
1, 1, Getting Started with 3TL, getting-started-3tl, Full tutorial content here..., true, 1523, 2024-01-15T10:00:00, 2024-01-16T09:30:00
2, 1, Advanced Types, advanced-types, More content about types..., false, 0, 2024-02-01T14:00:00,
3, 3, My First Post, my-first-post, Charlie's content..., true, 45, 2024-03-05T11:00:00,

#! Comment
#@ id:uint, post_id:ref(Post.id), author_id:ref(User.id), text:text, approved:bool, created:datetime
1, 1, 2, Great tutorial! Very helpful., true, 2024-01-15T12:30:00
2, 1, 3, Thanks for sharing this!, true, 2024-01-15T15:45:00
3, 1, 2, When is the next part coming?, true, 2024-01-16T10:00:00
4, 3, 1, Welcome to blogging!, true, 2024-03-05T11:30:00

#! Tag
#@ id:uint, name:str, slug:str
1, Tutorial, tutorial
2, Programming, programming
3, Beginner, beginner

#! PostTag
#@ post_id:ref(Post.id), tag_id:ref(Tag.id)
1, 1
1, 2
1, 3
3, 3
```

**Features demonstrated:**
- Multiple foreign keys per table
- Nullable text: `bio:text?`, `updated:datetime?`
- Junction tables: `PostTag` links posts and tags
- Text vs string: `text` for long content, `str` for short fields

## Scientific Data

Experiment results with precise measurements.

```
#! Experiment
#@ id:uint, name:str, scientist:str, started:datetime, completed:datetime?, status:enum(running|completed|failed)
1, Protein Analysis A, Dr. Smith, 2024-01-10T08:00:00, 2024-01-15T17:30:00, completed
2, RNA Sequencing B, Dr. Jones, 2024-01-20T09:00:00, , running

#! Measurement
#@ id:uint, experiment_id:ref(Experiment.id), sample:str, value:decimal(20,10), unit:str, temperature:decimal(5,2), timestamp:datetime
1, 1, SAMPLE-001, 0.0000125678, mg/ml, 23.45, 2024-01-10T10:15:30
2, 1, SAMPLE-001, 0.0000126123, mg/ml, 23.47, 2024-01-10T11:15:30
3, 1, SAMPLE-002, 0.0000089456, mg/ml, 23.46, 2024-01-10T10:15:30
4, 2, SAMPLE-003, 0.0000234567, mg/ml, 22.98, 2024-01-20T10:00:00
```

**Features demonstrated:**
- High precision: `decimal(20,10)` for scientific measurements
- Temperature precision: `decimal(5,2)`
- Nullable completion: `completed:datetime?`
- Status tracking with enums

## Internationalization

Unicode support in table and field names.

```
#! Café
#@ id:uint, nombre:str, correo:str, país:str, activo:bool
1, José García, jose@example.com, España, true
2, François Dubois, francois@example.com, France, true
3, 田中太郎, tanaka@example.jp, 日本, true
4, Владимир Иванов, vladimir@example.ru, Россия, false

#! Заказ
#@ id:uint, café_id:ref(Café.id), товар:str, цена:decimal(10,2)
1, 1, Café con leche, 3.50
2, 2, Café au lait, 4.20
3, 3, カフェラテ, 450.00
```

**Features demonstrated:**
- Unicode table names: `Café`, `Заказ`
- Unicode column names: `nombre`, `país`, `товар`, `цена`
- Unicode data: Spanish, French, Japanese, Russian text
- International characters in refs: `café_id:ref(Café.id)`

## IoT Sensor Data

Time-series data from sensors.

```
#! Sensor
#@ id:uint, device_id:str, location:str, type:enum(temperature|humidity|pressure), unit:str, calibrated:date
1, TEMP-001, Room A, temperature, celsius, 2024-01-01
2, HUM-001, Room A, humidity, percent, 2024-01-01
3, PRES-001, Room B, pressure, hPa, 2024-01-01

#! Reading
#@ id:uint, sensor_id:ref(Sensor.id), value:decimal(10,4), quality:enum(good|fair|poor), timestamp:timestamp
1, 1, 22.3456, good, 1705320000
2, 1, 22.4123, good, 1705320060
3, 2, 65.2345, good, 1705320000
4, 2, 65.1876, fair, 1705320060
5, 3, 1013.2500, good, 1705320000
```

**Features demonstrated:**
- Timestamps: `timestamp:timestamp` (Unix timestamps)
- Precise readings: `decimal(10,4)`
- Device categorization with enums
- Time-series data pattern

## Try These Examples

All examples available in `examples/` directory:

```bash
# Python
python python/parser.py examples/products.3tl --pretty
python python/parser.py examples/blog.3tl --pretty
python python/parser.py examples/invoices.3tl --pretty
python python/parser.py examples/unicode.3tl --pretty

# JavaScript
node javascript/src/cli.js examples/products.3tl --pretty
node javascript/src/cli.js examples/blog.3tl --pretty

# Clojure
clojure -M -m three-tl.parser examples/products.3tl
clojure -M -m three-tl.parser examples/blog.3tl

# Go
go run go/cmd/3tl-parser/main.go examples/products.3tl --pretty
go run go/cmd/3tl-parser/main.go examples/blog.3tl --pretty
```

All parsers produce identical JSON output.
