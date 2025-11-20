#!/usr/bin/env node
/**
 * 3TL Parser CLI
 */

import { parseFile, toJSON } from './parser.js';

const args = process.argv.slice(2);

if (args.length === 0) {
  console.error('Usage: node src/cli.js <file.3tl> [--pretty]');
  process.exit(1);
}

const filepath = args[0];
const pretty = args.includes('--pretty');

try {
  const doc = parseFile(filepath);
  console.log(toJSON(doc, pretty));
  process.exit(0);
} catch (error) {
  console.error('Error:', error.message);
  process.exit(1);
}
