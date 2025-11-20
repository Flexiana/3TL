# 3TL Python Validator

Python validator for 3TL (Typed Talking To LLMs) format using the [Lark](https://lark-parser.readthedocs.io/) parsing library.

## Features

- Full Unicode support
- Validates against the complete 3TL grammar
- Case-insensitive type names
- Detailed error messages with line and column numbers
- Optional parse tree visualization

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Validate a file

```bash
python validator.py examples/products.3tl
```

### Validate a string

```bash
python validator.py --string "#! Test
#@ id:uint, name:str
1, Alice
"
```

### Show parse tree

```bash
python validator.py --show-tree file.3tl
```

### Use custom grammar

```bash
python validator.py --grammar custom-grammar.lark file.3tl
```

## Exit Codes

- `0`: Valid 3TL format
- `1`: Invalid format or error

## Examples

Valid:
```bash
$ python validator.py ../examples/blog.3tl
Valid 3TL format
```

Invalid:
```bash
$ python validator.py --string "#@ id:uint"
Invalid: Unexpected character at line 1, column 1
  #@ id:uint
  ^
Expected: {'LINE_BREAK', '__ANON_0', 'COMMENT_START'}
```

## Grammar

The validator uses the Lark EBNF grammar defined in `../3tl-grammar.lark`. The grammar supports:

- Unicode identifiers (café, 名前, etc.)
- Case-insensitive type names (int, INT, Int all valid)
- Flexible array/nullable modifiers (int[]?, int?[])
- Comments anywhere in the file
- Multiple tables per file
- Foreign key references and enums
