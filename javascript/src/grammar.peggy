/*
 * 3TL Grammar for Peggy (PEG.js)
 *
 * Parses 3TL (Typed Talking To LLMs) format
 */

ThreeTLFile
  = (LineBreak / Element)* {
      return {
        tables: options.tables || []
      };
    }

Element
  = CommentLine
  / TableBlock

// Comments
CommentLine
  = "#" ![@!] [^\n]* LineBreak { return null; }

// Table Structure
TableBlock
  = header:TableHeader body:(SchemaDefLine / CommentLine / DataRow)* {
      const schema = body.find(item => item?.type === 'schema');
      const rows = body.filter(item => item?.type === 'row').map(item => item.data);

      const table = {
        name: header,
        columns: schema?.columns || [],
        rows: rows
      };

      options.tables = options.tables || [];
      options.tables.push(table);

      return table;
    }

TableHeader
  = "#!" WS? name:Identifier WS? LineBreak { return name; }

SchemaDefLine
  = "#@" WS? columns:ColDefs WS? LineBreak {
      return { type: 'schema', columns };
    }

ColDefs
  = first:ColDef rest:(WS? "," WS? ColDef)* {
      return [first, ...rest.map(r => r[3])];
    }

ColDef
  = name:Identifier WS? ":" WS? type:TypeExpr {
      return { name, type: options.formatType(type) };
    }

// Identifiers (Unicode support)
Identifier
  = start:IdentifierStart cont:IdentifierContinue* {
      return start + cont.join('');
    }

IdentifierStart
  = [a-zA-Z_\u00C0-\u024F\u1E00-\u1EFF\u0400-\u04FF\u0370-\u03FF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]

IdentifierContinue
  = [a-zA-Z0-9_\u00C0-\u024F\u1E00-\u1EFF\u0400-\u04FF\u0370-\u03FF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]

// Type Expressions
TypeExpr
  = base:BaseType modifier:TypeModifier? {
      return { base, modifier };
    }

TypeModifier
  = (ArraySuffix NullableSuffix) { return { array: true, nullable: true }; }
  / (NullableSuffix ArraySuffix) { return { nullable: true, array: true }; }
  / ArraySuffix { return { array: true }; }
  / NullableSuffix { return { nullable: true }; }

ArraySuffix = "[" "]"
NullableSuffix = "?"

BaseType
  = IntegerType
  / FloatType
  / DecimalType
  / BoolType
  / TextType
  / TimeType
  / RefType
  / EnumType

// Base Types (case-insensitive)
IntegerType
  = val:$("i8"i / "i16"i / "i32"i / "i64"i / "int"i / "u8"i / "u16"i / "u32"i / "u64"i / "uint"i) {
      return { type: val.toLowerCase() };
    }

FloatType
  = val:$("f32"i / "f64"i / "float"i) {
      return { type: val.toLowerCase() };
    }

BoolType
  = "bool"i { return { type: 'bool' }; }

TextType
  = val:$("str"i / "text"i) {
      return { type: val.toLowerCase() };
    }

TimeType
  = val:$("datetime"i / "timestamp"i / "date"i / "time"i) {
      return { type: val.toLowerCase() };
    }

DecimalType
  = "decimal"i WS? "(" WS? precision:$([0-9]+) WS? "," WS? scale:$([0-9]+) WS? ")" {
      return {
        type: 'decimal',
        precision: parseInt(precision),
        scale: parseInt(scale)
      };
    }

RefType
  = "ref"i WS? "(" WS? table:Identifier "." column:Identifier WS? ")" {
      return {
        type: 'ref',
        table,
        column
      };
    }

EnumType
  = "enum"i WS? "(" WS? values:EnumValues WS? ")" {
      return {
        type: 'enum',
        values
      };
    }

EnumValues
  = first:Identifier rest:(WS? "|" WS? Identifier)* {
      return [first, ...rest.map(r => r[3])];
    }

// Data Rows
DataRow
  = fields:FieldList LineBreak {
      return {
        type: 'row',
        data: fields.map(f => options.cleanField(f))
      };
    }

FieldList
  = first:Field rest:("," Field)* {
      return [first, ...rest.map(r => r[1])];
    }

Field
  = WS? field:(QuotedField / UnquotedField)? WS? {
      return field ?? '';
    }

QuotedField
  = '"' chars:QuotedChar* '"' {
      return chars.join('').replace(/""/g, '"');
    }

QuotedChar
  = '""' { return '""'; }
  / [^"]

UnquotedField
  = chars:$([^#",\r\n][^",\r\n]*) { return chars; }
  / chars:$([0-9][^",\r\n]*) { return chars; }

// Whitespace and Line Breaks
WS = [ \t]+
LineBreak = "\r"? "\n"
