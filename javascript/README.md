# 3TL JavaScript Parser

JavaScript/Node.js implementation of the 3TL (Typed Talking To LLMs) parser using [Peggy](https://peggyjs.org/) (PEG parser generator).

## Features

- Full Unicode support
- Parses 3TL files into JavaScript objects
- Converts to JSON
- Uses Peggy PEG grammar
- Case-insensitive type names
- Comprehensive type support

## Installation

```bash
npm install
```

## Usage

### Parse a file to JSON

```bash
node src/cli.js ../examples/products.3tl --pretty
```

### Use as a library

```javascript
import { parseString, parseFile, toJSON } from './src/parser.js';

// Parse a string
const doc = parseString('#! User\n#@ id:uint, name:str\n1, Alice\n');

// Parse a file
const doc = parseFile('../examples/products.3tl');

// Convert to JSON
console.log(toJSON(doc, true)); // pretty-printed
```

## Running Tests

```bash
npm test
```

All 12 tests pass:
- ✔ parse basic table
- ✔ parse nullable type
- ✔ parse array type
- ✔ parse decimal type
- ✔ parse ref type
- ✔ parse enum type
- ✔ parse multiple tables
- ✔ ignore comments
- ✔ parse quoted fields
- ✔ case-insensitive types
- ✔ unicode identifiers
- ✔ to JSON

## Project Structure

```
javascript/
├── package.json           # Project configuration
├── src/
│   ├── grammar.peggy      # Peggy PEG grammar
│   ├── parser.js          # Main parser implementation
│   └── cli.js             # Command-line interface
└── test/
    └── parser.test.js     # Tests using Node.js test runner
```

## Grammar

The parser uses a Peggy PEG grammar defined in `src/grammar.peggy`. The grammar supports:

- Unicode identifiers (café, 名前, etc.)
- Case-insensitive type names (int, INT, Int)
- Flexible array/nullable modifiers (int[]?, int?[])
- Comments anywhere in the file
- Multiple tables per file
- Foreign key references: `ref(Table.column)`
- Enums: `enum(val1|val2|val3)`
- Decimal types: `decimal(precision,scale)`

## Example Output

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

## Dependencies

- Node.js 16+ (uses ES modules and native test runner)
- Peggy ^4.0.3 (PEG parser generator)

## Notes

- Uses ES modules (`type: "module"` in package.json)
- Uses Node.js built-in test runner (no external test framework needed)
- Automatic type conversion (strings → numbers, booleans, null)
- Proper handling of CSV quoted fields with escaped quotes
