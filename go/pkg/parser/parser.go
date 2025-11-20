// Package parser implements 3TL (Typed Talking To LLMs) parser using Participle
package parser

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"

	"github.com/alecthomas/participle/v2"
	"github.com/alecthomas/participle/v2/lexer"
)

// Document represents a parsed 3TL document
type Document struct {
	Tables []Table `json:"tables"`
}

// Table represents a 3TL table with schema and data
type Table struct {
	Name    string     `json:"name"`
	Columns []Column   `json:"columns"`
	Rows    [][]any    `json:"rows"`
}

// Column represents a column definition
type Column struct {
	Name string `json:"name"`
	Type string `json:"type"`
}

// Internal parsing structures
type file struct {
	Lines []line `parser:"@@*"`
}

type line struct {
	Comment     *comment     `parser:"  @@"`
	TableHeader *tableHeader `parser:"| @@"`
	SchemaDef   *schemaDef   `parser:"| @@"`
	DataRow     *dataRow     `parser:"| @@"`
	EmptyLine   *string      `parser:"| @Newline"`
}

type comment struct {
	Text string `parser:"'#' ( ![@!] @( ~Newline )* )? Newline"`
}

type tableHeader struct {
	Name string `parser:"'#' '!' @Ident Newline"`
}

type schemaDef struct {
	Columns []columnDef `parser:"'#' '@' @@ ( ',' @@ )* Newline"`
}

type columnDef struct {
	Name     string   `parser:"@Ident ':'"`
	TypeName string   `parser:"@TypeName"`
	Params   []string `parser:"( '(' @( Ident | Number ) ( ( ',' | '.' | '|' ) @( Ident | Number ) )* ')' )?"`
	Array    bool     `parser:"@( '[' ']' )?"`
	Nullable bool     `parser:"@'?'?"`
}

type dataRow struct {
	Fields []field `parser:"@@ ( ',' @@ )* Newline"`
}

type field struct {
	Quoted   *string `parser:"  @String"`
	Unquoted *string `parser:"| @( Ident | Number | '.' | '-' | '@' | '_' | '/' | ':' | ~( ',' | Newline | '#' ) )*"`
}

var (
	lex = lexer.MustSimple([]lexer.SimpleRule{
		{Name: "Comment", Pattern: `#[^!@][^\n]*`},
		{Name: "TableMarker", Pattern: `#!`},
		{Name: "SchemaMarker", Pattern: `#@`},
		{Name: "TypeName", Pattern: `(?i)(i8|i16|i32|i64|int|u8|u16|u32|u64|uint|f32|f64|float|bool|str|text|date|time|datetime|timestamp|decimal|ref|enum)\b`},
		{Name: "String", Pattern: `"(?:[^"]|"")*"`},
		{Name: "Number", Pattern: `-?\d+(?:\.\d+)?`},
		{Name: "Ident", Pattern: `[a-zA-Z_\x{00C0}-\x{024F}\x{1E00}-\x{1EFF}\x{0400}-\x{04FF}\x{0370}-\x{03FF}\x{4E00}-\x{9FFF}\x{3040}-\x{309F}\x{30A0}-\x{30FF}][a-zA-Z0-9_\x{00C0}-\x{024F}\x{1E00}-\x{1EFF}\x{0400}-\x{04FF}\x{0370}-\x{03FF}\x{4E00}-\x{9FFF}\x{3040}-\x{309F}\x{30A0}-\x{30FF}]*`},
		{Name: "Punct", Pattern: `[-[!@#$%^&*()+_={}\|:;"'<,>.?/]|\[\]`},
		{Name: "Newline", Pattern: `\r?\n`},
		{Name: "whitespace", Pattern: `[ \t]+`},
	})

	parser = participle.MustBuild[file](
		participle.Lexer(lex),
		participle.Elide("whitespace"),
	)
)

// ParseString parses a 3TL string and returns a Document
func ParseString(input string) (*Document, error) {
	parsed, err := parser.ParseString("", input)
	if err != nil {
		return nil, fmt.Errorf("parse error: %w", err)
	}

	return transform(parsed), nil
}

// ParseFile parses a 3TL file and returns a Document
func ParseFile(filename string) (*Document, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("read file: %w", err)
	}

	return ParseString(string(data))
}

// ToJSON converts a Document to JSON
func ToJSON(doc *Document, pretty bool) (string, error) {
	var data []byte
	var err error

	if pretty {
		data, err = json.MarshalIndent(doc, "", "  ")
	} else {
		data, err = json.Marshal(doc)
	}

	if err != nil {
		return "", fmt.Errorf("marshal JSON: %w", err)
	}

	return string(data), nil
}

// WriteJSON writes a Document to JSON to an io.Writer
func WriteJSON(w io.Writer, doc *Document, pretty bool) error {
	jsonStr, err := ToJSON(doc, pretty)
	if err != nil {
		return err
	}

	_, err = w.Write([]byte(jsonStr))
	return err
}

// Transform parsed structure into Document
func transform(f *file) *Document {
	doc := &Document{Tables: []Table{}}
	var currentTable *Table

	for _, line := range f.Lines {
		if line.TableHeader != nil {
			// Save previous table if exists
			if currentTable != nil {
				doc.Tables = append(doc.Tables, *currentTable)
			}
			// Start new table
			currentTable = &Table{
				Name:    line.TableHeader.Name,
				Columns: []Column{},
				Rows:    [][]any{},
			}
		} else if line.SchemaDef != nil && currentTable != nil {
			// Add columns to current table
			for _, col := range line.SchemaDef.Columns {
				currentTable.Columns = append(currentTable.Columns, Column{
					Name: col.Name,
					Type: formatType(&col),
				})
			}
		} else if line.DataRow != nil && currentTable != nil {
			// Add data row to current table
			row := make([]any, 0, len(line.DataRow.Fields))
			for _, field := range line.DataRow.Fields {
				row = append(row, cleanField(&field))
			}
			currentTable.Rows = append(currentTable.Rows, row)
		}
	}

	// Add last table
	if currentTable != nil {
		doc.Tables = append(doc.Tables, *currentTable)
	}

	return doc
}

// Format type definition into string representation
func formatType(col *columnDef) string {
	typeName := strings.ToLower(col.TypeName)
	typeStr := typeName

	// Handle parameterized types
	if len(col.Params) > 0 {
		switch typeName {
		case "decimal":
			if len(col.Params) >= 2 {
				typeStr = fmt.Sprintf("decimal(%s,%s)", col.Params[0], col.Params[1])
			}
		case "ref":
			if len(col.Params) >= 2 {
				typeStr = fmt.Sprintf("ref(%s.%s)", col.Params[0], col.Params[1])
			}
		case "enum":
			typeStr = fmt.Sprintf("enum(%s)", strings.Join(col.Params, " | "))
		}
	}

	if col.Array {
		typeStr += "[]"
	}
	if col.Nullable {
		typeStr += "?"
	}

	return typeStr
}

// Clean and convert field value
func cleanField(f *field) any {
	var value string

	if f.Quoted != nil {
		// Remove quotes and unescape doubled quotes
		value = *f.Quoted
		value = strings.TrimPrefix(value, "\"")
		value = strings.TrimSuffix(value, "\"")
		value = strings.ReplaceAll(value, "\"\"", "\"")
	} else if f.Unquoted != nil {
		value = strings.TrimSpace(*f.Unquoted)
	} else {
		return nil
	}

	// Empty or null
	if value == "" || strings.ToLower(value) == "null" {
		return nil
	}

	// Try boolean
	switch strings.ToLower(value) {
	case "true":
		return true
	case "false":
		return false
	}

	// Try number
	if num, err := strconv.ParseInt(value, 10, 64); err == nil {
		return num
	}
	if num, err := strconv.ParseFloat(value, 64); err == nil {
		return num
	}

	return value
}
