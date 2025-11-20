---
title: "3TL - Typed Talking To LLMs"
---

## What

CSV with types, foreign keys, and enums. Multiple tables in one file.

```
#! User
#@ id:uint, name:str, email:str, role:enum(admin|user), active:bool
1, Alice, alice@example.com, admin, true
2, Bob, bob@example.com, user, true

#! Order
#@ id:uint, user_id:ref(User.id), amount:decimal(10,2), status:enum(pending|shipped)
101, 1, 99.99, shipped
102, 2, 149.50, pending
```

Parse this without documentation. Types are clear. Foreign keys explicit. Enums defined.

## Why

CSV problems:
- Types inferred (is "123" a string or number?)
- Booleans inconsistent (true/1/yes all valid)
- Precision lost (can't distinguish 0.05 from 0.050)
- Dates ambiguous (01/02/03 is which date?)
- No enum validation
- Foreign keys unclear
- Arrays non-standard

3TL fixes these with explicit declarations.

## Results

Evaluated with Claude 3 Haiku, 3.5 Haiku, and Opus:
- **95% accuracy** (Claude 3.5 Haiku, Opus)
- **+2% tokens** at 100 rows (+$0.00004 per request)
- **100% zero-shot understanding** (no docs needed)
- **75% identified CSV ambiguities** (type confusion, boolean inconsistency, date parsing)

Token overhead decreases with data size:
- 3 rows: +54%
- 100 rows: +2%
- 1000 rows: +0.2%

Schema overhead is fixed. Amortizes over data.

## Parsers

Available in Python, JavaScript, Clojure, and Go. All produce identical JSON output.

See [GitHub](https://github.com/Flexiana/3TL) for implementation details.
