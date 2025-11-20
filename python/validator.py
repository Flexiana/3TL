#!/usr/bin/env python3
"""
3TL Validator - Validates that input conforms to 3TL format using Lark parser.

Usage:
    python validator.py <file.3tl>
    python validator.py --string "3TL content"
"""

import sys
import argparse
from pathlib import Path

from lark import Lark, LarkError, UnexpectedInput, UnexpectedCharacters


# Get the grammar file path relative to this script
GRAMMAR_FILE = Path(__file__).parent.parent / "3tl-grammar.lark"

# Cache the parser instance
_parser = None


def get_parser() -> Lark:
    """Get or create the Lark parser instance."""
    global _parser
    if _parser is None:
        grammar_text = GRAMMAR_FILE.read_text(encoding='utf-8')
        # Use earley parser - resolve ambiguities automatically
        _parser = Lark(grammar_text, parser='earley', ambiguity='resolve')
    return _parser


def validate_string(content: str) -> tuple[bool, str]:
    """
    Validate a 3TL string.

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parser = get_parser()
        tree = parser.parse(content)
        return True, ""

    except UnexpectedCharacters as e:
        # Calculate line and column
        lines = content.split('\n')
        line_num = e.line
        col_num = e.column

        # Get the problematic line
        if 0 <= line_num - 1 < len(lines):
            problem_line = lines[line_num - 1]
            # Show the error with context
            error_msg = f"Unexpected character at line {line_num}, column {col_num}\n"
            error_msg += f"  {problem_line}\n"
            error_msg += f"  {' ' * (col_num - 1)}^\n"
            error_msg += f"Expected: {e.allowed}"
        else:
            error_msg = f"Unexpected character at line {line_num}: {e}"

        return False, error_msg

    except UnexpectedInput as e:
        lines = content.split('\n')
        line_num = e.line
        col_num = e.column

        if 0 <= line_num - 1 < len(lines):
            problem_line = lines[line_num - 1]
            error_msg = f"Parse error at line {line_num}, column {col_num}\n"
            error_msg += f"  {problem_line}\n"
            error_msg += f"  {' ' * (col_num - 1)}^\n"
            if hasattr(e, 'expected'):
                error_msg += f"Expected: {e.expected}"
        else:
            error_msg = f"Parse error at line {line_num}: {e}"

        return False, error_msg

    except LarkError as e:
        return False, f"Parse error: {e}"

    except Exception as e:
        return False, f"Validation error: {e}"


def validate_file(filepath: str) -> tuple[bool, str]:
    """
    Validate a 3TL file.

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"File not found: {filepath}"

        content = path.read_text(encoding='utf-8')
        return validate_string(content)

    except Exception as e:
        return False, f"Error reading file: {e}"


def main():
    parser = argparse.ArgumentParser(
        description='Validate 3TL (Typed Talking To LLMs) files using Lark parser'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Path to 3TL file to validate'
    )
    parser.add_argument(
        '--string', '-s',
        help='Validate a 3TL string directly'
    )
    parser.add_argument(
        '--grammar', '-g',
        help='Path to custom Lark grammar file'
    )
    parser.add_argument(
        '--show-tree', '-t',
        action='store_true',
        help='Show the parse tree for valid input'
    )

    args = parser.parse_args()

    if not args.file and not args.string:
        parser.error('Either a file path or --string must be provided')

    # Override grammar file if specified
    if args.grammar:
        global GRAMMAR_FILE
        GRAMMAR_FILE = Path(args.grammar)
        global _parser
        _parser = None  # Reset cache

    if args.string:
        is_valid, error = validate_string(args.string)
    else:
        is_valid, error = validate_file(args.file)

    if is_valid:
        print("Valid 3TL format")

        # Show parse tree if requested
        if args.show_tree:
            content = args.string if args.string else Path(args.file).read_text(encoding='utf-8')
            tree = get_parser().parse(content)
            print("\nParse tree:")
            print(tree.pretty())

        sys.exit(0)
    else:
        print(f"Invalid: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
