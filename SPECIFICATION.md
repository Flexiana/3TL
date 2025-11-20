# 3TL: Typed Talking To LLMs

3TL is a lightweight format to help communication between humans and LLMs.

It is enriched CSV with types inspired by SQL and C-like programming languages.

Data themselves are a valid CSV. The whole grammar extends CSV via comments.

## Quick Start

```bash
# Install dependencies
pip install -r python/requirements.txt

# Validate a 3TL file
python python/validator.py examples/products.3tl

# Parse to JSON
python python/parser.py examples/products.3tl --pretty

# Run tests
python python/test_parser.py
```

## Features
- Token Efficient: Minimal syntax overhead compared to JSON/XML.
- Strictly Typed: Supports Integers, Floats, Decimals (Currency), Booleans, and Dates.
- Relational: Native support for Foreign Keys (ref) and Enums.
- LLM-Friendly: Uses C-like type names (i32, str, u64) that LLMs already understand perfectly.
- Compatible: The data payload is valid RFC 4180 CSV (compatible with Excel/Pandas via comment filtering).


Generally, it contains 3 things:
1. There can be multiple tables in one file. Each table has a header that gives it a name.
2. Optionally, table  might have type description.
3. Columns can refer to other tables.

## Supported Types Reference

- Integers: i8, i16, i32, i64, int (signed), u8, u16, u32, u64, uint (unsigned)
- Floats: f32, f64 (IEEE 754)
- Financial: decimal(p,s) (Fixed point for currency)
- Boolean: bool (true/false)
- Text: str (short), text (long/multiline)
- Date/Time: date, time, datetime (ISO8601), timestamp (unix epoch)
- Logic: ref(Table.Column), enum(opt1|opt2), type[] (array)
- Nullable: Append '?' (e.g., int?, str?)

**Note:** Type names are case-insensitive (int, INT, Int are all valid).

## Modifiers

Arrays and nullable can be combined in either order:
- `int[]?` - nullable array of integers
- `int?[]` - array of nullable integers

## Null Values

Null values can be represented as:
- Empty field: `1,,3` or `1, ,3`
- Explicit keyword: `null` or `NULL`

## Identifiers

Table names, column names, and enum values follow identifier rules:
- Must start with a letter or underscore
- Can contain letters, digits, and underscores
- Unicode letters are supported (e.g., café, 名前)

## Comments

Comments start with `#` followed by a space or any character except `!` or `@`:
- `# This is a comment`
- `#This is also a comment`

Comments can appear anywhere in the file, including between schema and data rows.

## Format

In each CSV file, we have tables. Table name starts with #! {here comes the table name}.
Under table name, we have type descriptions that starts with #@ {here comes the type description}.
Then, there are data.
Also, we specify that "# " is a comment.

## Example

```csv

# Here we have our articles
#! Article
#@ id:uint, slug:str, title:str, content:str?, created_at:datetime
1, how-to-learn-italian, How to learn Italian?, Here is how to learn Italian..., 2025-01-05 10:20:30

#! Comment
#@ id:uint, article_id:ref(Article.id), comment:str, created_at:datetime
1, 1, Awesome article!, 2025-02-03 10:10:10

```

In this repository, we provide a simple grammar, validator, and parser.

## Grammar

The canonical grammar is defined in `3tl-grammar.lark` using EBNF (Extended Backus-Naur Form) with the Lark parser syntax. An ABNF version is also provided in `3tl-grammar.abnf` for reference.

Key grammar rules:

```ebnf
// File structure
three_tl_file = (LINE_BREAK | element)*
element = comment_line | table_block

// Table structure
table_block = table_header (schema_def | comment_line | data_row)*
table_header = "#!" WS? identifier WS? LINE_BREAK
schema_def = "#@" WS? col_defs WS? LINE_BREAK

// Type expressions (case-insensitive)
type_expr = base_type type_modifier?
type_modifier = array_suffix nullable_suffix  // int[]?
              | nullable_suffix array_suffix  // int?[]
              | array_suffix                  // int[]
              | nullable_suffix               // int?

// Base types (case-insensitive via /i flag)
integer_type = /i8|i16|i32|i64|int|u8|u16|u32|u64|uint/i
float_type = /f32|f64|float/i
decimal_type = /decimal/i WS? "(" WS? /\d+/ WS? "," WS? /\d+/ WS? ")"
bool_type = /bool/i
text_type = /str|text/i
time_type = /date|time|datetime|timestamp/i
ref_type = /ref/i WS? "(" WS? identifier "." identifier WS? ")"
enum_type = /enum/i WS? "(" WS? enum_values WS? ")"

// Data rows (RFC 4180 CSV compatible)
data_row = field ("," field)* LINE_BREAK
field = WS? (quoted_field | unquoted_field?) WS?
```