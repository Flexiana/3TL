---
title: "Parsers"
---

Four implementations. Identical JSON output. Pick your language.

## Python

Uses Lark parser with Earley algorithm. Type-safe transformation with dataclasses.

### Installation

```bash
cd python/
pip install -r requirements.txt
```

Dependencies: `lark>=1.1.0`

### Command Line

```bash
python parser.py input.3tl              # Compact JSON
python parser.py input.3tl --pretty     # Pretty-printed
python validator.py input.3tl           # Validate only
```

### Library Usage

```python
from parser import parse_file, parse_string, to_json

# Parse file
doc = parse_file('data.3tl')

# Parse string
doc = parse_string('''
#! User
#@ id:uint, name:str
1, Alice
''')

# Access data
for table in doc.tables:
    print(f"Table: {table.name}")
    for col in table.columns:
        print(f"  {col.name}: {col.type.base_type}")
    for row in table.rows:
        print(f"  Row: {row}")

# Convert to JSON
json_str = to_json(doc, pretty=True)
```

### Data Structures

```python
@dataclass
class TypeInfo:
    base_type: str
    is_array: bool = False
    is_nullable: bool = False
    params: Optional[dict[str, Any]] = None

@dataclass
class Column:
    name: str
    type: TypeInfo

@dataclass
class Table:
    name: str
    columns: list[Column]
    rows: list[list[Any]]

@dataclass
class Document:
    tables: list[Table]
```

### Testing

```bash
python -m pytest test_parser.py
```

12 tests. All passing.

---

## JavaScript

Uses Peggy PEG parser. ES modules. Node 16+.

### Installation

```bash
cd javascript/
npm install
```

Dependencies: `peggy ^4.0.3`

### Command Line

```bash
node src/cli.js input.3tl              # Compact JSON
node src/cli.js input.3tl --pretty     # Pretty-printed
```

### Library Usage

```javascript
import { parseFile, parseString, toJSON } from './src/parser.js';

// Parse file
const doc = parseFile('../examples/products.3tl');

// Parse string
const doc = parseString(`
#! User
#@ id:uint, name:str
1, Alice
`);

// Access data
for (const table of doc.tables) {
  console.log(`Table: ${table.name}`);
  for (const col of table.columns) {
    console.log(`  ${col.name}: ${col.type}`);
  }
  for (const row of table.rows) {
    console.log(`  Row: ${row}`);
  }
}

// Convert to JSON
const json = toJSON(doc, true);
console.log(json);
```

### Data Structures

```javascript
{
  tables: [
    {
      name: 'User',
      columns: [
        { name: 'id', type: 'uint' },
        { name: 'name', type: 'str' }
      ],
      rows: [
        [1, 'Alice'],
        [2, 'Bob']
      ]
    }
  ]
}
```

### Testing

```bash
npm test
```

12 tests. All passing.

---

## Clojure

Uses Instaparse with EBNF grammar. Functional transformation. Immutable data.

### Installation

```bash
cd clojure/
# Dependencies auto-downloaded via deps.edn
```

Dependencies: `instaparse 1.4.12`, `org.clojure/data.json 2.4.0`

### Command Line

```bash
clojure -M -m three-tl.parser input.3tl        # Compact JSON
clojure -M -m three-tl.parser input.3tl true   # Pretty-printed
```

### Library Usage

```clojure
(require '[three-tl.parser :as parser])

;; Parse file
(def doc (parser/parse-file "../examples/products.3tl"))

;; Parse string
(def doc (parser/parse-string 
  "#! User
   #@ id:uint, name:str
   1, Alice"))

;; Access data
(doseq [table (:tables doc)]
  (println "Table:" (:name table))
  (doseq [col (:columns table)]
    (println "  " (:name col) ":" (:type col)))
  (doseq [row (:rows table)]
    (println "  Row:" row)))

;; Convert to JSON
(parser/to-json doc true)
```

### Data Structures

```clojure
{:tables
 [{:name "User"
   :columns [{:name "id" :type {:base-type "uint"}}
             {:name "name" :type {:base-type "str"}}]
   :rows [[1 "Alice"]
          [2 "Bob"]]}]}
```

### Testing

```bash
clojure -X:test
```

12 tests. All passing.

---

## Go

Uses Participle parser. Grammar defined via struct tags. Go 1.21+.

### Installation

```bash
cd go/
go mod download
```

Dependencies: `github.com/alecthomas/participle/v2 v2.1.1`

### Command Line

```bash
go run ./cmd/3tl-parser input.3tl              # Compact JSON
go run ./cmd/3tl-parser input.3tl --pretty     # Pretty-printed
```

### Library Usage

```go
package main

import (
    "fmt"
    "log"
    "github.com/jiriknesl/3tl/pkg/parser"
)

func main() {
    // Parse file
    doc, err := parser.ParseFile("../examples/products.3tl")
    if err != nil {
        log.Fatal(err)
    }

    // Parse string
    doc, err = parser.ParseString(`
#! User
#@ id:uint, name:str
1, Alice
`)
    if err != nil {
        log.Fatal(err)
    }

    // Access data
    for _, table := range doc.Tables {
        fmt.Printf("Table: %s\n", table.Name)
        for _, col := range table.Columns {
            fmt.Printf("  %s: %s\n", col.Name, col.Type)
        }
        for _, row := range table.Rows {
            fmt.Printf("  Row: %v\n", row)
        }
    }

    // Convert to JSON
    json, err := parser.ToJSON(doc, true)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(json)
}
```

### Data Structures

```go
type Document struct {
    Tables []Table `json:"tables"`
}

type Table struct {
    Name    string     `json:"name"`
    Columns []Column   `json:"columns"`
    Rows    [][]any    `json:"rows"`
}

type Column struct {
    Name string `json:"name"`
    Type string `json:"type"`
}
```

### Testing

```bash
go test ./pkg/parser -v
```

12 tests. All passing.

---

## JSON Output

All parsers produce identical JSON:

```json
{
  "tables": [
    {
      "name": "User",
      "columns": [
        {
          "name": "id",
          "type": "uint"
        },
        {
          "name": "name",
          "type": "str"
        }
      ],
      "rows": [
        [1, "Alice"],
        [2, "Bob"]
      ]
    }
  ]
}
```

Type information preserved. Foreign keys explicit. Arrays and nullability marked.

## Performance

All parsers validated with identical test suites:

- Basic table parsing
- Nullable types
- Array types
- Decimal types with precision
- Ref (foreign key) types
- Enum types with validation
- Multiple tables
- Comments (ignored)
- Quoted CSV fields
- Case-insensitive types
- Unicode identifiers
- JSON output

12 tests per implementation. 48 tests total. All passing.

## Choosing a Parser

| Language | Best For | Notes |
|----------|----------|-------|
| Python | Data science, scripting | Most common for LLM work |
| JavaScript | Web apps, Node services | ES modules, modern syntax |
| Clojure | Functional programming | Immutable data structures |
| Go | Systems, performance | Compiled, fast, type-safe |

Pick based on your environment. All parsers are complete and tested.
