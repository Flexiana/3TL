#!/usr/bin/env python3
"""
Tests for the 3TL parser.
"""

import sys
from parser import ThreeTLParser, TypeInfo, Column, Table, Document


def test_basic_table():
    """Test parsing a basic table."""
    content = """#! User
#@ id:uint, name:str, email:str
1, Alice, alice@example.com
2, Bob, bob@example.com
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    assert len(doc.tables) == 1, f"Expected 1 table, got {len(doc.tables)}"

    table = doc.tables[0]
    assert table.name == "User", f"Expected table name 'User', got '{table.name}'"
    assert len(table.columns) == 3, f"Expected 3 columns, got {len(table.columns)}"
    assert len(table.rows) == 2, f"Expected 2 rows, got {len(table.rows)}"

    # Check columns
    assert table.columns[0].name == "id"
    assert table.columns[0].type.base_type == "uint"
    assert table.columns[1].name == "name"
    assert table.columns[1].type.base_type == "str"

    # Check data
    assert table.rows[0][0] == 1
    assert table.rows[0][1] == "Alice"
    assert table.rows[1][0] == 2
    assert table.rows[1][1] == "Bob"

    print("✓ test_basic_table passed")


def test_nullable_type():
    """Test nullable types."""
    content = """#! Article
#@ id:uint, title:str, content:str?
1, Hello, This is content
2, World,
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    assert table.columns[2].type.is_nullable, "Expected nullable type"
    assert table.rows[1][2] is None, "Expected None for empty field"

    print("✓ test_nullable_type passed")


def test_array_type():
    """Test array types."""
    content = """#! Test
#@ id:uint, tags:str[]
1, tag1
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    assert table.columns[1].type.is_array, "Expected array type"

    print("✓ test_array_type passed")


def test_decimal_type():
    """Test decimal type."""
    content = """#! Product
#@ id:uint, price:decimal(10,2)
1, 19.99
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    decimal_col = table.columns[1]
    assert decimal_col.type.base_type == "decimal"
    assert decimal_col.type.params['precision'] == 10
    assert decimal_col.type.params['scale'] == 2

    print("✓ test_decimal_type passed")


def test_ref_type():
    """Test reference type."""
    content = """#! Comment
#@ id:uint, article_id:ref(Article.id)
1, 42
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    ref_col = table.columns[1]
    assert ref_col.type.base_type == "ref"
    assert ref_col.type.params['table'] == "Article"
    assert ref_col.type.params['column'] == "id"

    print("✓ test_ref_type passed")


def test_enum_type():
    """Test enum type."""
    content = """#! Task
#@ id:uint, status:enum(pending|in_progress|completed)
1, pending
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    enum_col = table.columns[1]
    assert enum_col.type.base_type == "enum"
    assert "pending" in enum_col.type.params['values']
    assert "in_progress" in enum_col.type.params['values']
    assert "completed" in enum_col.type.params['values']

    print("✓ test_enum_type passed")


def test_multiple_tables():
    """Test parsing multiple tables."""
    content = """#! User
#@ id:uint, name:str
1, Alice

#! Post
#@ id:uint, user_id:ref(User.id), title:str
1, 1, My First Post
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    assert len(doc.tables) == 2, f"Expected 2 tables, got {len(doc.tables)}"
    assert doc.tables[0].name == "User"
    assert doc.tables[1].name == "Post"
    assert len(doc.tables[1].columns) == 3

    print("✓ test_multiple_tables passed")


def test_comments():
    """Test that comments are ignored."""
    content = """# This is a comment
#! User
# Another comment
#@ id:uint, name:str
# Yet another comment
1, Alice
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    assert len(doc.tables) == 1
    assert len(doc.tables[0].rows) == 1

    print("✓ test_comments passed")


def test_quoted_fields():
    """Test quoted CSV fields."""
    content = """#! Article
#@ id:uint, title:str, content:str
1, "Hello, World", "This is a test"
2, Normal, "With ""quotes"" inside"
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    assert table.rows[0][1] == "Hello, World"
    assert table.rows[0][2] == "This is a test"
    assert table.rows[1][2] == 'With "quotes" inside'

    print("✓ test_quoted_fields passed")


def test_case_insensitive_types():
    """Test case-insensitive type names."""
    content = """#! Test
#@ id:UINT, name:STR, active:BOOL
1, Alice, true
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    assert table.columns[0].type.base_type == "uint"
    assert table.columns[1].type.base_type == "str"
    assert table.columns[2].type.base_type == "bool"

    print("✓ test_case_insensitive_types passed")


def test_unicode_identifiers():
    """Test Unicode in identifiers and data."""
    content = """#! Café
#@ id:uint, nombre:str
1, José
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    table = doc.tables[0]
    assert table.name == "Café"
    assert table.columns[1].name == "nombre"
    assert table.rows[0][1] == "José"

    print("✓ test_unicode_identifiers passed")


def test_to_json():
    """Test JSON serialization."""
    content = """#! User
#@ id:uint, name:str
1, Alice
"""

    parser = ThreeTLParser()
    doc = parser.parse_string(content)

    json_str = doc.to_json()
    assert "User" in json_str
    assert "Alice" in json_str
    assert "tables" in json_str

    print("✓ test_to_json passed")


def run_all_tests():
    """Run all tests."""
    tests = [
        test_basic_table,
        test_nullable_type,
        test_array_type,
        test_decimal_type,
        test_ref_type,
        test_enum_type,
        test_multiple_tables,
        test_comments,
        test_quoted_fields,
        test_case_insensitive_types,
        test_unicode_identifiers,
        test_to_json,
    ]

    failed = []

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed.append(test.__name__)

    print(f"\n{'='*60}")
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(tests)} tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    run_all_tests()
