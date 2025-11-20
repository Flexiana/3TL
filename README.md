# 3TL (Typed Talking To LLMs)

CSV with types, foreign keys, and enums. Designed for LLM data exchange.

## What

3TL extends CSV with a schema declaration syntax. Types are explicit. Relationships are declared. Multiple tables fit in one file.

```
#! User
#@ id:uint, name:str, email:str, role:enum(admin|user|moderator), active:bool
1, Alice, alice@example.com, admin, true
2, Bob, bob@example.com, user, true

#! Order
#@ id:uint, user_id:ref(User.id), amount:decimal(10,2), status:enum(pending|shipped|delivered)
101, 1, 99.99, shipped
102, 2, 149.50, pending
```

Parse this without documentation. Types are clear. Foreign keys explicit. Enums defined.

## Why

CSV has problems:
- Types inferred (is "123" a string or number?)
- Booleans inconsistent (true/1/yes all valid)
- Precision lost (can't distinguish 0.05 from 0.050)
- Dates ambiguous (01/02/03 is which date?)
- No enum validation (any value accepted)
- Foreign keys unclear (what does user_id reference?)
- Arrays non-standard (comma-separated strings?)

3TL fixes these:
- Types declared: `uint`, `str`, `decimal(10,2)`, `bool`
- Booleans standard: `true`/`false` only
- Precision explicit: `decimal(10,2)` means exactly 2 decimals
- Dates ISO: `2003-01-02` unambiguous
- Enums validated: `enum(pending|shipped|delivered)`
- Foreign keys explicit: `ref(User.id)`
- Arrays typed: `str[]`

## Type System

### Integers
- `i8`, `i16`, `i32`, `i64` - signed integers (8 to 64 bit)
- `u8`, `u16`, `u32`, `u64` - unsigned integers
- `int` - alias for `i64`
- `uint` - alias for `u64`

### Floating Point
- `f32`, `f64` - IEEE 754 floats
- `float` - alias for `f64`
- `decimal(precision, scale)` - exact decimal (e.g., `decimal(10,2)` for currency)

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

### Complete Example
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

Available in 4 languages:

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

Uses Instaparse. Functional transformation. Immutable data structures.

### Go
```bash
cd go/
go run ./cmd/3tl-parser example.3tl --pretty
```

Uses Participle. Struct tags define grammar. Requires Go 1.21+.

All parsers produce identical JSON output.

## Evaluation Results

Tested with Claude 3 Haiku, 3.5 Haiku, and Opus across 23 samples.

### Accuracy
- Claude 3.5 Haiku: 95% (21/22)
- Claude 3 Opus: 95% (21/22)
- Claude 3 Haiku: 91% (20/22)

Both formats achieved 100% on comparable tasks. 3TL enables features CSV cannot express.

### Token Overhead
- 3 rows: +54% (+18 tokens for schema)
- 100 rows: +2% (schema overhead amortizes)
- 1000 rows: +0.2%

Cost with Claude 3.5 Haiku (100 rows): +$0.00004 per request.

### Zero-Shot Understanding
100% accuracy (15/15 samples). LLMs understand 3TL without documentation. Format is self-explanatory.

### CSV Failure Cases
75% accuracy (15/20 samples). Model correctly identified where CSV is ambiguous:
- Type ambiguity: 100%
- Boolean inconsistency: 100%
- Date format confusion: 100%
- Enum validation missing: 100%
- Array representation: 100%
- Schema inference errors: 100%

Partial recognition (50%) in cases where model was "too smart" and inferred from context. This proves the point: CSV relies on inference, 3TL is explicit.

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

## Specification

Full grammar and type system documented in `SPECIFICATION.md`.

Formal ABNF grammar in `3tl-grammar.abnf`.

## Examples

See `examples/` for:
- `products.3tl` - E-commerce with enums, nullable fields, refs
- `blog.3tl` - Multi-table with foreign keys
- `invoices.3tl` - Financial data with decimal types
- `unicode.3tl` - International text (Spanish, French, Japanese, Russian, Greek)

## Evaluations

See `evals/` for:
- `RESULTS.md` - Single model evaluation (Claude 3 Haiku)
- `MULTI_MODEL_RESULTS.md` - Cross-model comparison (3 Claude models)
- `ZERO_SHOT_RESULTS.md` - Understanding without documentation
- `CSV_FAILURE_RESULTS.md` - CSV ambiguity vs 3TL clarity

Run evals:
```bash
cd evals/
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add API keys
python run_evals.py --model claude-3-5-haiku --all-tasks
```

## Design Principles

1. **Obvious syntax** - Uses familiar conventions (# for metadata, : for types)
2. **Self-documenting** - Schema embedded in data
3. **No ambiguity** - Types explicit, not inferred
4. **Scales well** - Schema overhead fixed, amortizes over rows
5. **LLM-friendly** - Follows patterns models already know

## Limitations

- Not a database (no indexes, queries, transactions)
- Not a serialization format (use Protocol Buffers/Avro for that)
- Not for binary data (use base64 in string fields)
- Parsers validate syntax only (not data integrity)
- Foreign keys not enforced (reference validation is application's job)

## Status

Experimental. Grammar stable. Parsers functional. Evaluations demonstrate value.

Use for LLM communication. Don't use for systems requiring ACID guarantees.

## License

Apache 2.0
