package parser

import (
	"testing"
)

func TestParseBasicTable(t *testing.T) {
	input := `#! User
#@ id:uint, name:str, email:str
1, Alice, alice@example.com
2, Bob, bob@example.com
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	if len(doc.Tables) != 1 {
		t.Errorf("Expected 1 table, got %d", len(doc.Tables))
	}

	table := doc.Tables[0]
	if table.Name != "User" {
		t.Errorf("Expected table name 'User', got '%s'", table.Name)
	}

	if len(table.Columns) != 3 {
		t.Errorf("Expected 3 columns, got %d", len(table.Columns))
	}

	if len(table.Rows) != 2 {
		t.Errorf("Expected 2 rows, got %d", len(table.Rows))
	}

	if table.Columns[0].Name != "id" || table.Columns[0].Type != "uint" {
		t.Errorf("Column 0 mismatch")
	}

	if table.Rows[0][0] != int64(1) {
		t.Errorf("Expected row 0 col 0 to be 1, got %v", table.Rows[0][0])
	}

	if table.Rows[0][1] != "Alice" {
		t.Errorf("Expected row 0 col 1 to be 'Alice', got %v", table.Rows[0][1])
	}
}

func TestParseNullableType(t *testing.T) {
	input := `#! Article
#@ id:uint, title:str, content:str?
1, Hello, This is content
2, World,
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Columns[2].Type != "str?" {
		t.Errorf("Expected type 'str?', got '%s'", table.Columns[2].Type)
	}

	if table.Rows[1][2] != nil {
		t.Errorf("Expected nil, got %v", table.Rows[1][2])
	}
}

func TestParseArrayType(t *testing.T) {
	input := `#! Test
#@ id:uint, tags:str[]
1, tag1
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Columns[1].Type != "str[]" {
		t.Errorf("Expected type 'str[]', got '%s'", table.Columns[1].Type)
	}
}

func TestParseDecimalType(t *testing.T) {
	input := `#! Product
#@ id:uint, price:decimal(10,2)
1, 19.99
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Columns[1].Type != "decimal(10,2)" {
		t.Errorf("Expected type 'decimal(10,2)', got '%s'", table.Columns[1].Type)
	}

	if table.Rows[0][1] != 19.99 {
		t.Errorf("Expected 19.99, got %v", table.Rows[0][1])
	}
}

func TestParseRefType(t *testing.T) {
	input := `#! Comment
#@ id:uint, article_id:ref(Article.id)
1, 42
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Columns[1].Type != "ref(Article.id)" {
		t.Errorf("Expected type 'ref(Article.id)', got '%s'", table.Columns[1].Type)
	}

	if table.Rows[0][1] != int64(42) {
		t.Errorf("Expected 42, got %v", table.Rows[0][1])
	}
}

func TestParseEnumType(t *testing.T) {
	input := `#! Task
#@ id:uint, status:enum(pending|in_progress|completed)
1, pending
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	typeStr := table.Columns[1].Type
	if typeStr != "enum(pending | in_progress | completed)" {
		t.Errorf("Expected enum type, got '%s'", typeStr)
	}

	if table.Rows[0][1] != "pending" {
		t.Errorf("Expected 'pending', got %v", table.Rows[0][1])
	}
}

func TestParseMultipleTables(t *testing.T) {
	input := `#! User
#@ id:uint, name:str
1, Alice

#! Post
#@ id:uint, user_id:ref(User.id), title:str
1, 1, My First Post
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	if len(doc.Tables) != 2 {
		t.Errorf("Expected 2 tables, got %d", len(doc.Tables))
	}

	if doc.Tables[0].Name != "User" {
		t.Errorf("Expected first table 'User', got '%s'", doc.Tables[0].Name)
	}

	if doc.Tables[1].Name != "Post" {
		t.Errorf("Expected second table 'Post', got '%s'", doc.Tables[1].Name)
	}

	if len(doc.Tables[1].Columns) != 3 {
		t.Errorf("Expected 3 columns in Post table, got %d", len(doc.Tables[1].Columns))
	}
}

func TestIgnoreComments(t *testing.T) {
	input := `# This is a comment
#! User
# Another comment
#@ id:uint, name:str
# Yet another comment
1, Alice
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	if len(doc.Tables) != 1 {
		t.Errorf("Expected 1 table, got %d", len(doc.Tables))
	}

	if len(doc.Tables[0].Rows) != 1 {
		t.Errorf("Expected 1 row, got %d", len(doc.Tables[0].Rows))
	}
}

func TestParseQuotedFields(t *testing.T) {
	input := `#! Article
#@ id:uint, title:str, content:str
1, "Hello, World", "This is a test"
2, Normal, "With ""quotes"" inside"
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Rows[0][1] != "Hello, World" {
		t.Errorf("Expected 'Hello, World', got %v", table.Rows[0][1])
	}

	if table.Rows[0][2] != "This is a test" {
		t.Errorf("Expected 'This is a test', got %v", table.Rows[0][2])
	}

	if table.Rows[1][2] != "With \"quotes\" inside" {
		t.Errorf("Expected 'With \"quotes\" inside', got %v", table.Rows[1][2])
	}
}

func TestCaseInsensitiveTypes(t *testing.T) {
	input := `#! Test
#@ id:UINT, name:STR, active:BOOL
1, Alice, true
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Columns[0].Type != "uint" {
		t.Errorf("Expected 'uint', got '%s'", table.Columns[0].Type)
	}

	if table.Columns[1].Type != "str" {
		t.Errorf("Expected 'str', got '%s'", table.Columns[1].Type)
	}

	if table.Columns[2].Type != "bool" {
		t.Errorf("Expected 'bool', got '%s'", table.Columns[2].Type)
	}

	if table.Rows[0][2] != true {
		t.Errorf("Expected true, got %v", table.Rows[0][2])
	}
}

func TestUnicodeIdentifiers(t *testing.T) {
	input := `#! Café
#@ id:uint, nombre:str
1, José
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	table := doc.Tables[0]

	if table.Name != "Café" {
		t.Errorf("Expected table name 'Café', got '%s'", table.Name)
	}

	if table.Columns[1].Name != "nombre" {
		t.Errorf("Expected column name 'nombre', got '%s'", table.Columns[1].Name)
	}

	if table.Rows[0][1] != "José" {
		t.Errorf("Expected 'José', got %v", table.Rows[0][1])
	}
}

func TestToJSON(t *testing.T) {
	input := `#! User
#@ id:uint, name:str
1, Alice
`

	doc, err := ParseString(input)
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}

	json, err := ToJSON(doc, false)
	if err != nil {
		t.Fatalf("ToJSON error: %v", err)
	}

	if json == "" {
		t.Error("JSON output is empty")
	}

	// Basic checks
	if len(json) < 10 {
		t.Error("JSON output is too short")
	}
}
