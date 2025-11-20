---
title: "Documentation"
---

## Syntax

### Comments
```
# This is a comment
```

### Table Declaration
```
#! TableName
```

### Schema Definition
```
#@ column1:type1, column2:type2, ...
```

### Data Rows
Standard CSV format after schema declaration.

## Type System

### Integers
- `i8`, `i16`, `i32`, `i64` - signed integers (8 to 64 bit)
- `u8`, `u16`, `u32`, `u64` - unsigned integers
- `int` - alias for `i64`
- `uint` - alias for `u64`

### Floating Point
- `f32`, `f64` - IEEE 754 floats
- `float` - alias for `f64`
- `decimal(precision, scale)` - exact decimal (e.g., `decimal(10,2)`)

### Text
- `str` - UTF-8 string
- `text` - alias for `str`

### Boolean
- `bool` - `true` or `false`

### Temporal
- `date` - ISO 8601 date (YYYY-MM-DD)
- `time` - ISO 8601 time (HH:MM:SS)
- `datetime` - ISO 8601 datetime
- `timestamp` - Unix timestamp

### Special
- `enum(val1|val2|val3)` - enumerated values
- `ref(Table.column)` - foreign key reference
- `type[]` - array of type
- `type?` - nullable type

## Complete Example

```
# User accounts
#! User
#@ id:uint, name:str, email:str, created:date, role:enum(admin|user|guest), active:bool
1, Alice, alice@example.com, 2024-01-15, admin, true
2, Bob, bob@example.com, 2024-02-20, user, true
3, Charlie, charlie@example.com, 2024-03-10, guest, false

# Purchase orders  
#! Order
#@ id:uint, user_id:ref(User.id), total:decimal(10,2), status:enum(pending|paid|shipped|delivered)
101, 1, 99.99, delivered
102, 2, 149.50, pending
103, 1, 75.00, shipped
```

## Parsers

### Python
```bash
cd python/
pip install -r requirements.txt
python parser.py example.3tl --pretty
```

Uses Lark parser. Validates syntax. Outputs JSON.

### JavaScript
```bash
cd javascript/
npm install
node src/cli.js example.3tl --pretty
```

Uses Peggy PEG parser. ES modules. Node 16+.

### Clojure
```bash
cd clojure/
clojure -M -m three-tl.parser example.3tl
```

Uses Instaparse. Functional transformation.

### Go
```bash
cd go/
go run ./cmd/3tl-parser example.3tl --pretty
```

Uses Participle. Struct tags define grammar. Requires Go 1.21+.

## Evaluation Results

Tested with Claude 3 Haiku, 3.5 Haiku, and Opus across 23 samples.

### Model Performance
- Claude 3.5 Haiku: 95% (21/22)
- Claude 3 Opus: 95% (21/22)
- Claude 3 Haiku: 91% (20/22)

Both CSV and 3TL achieved 100% on comparable tasks. 3TL enables features CSV cannot express:
- Enum constraints: 100%
- Explicit foreign keys: 100%
- Precision specifications: 100% (3.5 Haiku, Opus)

### Token Overhead
Average tokens per sample:

| Rows | CSV | 3TL | Overhead |
|------|-----|-----|----------|
| 3 | 135 chars | 208 chars | +54% |
| 10 | 380 chars | 445 chars | +17% |
| 100 | 3,200 chars | 3,265 chars | +2% |
| 1000 | 32,000 chars | 32,065 chars | +0.2% |

Schema overhead is fixed. Cost becomes negligible with larger datasets.

Cost with Claude 3.5 Haiku (100 rows): +$0.00004 per request.

### Zero-Shot Understanding
100% accuracy (15/15 samples). LLMs understand 3TL without documentation. Format is self-explanatory because:
- `#` prefix common for metadata
- `:` for types (TypeScript, Python)
- `enum(...)` familiar from programming
- `ref(...)` familiar from databases

### CSV Failure Cases
75% accuracy (15/20 samples). Model correctly identified where CSV is ambiguous:

| CSV Problem | Recognition |
|-------------|-------------|
| Type ambiguity | 100% |
| Boolean inconsistency | 100% |
| Date format confusion | 100% |
| Enum validation missing | 100% |
| Array representation | 100% |
| Schema inference errors | 100% |
| Precision loss | 50% |
| Null vs empty | 50% |
| Foreign key unclear | 50% |

Partial recognition (50%) in cases where model inferred from context. This proves the point: CSV relies on inference, 3TL is explicit.

## When To Use

### Use 3TL
- Database schema communication with LLMs
- Type precision matters (financial, scientific)
- Multiple related tables
- Code generation from schemas
- Data validation required
- Explicit foreign keys needed

### Use CSV
- Simple tabular data
- Maximum tool compatibility
- Very small datasets (<10 rows)
- Types don't matter

## Design Principles

1. **Obvious syntax** - Uses familiar conventions
2. **Self-documenting** - Schema embedded in data
3. **No ambiguity** - Types explicit, not inferred
4. **Scales well** - Schema overhead amortizes
5. **LLM-friendly** - Follows patterns models know

## Limitations

- Not a database (no indexes, queries, transactions)
- Not a serialization format (use Protocol Buffers/Avro)
- Not for binary data (use base64 in strings)
- Parsers validate syntax only (not data integrity)
- Foreign keys not enforced (validation is application's job)

## License

Apache 2.0 - Explicit patent grant. Commerce-friendly.
