#!/usr/bin/env python3
"""
3TL Parser - Parses 3TL files into Python data structures.

Usage:
    from parser import ThreeTLParser

    parser = ThreeTLParser()
    document = parser.parse_file("data.3tl")

    for table in document.tables:
        print(f"Table: {table.name}")
        print(f"Columns: {table.columns}")
        for row in table.rows:
            print(row)
"""

import sys
import argparse
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Any

from lark import Lark, Transformer, Tree, Token


# Get the grammar file path relative to this script
GRAMMAR_FILE = Path(__file__).parent.parent / "3tl-grammar.lark"


@dataclass
class TypeInfo:
    """Type information for a column."""
    base_type: str  # e.g., "int", "str", "decimal"
    is_array: bool = False
    is_nullable: bool = False
    params: Optional[dict[str, Any]] = None  # For decimal(10,2), ref(Table.col), enum(a|b)

    def __str__(self):
        result = self.base_type
        if self.params:
            if self.base_type == "decimal":
                result = f"decimal({self.params['precision']},{self.params['scale']})"
            elif self.base_type == "ref":
                result = f"ref({self.params['table']}.{self.params['column']})"
            elif self.base_type == "enum":
                result = f"enum({' | '.join(self.params['values'])})"

        if self.is_array:
            result += "[]"
        if self.is_nullable:
            result += "?"

        return result


@dataclass
class Column:
    """Column definition."""
    name: str
    type: TypeInfo


@dataclass
class Table:
    """Table with schema and data."""
    name: str
    columns: list[Column] = field(default_factory=list)
    rows: list[list[Any]] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'name': self.name,
            'columns': [{'name': col.name, 'type': str(col.type)} for col in self.columns],
            'rows': self.rows
        }


@dataclass
class Document:
    """3TL document containing multiple tables."""
    tables: list[Table] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'tables': [table.to_dict() for table in self.tables]
        }

    def to_json(self, indent=2):
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class ThreeTLTransformer(Transformer):
    """Transform parse tree into 3TL data structures."""

    def __init__(self):
        super().__init__()
        self.current_table: Optional[Table] = None

    def three_tl_file(self, items):
        """Process the entire file."""
        tables = [item for item in items if isinstance(item, Table)]
        return Document(tables=tables)

    def element(self, items):
        """Process an element (table or comment)."""
        return items[0] if items else None

    def table_block(self, items):
        """Process a table block."""
        table = None

        for item in items:
            if isinstance(item, Table):
                table = item
            elif isinstance(item, Column):
                # Individual column from schema
                if table:
                    table.columns.append(item)
            elif isinstance(item, list):
                # Check if it's a list of columns (schema) or data row
                if item and isinstance(item[0], Column):
                    # Schema definition
                    if table:
                        table.columns = item
                elif table:
                    # Data row
                    table.rows.append(item)

        return table

    def table_header(self, items):
        """Process table header: #! TableName"""
        name = ''.join(str(item) for item in items if item)
        return Table(name=name)

    def schema_def(self, items):
        """Process schema definition: #@ col:type, col:type"""
        # Filter out None items and find the list of columns
        for item in items:
            if isinstance(item, list):
                # Filter out None values from the column list
                return [col for col in item if col is not None]
        return []

    def col_defs(self, items):
        """Process column definitions."""
        return items

    def col_def(self, items):
        """Process single column definition: name:type"""
        name = items[0]
        type_info = items[1]
        return Column(name=name, type=type_info)

    def identifier(self, items):
        """Process identifier."""
        return ''.join(str(item) for item in items)

    def type_expr(self, items):
        """Process type expression."""
        base_type = items[0]

        # Check for modifiers
        if len(items) > 1:
            modifier = items[1]
            if isinstance(modifier, dict):
                base_type.is_array = modifier.get('is_array', False)
                base_type.is_nullable = modifier.get('is_nullable', False)

        return base_type

    def type_modifier(self, items):
        """Process type modifier."""
        is_array = False
        is_nullable = False

        for item in items:
            if item == 'array':
                is_array = True
            elif item == 'nullable':
                is_nullable = True

        return {'is_array': is_array, 'is_nullable': is_nullable}

    def array_suffix(self, items):
        """Process array suffix []."""
        return 'array'

    def nullable_suffix(self, items):
        """Process nullable suffix ?."""
        return 'nullable'

    def base_type(self, items):
        """Process base type."""
        return items[0]

    def integer_type(self, items):
        """Process integer type."""
        return TypeInfo(base_type=str(items[0]).lower())

    def float_type(self, items):
        """Process float type."""
        return TypeInfo(base_type=str(items[0]).lower())

    def bool_type(self, items):
        """Process bool type."""
        return TypeInfo(base_type='bool')

    def text_type(self, items):
        """Process text type."""
        return TypeInfo(base_type=str(items[0]).lower())

    def time_type(self, items):
        """Process time type."""
        return TypeInfo(base_type=str(items[0]).lower())

    def decimal_type(self, items):
        """Process decimal type: decimal(p,s)."""
        # Extract precision and scale from items
        digits = [str(item) for item in items if str(item).isdigit()]
        precision = int(digits[0]) if len(digits) > 0 else 10
        scale = int(digits[1]) if len(digits) > 1 else 2

        return TypeInfo(
            base_type='decimal',
            params={'precision': precision, 'scale': scale}
        )

    def ref_type(self, items):
        """Process ref type: ref(Table.column)."""
        # Filter out tokens and keep only identifiers (strings)
        identifiers = [item for item in items if isinstance(item, str) and item != 'ref']
        table = identifiers[0] if len(identifiers) > 0 else ''
        column = identifiers[1] if len(identifiers) > 1 else ''

        return TypeInfo(
            base_type='ref',
            params={'table': table, 'column': column}
        )

    def enum_type(self, items):
        """Process enum type: enum(val1|val2|val3)."""
        # Filter out the 'enum' keyword and extract the list
        values = []
        for item in items:
            if isinstance(item, list):
                values = item
                break

        return TypeInfo(
            base_type='enum',
            params={'values': values}
        )

    def enum_values(self, items):
        """Process enum values."""
        # Items are identifier strings
        return [item for item in items if isinstance(item, str)]

    def data_row(self, items):
        """Process data row."""
        # Keep all fields, including empty ones
        return [self._clean_field(item) for item in items]

    def field(self, items):
        """Process field."""
        # Return the first non-None item, or None if all are None
        for item in items:
            if item is not None:
                return item
        return ''  # Empty field

    def quoted_field(self, items):
        """Process quoted field."""
        if items and isinstance(items[0], Token):
            # Remove surrounding quotes and unescape doubled quotes
            value = str(items[0])
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            value = value.replace('""', '"')
            return value
        return str(items[0]) if items else ''

    def unquoted_field(self, items):
        """Process unquoted field."""
        return str(items[0]).strip() if items else ''

    def _clean_field(self, value):
        """Clean and convert field value."""
        if value is None or value == '':
            return None

        # Try to detect type and convert
        value_str = str(value).strip()

        if value_str.lower() in ('null', ''):
            return None

        # Try boolean
        if value_str.lower() in ('true', 'false'):
            return value_str.lower() == 'true'

        # Try integer
        try:
            if '.' not in value_str:
                return int(value_str)
        except ValueError:
            pass

        # Try float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Return as string
        return value_str

    # Ignore whitespace and line breaks
    def WS(self, items):
        return None

    def LINE_BREAK(self, items):
        return None

    def comment_line(self, items):
        """Ignore comments."""
        return None


class ThreeTLParser:
    """Parser for 3TL format."""

    def __init__(self, grammar_file: Optional[Path] = None):
        """Initialize parser with grammar file."""
        self.grammar_file = grammar_file or GRAMMAR_FILE
        grammar_text = self.grammar_file.read_text(encoding='utf-8')
        self.parser = Lark(grammar_text, parser='earley', ambiguity='resolve')
        self.transformer = ThreeTLTransformer()

    def parse_string(self, content: str) -> Document:
        """Parse 3TL string into Document."""
        tree = self.parser.parse(content)
        document = self.transformer.transform(tree)
        return document

    def parse_file(self, filepath: str) -> Document:
        """Parse 3TL file into Document."""
        content = Path(filepath).read_text(encoding='utf-8')
        return self.parse_string(content)


def main():
    parser = argparse.ArgumentParser(
        description='Parse 3TL files into JSON'
    )
    parser.add_argument(
        'file',
        help='Path to 3TL file to parse'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file (default: stdout)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    try:
        three_tl_parser = ThreeTLParser()
        document = three_tl_parser.parse_file(args.file)

        # Convert to JSON
        indent = 2 if args.pretty else None
        json_output = document.to_json(indent=indent)

        if args.output:
            Path(args.output).write_text(json_output, encoding='utf-8')
            print(f"Parsed {args.file} -> {args.output}")
        else:
            print(json_output)

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
