/**
 * 3TL Parser Tests
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseString, toJSON } from '../src/parser.js';

test('parse basic table', () => {
  const input = `#! User
#@ id:uint, name:str, email:str
1, Alice, alice@example.com
2, Bob, bob@example.com
`;

  const doc = parseString(input);

  assert.equal(doc.tables.length, 1);

  const table = doc.tables[0];
  assert.equal(table.name, 'User');
  assert.equal(table.columns.length, 3);
  assert.equal(table.rows.length, 2);

  assert.equal(table.columns[0].name, 'id');
  assert.equal(table.columns[0].type, 'uint');
  assert.equal(table.columns[1].name, 'name');
  assert.equal(table.columns[1].type, 'str');

  assert.equal(table.rows[0][0], 1);
  assert.equal(table.rows[0][1], 'Alice');
  assert.equal(table.rows[1][0], 2);
  assert.equal(table.rows[1][1], 'Bob');
});

test('parse nullable type', () => {
  const input = `#! Article
#@ id:uint, title:str, content:str?
1, Hello, This is content
2, World,
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.columns[2].type, 'str?');
  assert.equal(table.rows[1][2], null);
});

test('parse array type', () => {
  const input = `#! Test
#@ id:uint, tags:str[]
1, tag1
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.columns[1].type, 'str[]');
});

test('parse decimal type', () => {
  const input = `#! Product
#@ id:uint, price:decimal(10,2)
1, 19.99
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.columns[1].type, 'decimal(10,2)');
  assert.equal(table.rows[0][1], 19.99);
});

test('parse ref type', () => {
  const input = `#! Comment
#@ id:uint, article_id:ref(Article.id)
1, 42
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.columns[1].type, 'ref(Article.id)');
  assert.equal(table.rows[0][1], 42);
});

test('parse enum type', () => {
  const input = `#! Task
#@ id:uint, status:enum(pending|in_progress|completed)
1, pending
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.match(table.columns[1].type, /enum\(/);
  assert.ok(table.columns[1].type.includes('pending'));
  assert.ok(table.columns[1].type.includes('in_progress'));
  assert.ok(table.columns[1].type.includes('completed'));
  assert.equal(table.rows[0][1], 'pending');
});

test('parse multiple tables', () => {
  const input = `#! User
#@ id:uint, name:str
1, Alice

#! Post
#@ id:uint, user_id:ref(User.id), title:str
1, 1, My First Post
`;

  const doc = parseString(input);

  assert.equal(doc.tables.length, 2);
  assert.equal(doc.tables[0].name, 'User');
  assert.equal(doc.tables[1].name, 'Post');
  assert.equal(doc.tables[1].columns.length, 3);
});

test('ignore comments', () => {
  const input = `# This is a comment
#! User
# Another comment
#@ id:uint, name:str
# Yet another comment
1, Alice
`;

  const doc = parseString(input);

  assert.equal(doc.tables.length, 1);
  assert.equal(doc.tables[0].rows.length, 1);
});

test('parse quoted fields', () => {
  const input = `#! Article
#@ id:uint, title:str, content:str
1, "Hello, World", "This is a test"
2, Normal, "With ""quotes"" inside"
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.rows[0][1], 'Hello, World');
  assert.equal(table.rows[0][2], 'This is a test');
  assert.equal(table.rows[1][2], 'With "quotes" inside');
});

test('case-insensitive types', () => {
  const input = `#! Test
#@ id:UINT, name:STR, active:BOOL
1, Alice, true
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.columns[0].type, 'uint');
  assert.equal(table.columns[1].type, 'str');
  assert.equal(table.columns[2].type, 'bool');
  assert.equal(table.rows[0][2], true);
});

test('unicode identifiers', () => {
  const input = `#! Café
#@ id:uint, nombre:str
1, José
`;

  const doc = parseString(input);
  const table = doc.tables[0];

  assert.equal(table.name, 'Café');
  assert.equal(table.columns[1].name, 'nombre');
  assert.equal(table.rows[0][1], 'José');
});

test('to JSON', () => {
  const input = `#! User
#@ id:uint, name:str
1, Alice
`;

  const doc = parseString(input);
  const json = toJSON(doc);

  assert.ok(typeof json === 'string');
  assert.ok(json.includes('User'));
  assert.ok(json.includes('Alice'));
  assert.ok(json.includes('tables'));
});
