# Testing Notes

## Framework Validation

✅ **Structure Test** (no API calls required):
```bash
source .venv/bin/activate
python test_structure.py
```

Results: All 12 tasks valid with 23 total samples

## Model Requirements

To run actual evaluations, your API key needs to be enabled for model access.

### Anthropic API Key Setup

1. Go to https://console.anthropic.com/settings/keys
2. Ensure your key has API access enabled (not just console access)
3. Verify model access is available

Common models to test:
- `claude-3-5-sonnet-20241022` (latest)
- `claude-3-5-sonnet-20240620` (stable)
- `claude-3-sonnet-20240229` (Claude 3)
- `claude-3-haiku-20240307` (fast/cheap)

### Testing API Access

```bash
python3 -c "
import anthropic
import os
client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
message = client.messages.create(
    model='claude-3-haiku-20240307',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Hi'}]
)
print('✓ API access working')
"
```

If you get 404 errors, your API key may not have model access enabled yet.

## Running Evals

Once API access is configured:

```bash
# Simple test
python run_evals.py --model claude-3-5-sonnet --task type-inference

# Full suite
python run_evals.py --model claude-3-5-sonnet --task suite

# All tasks
python run_evals.py --model claude-3-5-sonnet --all-tasks
```

## Expected Results

The eval suite demonstrates that 3TL provides better LLM comprehension than CSV:

1. **Type Reading**: Models can directly read types instead of inferring
2. **Relationships**: `ref()` syntax makes foreign keys explicit
3. **Enums**: Valid values are defined in schema
4. **Precision**: `decimal(10,2)` specifies exact constraints
5. **Validation**: Type errors are easier to spot with explicit types

Results will be saved to `./logs/` with detailed scoring.
