---
title: "3TL - Typed Talking To LLMs"
---

## What

CSV with types, foreign keys, and enums. Multiple tables in one file.

```
#! User
#@ id:uint, name:str, email:str, role:enum(admin|user), active:bool
1, Alice, alice@example.com, admin, true
2, Bob, bob@example.com, user, true

#! Order
#@ id:uint, user_id:ref(User.id), amount:decimal(10,2), status:enum(pending|shipped)
101, 1, 99.99, shipped
102, 2, 149.50, pending
```

Parse this without documentation. Types are clear. Foreign keys explicit. Enums defined.

## The Problem

CSV forces inference and creates ambiguity:

| Problem | CSV | 3TL |
|---------|-----|-----|
| Type confusion | Is "123" string or number? | `code:str` explicit |
| Boolean chaos | true, 1, yes all mean same? | Only `true`/`false` |
| Precision loss | Can't specify decimals | `decimal(10,2)` exact |
| Date ambiguity | 01/02/03 is which date? | ISO `2003-01-02` |
| No validation | Any enum value accepted | `enum(a\|b\|c)` enforced |
| Unclear refs | What does user_id reference? | `ref(User.id)` explicit |

3TL makes everything explicit. No guessing.

## Examples

### E-Commerce

```
#! Product
#@ id:uint, name:str, price:decimal(10,2), category:enum(Electronics|Books|Toys), in_stock:bool
1, Laptop, 999.99, Electronics, true
2, Python Book, 29.99, Books, true
3, Robot Toy, 49.99, Toys, false

#! Order
#@ id:uint, product_id:ref(Product.id), quantity:uint, status:enum(pending|paid|shipped|delivered)
101, 1, 1, shipped
102, 2, 3, pending
```

Foreign keys clear. Enum values defined. Decimal precision exact.

### Financial Data

```
#! Transaction
#@ id:uint, account:str, amount:decimal(15,2), fee:decimal(10,4), date:date, type:enum(debit|credit)
1, ACC-001, 1250.50, 2.5000, 2024-01-15, debit
2, ACC-002, 3499.99, 5.2500, 2024-01-16, credit
```

Precision matters for money. `decimal(15,2)` guarantees 2 decimal places. `decimal(10,4)` for fees.

### Multi-Table Relations

```
#! User
#@ id:uint, name:str, email:str, created:date, status:enum(active|inactive|banned)
1, Alice, alice@example.com, 2024-01-10, active
2, Bob, bob@example.com, 2024-02-15, active

#! Post
#@ id:uint, user_id:ref(User.id), title:str, content:text, published:bool
101, 1, First Post, Content here, true
102, 1, Second Post, More content, false
103, 2, Bob Post, Bob content, true

#! Comment
#@ id:uint, post_id:ref(Post.id), user_id:ref(User.id), text:str, created:datetime
1001, 101, 2, Great post!, 2024-01-11T10:30:00
1002, 101, 1, Thanks!, 2024-01-11T11:00:00
```

Three tables. Foreign keys explicit. Relationships clear.

## Parsers

Parse 3TL in 4 languages. All produce identical JSON output.

### Python

```bash
cd python/
pip install -r requirements.txt
python parser.py ../examples/products.3tl --pretty
```

**Output:**
```json
{
  "tables": [
    {
      "name": "Product",
      "columns": [
        {"name": "id", "type": "uint"},
        {"name": "name", "type": "str"},
        {"name": "price", "type": "decimal(10,2)"}
      ],
      "rows": [
        [1, "Laptop", 999.99],
        [2, "Book", 29.99]
      ]
    }
  ]
}
```

Uses Lark parser. Validates syntax. Type-safe.

### JavaScript

```bash
cd javascript/
npm install
node src/cli.js ../examples/products.3tl --pretty
```

**Library usage:**
```javascript
import { parseFile, toJSON } from './src/parser.js';

const doc = parseFile('../examples/products.3tl');
console.log(toJSON(doc, true));
```

Uses Peggy PEG parser. ES modules. Node 16+.

### Clojure

```bash
cd clojure/
clojure -M -m three-tl.parser ../examples/products.3tl
```

**Library usage:**
```clojure
(require '[three-tl.parser :as parser])

(def doc (parser/parse-file "../examples/products.3tl"))
(println (parser/to-json doc true))
```

Uses Instaparse. Functional transformation. Immutable data.

### Go

```bash
cd go/
go run ./cmd/3tl-parser ../examples/products.3tl --pretty
```

**Library usage:**
```go
import "github.com/jiriknesl/3tl/pkg/parser"

doc, err := parser.ParseFile("../examples/products.3tl")
if err != nil {
    log.Fatal(err)
}

json, _ := parser.ToJSON(doc, true)
fmt.Println(json)
```

Uses Participle. Struct tags define grammar. Go 1.21+.

## Results

Evaluated with Claude 3 Haiku, 3.5 Haiku, and Opus:

- **95% accuracy** (Claude 3.5 Haiku, Opus)
- **+2% tokens** at 100 rows (+$0.00004 per request)
- **100% zero-shot understanding** (no docs needed)
- **75% identified CSV ambiguities**

Token overhead decreases with data size:
- 3 rows: +54%
- 100 rows: +2%
- 1000 rows: +0.2%

Schema overhead is fixed. Amortizes over data.

## Quick Start

1. **Clone repository:**
   ```bash
   git clone https://github.com/Flexiana/3TL.git
   cd 3TL
   ```

2. **Try examples:**
   ```bash
   python python/parser.py examples/products.3tl --pretty
   node javascript/src/cli.js examples/blog.3tl --pretty
   clojure -M -m three-tl.parser examples/invoices.3tl
   go run go/cmd/3tl-parser/main.go examples/unicode.3tl --pretty
   ```

3. **Read docs:** See [Documentation](/docs/) for complete type system and syntax reference.

## When To Use

**Use 3TL when:**
- Communicating database schemas with LLMs
- Type precision matters (financial, scientific)
- Multiple related tables
- Code generation from schemas
- Need explicit foreign keys
- Data validation required

**Use CSV when:**
- Simple tabular data
- Maximum tool compatibility
- Very small datasets (<10 rows)
- Types don't matter

See [GitHub](https://github.com/Flexiana/3TL) for source code and evaluations.
