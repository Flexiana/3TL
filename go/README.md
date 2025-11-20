# 3TL Go Parser

Go implementation of the 3TL (Typed Talking To LLMs) parser using [Participle](https://github.com/alecthomas/participle).

## Features

- Full Unicode support
- Parses 3TL files into Go structs
- Converts to JSON
- Uses Participle parser with struct tags
- Case-insensitive type names
- Comprehensive type support

## Installation

Requires Go 1.21 or later.

```bash
go mod download
```

## Usage

### Parse a file to JSON

```bash
go run ./cmd/3tl-parser ../examples/products.3tl --pretty
```

### Use as a library

```go
import "github.com/jiriknesl/3tl/pkg/parser"

// Parse a string
doc, err := parser.ParseString("#! User\n#@ id:uint, name:str\n1, Alice\n")
if err != nil {
    log.Fatal(err)
}

// Parse a file
doc, err := parser.ParseFile("../examples/products.3tl")
if err != nil {
    log.Fatal(err)
}

// Convert to JSON
jsonStr, err := parser.ToJSON(doc, true) // pretty-printed
if err != nil {
    log.Fatal(err)
}
fmt.Println(jsonStr)
```

## Running Tests

```bash
go test ./pkg/parser -v
```

All 12 tests should pass:
- ✓ TestParseBasicTable
- ✓ TestParseNullableType
- ✓ TestParseArrayType
- ✓ TestParseDecimalType
- ✓ TestParseRefType
- ✓ TestParseEnumType
- ✓ TestParseMultipleTables
- ✓ TestIgnoreComments
- ✓ TestParseQuotedFields
- ✓ TestCaseInsensitiveTypes
- ✓ TestUnicodeIdentifiers
- ✓ TestToJSON

## Project Structure

```
go/
├── go.mod                  # Module definition
├── cmd/
│   └── 3tl-parser/
│       └── main.go         # Command-line interface
└── pkg/
    └── parser/
        ├── parser.go       # Main parser implementation
        └── parser_test.go  # Tests
```

## Parser Implementation

The parser uses Participle, which allows defining the grammar using Go struct tags:

```go
type tableHeader struct {
    Name string `parser:"'#' '!' @Ident Newline"`
}

type schemaDef struct {
    Columns []columnDef `parser:"'#' '@' @@ ( ',' @@ )* Newline"`
}
```

The lexer supports:
- Unicode identifiers (café, 名前, etc.)
- Case-insensitive type names (int, INT, Int)
- Flexible array/nullable modifiers (int[]?, int?[])
- Comments anywhere in the file
- Multiple tables per file
- Foreign key references: `ref(Table.column)`
- Enums: `enum(val1|val2|val3)`
- Decimal types: `decimal(precision,scale)`

## Example Output

```go
Document{
    Tables: []Table{
        {
            Name: "User",
            Columns: []Column{
                {Name: "id", Type: "uint"},
                {Name: "name", Type: "str"},
            },
            Rows: [][]any{
                {int64(1), "Alice"},
                {int64(2), "Bob"},
            },
        },
    },
}
```

## Dependencies

- Go 1.21+
- github.com/alecthomas/participle/v2 v2.1.1

## Notes

- Uses Participle's struct-tag based grammar definition
- Automatic type conversion (strings → numbers, booleans, null)
- Proper handling of CSV quoted fields with escaped quotes
- JSON output compatible with other 3TL implementations
