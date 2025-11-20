# 3TL Evaluations

LLM evaluations to test comprehension of 3TL format and demonstrate its advantages over plain CSV.

## Overview

This evaluation suite tests whether language models better understand structured data when presented in 3TL format versus traditional CSV. The evals demonstrate that 3TL provides:

1. **Explicit type information** - No inference needed
2. **Clear foreign key relationships** - Using `ref(Table.column)` syntax
3. **Multiple tables in one file** - Better organization
4. **Enum constraints** - Defined valid values
5. **Precision specifications** - e.g., `decimal(10,2)`
6. **Better validation** - Types declared upfront

## Setup

### 1. Install Dependencies

```bash
cd evals/
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Running Evaluations

### Quick Start

Run the comprehensive suite with GPT-4:

```bash
python run_evals.py --model gpt-4
```

Run with Claude:

```bash
python run_evals.py --model claude-3-5-sonnet
```

### Available Models

- `gpt-4` - OpenAI GPT-4
- `gpt-4-turbo` - OpenAI GPT-4 Turbo
- `gpt-3.5` - OpenAI GPT-3.5 Turbo
- `claude-3-5-sonnet` - Anthropic Claude 3.5 Sonnet
- `claude-3-opus` - Anthropic Claude 3 Opus
- `claude-3-sonnet` - Anthropic Claude 3 Sonnet
- `claude-3-haiku` - Anthropic Claude 3 Haiku

### Task Groups

Run specific evaluation categories:

```bash
# Type inference tasks
python run_evals.py --task type-inference --model gpt-4

# Relationship understanding tasks
python run_evals.py --task relationships --model claude-3-5-sonnet

# Schema generation comparison
python run_evals.py --task schema-generation --model gpt-4

# Data validation tasks
python run_evals.py --task validation --model gpt-4

# Precision understanding (decimal types)
python run_evals.py --task precision --model gpt-4

# Multi-table comprehension
python run_evals.py --task multi-table --model gpt-4

# Enum understanding
python run_evals.py --task enums --model gpt-4

# Full comparison suite (default)
python run_evals.py --task suite --model gpt-4
```

### Run All Tasks

```bash
python run_evals.py --all-tasks --model gpt-4
```

## Evaluation Tasks

### 1. Type Inference vs Type Reading

**CSV**: Tests if LLM can infer types from data
**3TL**: Tests if LLM can read explicit types from schema

Demonstrates: 3TL makes types explicit, no guessing needed.

### 2. Relationship Inference vs Reading

**CSV**: Tests if LLM can identify foreign keys by column naming conventions
**3TL**: Tests if LLM can read explicit `ref()` relationships

Demonstrates: 3TL makes relationships unambiguous.

### 3. Schema Generation

Compares quality of schemas when asked to design in CSV vs 3TL format.

Demonstrates: 3TL schemas are more precise and informative.

### 4. Data Validation

Tests if LLM can spot type mismatches in both formats.

Demonstrates: 3TL's explicit types make validation errors clearer.

### 5. Precision Understanding

Tests if LLM understands precision specifications like `decimal(10,2)`.

Demonstrates: 3TL supports precise numeric types (CSV doesn't).

### 6. Multi-Table Comprehension

Tests understanding of multiple related tables.

Demonstrates: 3TL can contain multiple tables in one file with clear boundaries.

### 7. Enum Understanding

Tests if LLM understands enum constraints.

Demonstrates: 3TL can define allowed values (CSV cannot).

### 8. Comprehensive Suite

Combined evaluation testing overall format comprehension.

Demonstrates: Overall superiority of 3TL for LLM-readable structured data.

## Evaluation Framework

This suite uses [Inspect AI](https://inspect.ai-safety-institute.org.uk/) by the UK AI Safety Institute:

- Multi-provider support (OpenAI, Anthropic, etc.)
- Reproducible evaluations
- Built-in scoring and logging
- Dataset management

## Results

Results are saved to `./logs/` by default. Each evaluation produces:

- JSON log with full results
- Scores for each task
- Model responses
- Pass/fail for each sample

View results:

```bash
# List all evaluation runs
ls -lt logs/

# View specific results (inspect provides CLI tools)
inspect view logs/
```

## Adding New Evaluations

Create new eval tasks in `three_tl_vs_csv.py`:

```python
@task
def my_new_eval():
    return Task(
        dataset=[
            Sample(
                input="Your prompt here",
                target="expected answer"
            ),
        ],
        solver=[generate()],
        scorer=includes(),  # or match() for exact matches
    )
```

Add to task groups in `run_evals.py`.

## Why This Matters

LLMs are increasingly used to generate, transform, and analyze structured data. When communicating data to LLMs:

- **CSV**: Forces LLMs to infer structure, types, relationships
- **3TL**: Makes everything explicit, reducing ambiguity

These evals demonstrate that 3TL's explicit structure leads to better LLM comprehension, which means:

- More accurate data processing
- Better code generation from schemas
- Fewer errors in data transformations
- Clearer communication between humans and LLMs

## License

Same as parent project (see main repository README).
