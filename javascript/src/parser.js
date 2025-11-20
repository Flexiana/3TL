/**
 * 3TL Parser - Parses 3TL files into JavaScript objects
 */

import peggy from 'peggy';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load and compile the grammar
const grammarSource = readFileSync(join(__dirname, 'grammar.peggy'), 'utf-8');

// Helper functions for the grammar
const helpers = {
  formatType(typeInfo) {
    const { base, modifier } = typeInfo;
    let typeStr;

    if (base.type === 'decimal') {
      typeStr = `decimal(${base.precision},${base.scale})`;
    } else if (base.type === 'ref') {
      typeStr = `ref(${base.table}.${base.column})`;
    } else if (base.type === 'enum') {
      typeStr = `enum(${base.values.join(' | ')})`;
    } else {
      typeStr = base.type;
    }

    if (modifier?.array) typeStr += '[]';
    if (modifier?.nullable) typeStr += '?';

    return typeStr;
  },

  cleanField(value) {
    if (value === '' || value === null || value === undefined) {
      return null;
    }

    const trimmed = value.trim();

    if (trimmed === '' || trimmed.toLowerCase() === 'null') {
      return null;
    }

    // Try boolean
    if (/^(true|false)$/i.test(trimmed)) {
      return trimmed.toLowerCase() === 'true';
    }

    // Try number
    if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
      return trimmed.includes('.') ? parseFloat(trimmed) : parseInt(trimmed);
    }

    return trimmed;
  }
};

const parser = peggy.generate(grammarSource, {
  allowedStartRules: ['ThreeTLFile'],
  grammarSource: 'grammar.peggy'
});

/**
 * Parse a 3TL string
 * @param {string} input - 3TL formatted string
 * @returns {Object} Parsed document with tables
 */
export function parseString(input) {
  const options = {
    tables: [],
    ...helpers
  };

  parser.parse(input, options);

  return {
    tables: options.tables
  };
}

/**
 * Parse a 3TL file
 * @param {string} filepath - Path to 3TL file
 * @returns {Object} Parsed document with tables
 */
export function parseFile(filepath) {
  const content = readFileSync(filepath, 'utf-8');
  return parseString(content);
}

/**
 * Convert document to JSON
 * @param {Object} doc - Parsed document
 * @param {boolean} pretty - Pretty print
 * @returns {string} JSON string
 */
export function toJSON(doc, pretty = false) {
  return JSON.stringify(doc, null, pretty ? 2 : 0);
}

export default {
  parseString,
  parseFile,
  toJSON
};
