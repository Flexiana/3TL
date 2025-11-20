# 3TL Clojure Parser

Clojure implementation of the 3TL (Typed Talking To LLMs) parser using [Instaparse](https://github.com/Engelberg/instaparse).

## Features

- Full Unicode support
- Parses 3TL files into Clojure data structures
- Converts to JSON
- Uses Instaparse EBNF grammar
- Case-insensitive type names
- Comprehensive type support

## Installation

```bash
# Install dependencies
clojure -P
```

## Usage

### Parse a file to JSON

```bash
clojure -M -m three-tl.parser ../examples/products.3tl --pretty
```

### Use as a library

```clojure
(require '[three-tl.parser :as parser])

;; Parse a string
(def doc (parser/parse-string "#! User\n#@ id:uint, name:str\n1, Alice\n"))

;; Parse a file
(def doc (parser/parse-file "../examples/products.3tl"))

;; Convert to JSON
(parser/to-json doc true)  ; pretty-printed
```

## Running Tests

```bash
clojure -M:test
```

## REPL Development

```bash
clojure -M:repl
```

## Project Structure

```
clojure/
├── deps.edn                    # Project dependencies
├── resources/
│   └── grammar.ebnf           # Instaparse EBNF grammar
├── src/
│   └── three_tl/
│       └── parser.clj         # Main parser implementation
└── test/
    └── three_tl/
        └── parser_test.clj    # Tests
```

## Grammar

The parser uses an Instaparse EBNF grammar defined in `resources/grammar.ebnf`. The grammar supports:

- Unicode identifiers (café, 名前, etc.)
- Case-insensitive type names (int, INT, Int)
- Flexible array/nullable modifiers (int[]?, int?[])
- Comments anywhere in the file
- Multiple tables per file
- Foreign key references: `ref(Table.column)`
- Enums: `enum(val1|val2|val3)`
- Decimal types: `decimal(precision,scale)`

## Example Output

```clojure
{:tables
 [{:name "User"
   :columns [{:name "id", :type "uint"}
             {:name "name", :type "str"}]
   :rows [[1 "Alice"]
          [2 "Bob"]]}]}
```

## Dependencies

- Clojure 1.11.1
- Instaparse 1.4.12
- org.clojure/data.json 2.4.0
