#!/usr/bin/env python3
"""
Run 3TL evaluation suite across different models

Usage:
    python run_evals.py --model gpt-4
    python run_evals.py --model claude-3-5-sonnet-20241022
    python run_evals.py --all-tasks
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from inspect_ai import eval
from three_tl_vs_csv import (
    type_inference_csv,
    type_reading_3tl,
    relationship_inference_csv,
    relationship_reading_3tl,
    schema_generation_comparison,
    data_validation_csv,
    data_validation_3tl,
    precision_understanding,
    multi_table_csv,
    multi_table_3tl,
    enum_understanding,
    three_tl_comprehension_suite,
)

# Load environment variables
load_dotenv()

# Available models
MODELS = {
    "gpt-4": "openai/gpt-4",
    "gpt-4-turbo": "openai/gpt-4-turbo-preview",
    "gpt-3.5": "openai/gpt-3.5-turbo",
    "claude-3-5-sonnet": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-opus": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet": "anthropic/claude-3-sonnet-20240229",
    "claude-3-haiku": "anthropic/claude-3-haiku-20240307",
}

# Task groups
TASK_GROUPS = {
    "type-inference": [type_inference_csv, type_reading_3tl],
    "relationships": [relationship_inference_csv, relationship_reading_3tl],
    "schema-generation": [schema_generation_comparison],
    "validation": [data_validation_csv, data_validation_3tl],
    "precision": [precision_understanding],
    "multi-table": [multi_table_csv, multi_table_3tl],
    "enums": [enum_understanding],
    "suite": [three_tl_comprehension_suite],
}

ALL_TASKS = [
    type_inference_csv,
    type_reading_3tl,
    relationship_inference_csv,
    relationship_reading_3tl,
    schema_generation_comparison,
    data_validation_csv,
    data_validation_3tl,
    precision_understanding,
    multi_table_csv,
    multi_table_3tl,
    enum_understanding,
]


def main():
    parser = argparse.ArgumentParser(
        description="Run 3TL vs CSV comprehension evaluations"
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default="gpt-4",
        help="Model to evaluate (default: gpt-4)",
    )
    parser.add_argument(
        "--task",
        choices=list(TASK_GROUPS.keys()),
        default="suite",
        help="Task group to run (default: suite)",
    )
    parser.add_argument(
        "--all-tasks",
        action="store_true",
        help="Run all individual tasks instead of just the suite",
    )
    parser.add_argument(
        "--log-dir",
        default="./logs",
        help="Directory for evaluation logs (default: ./logs)",
    )

    args = parser.parse_args()

    # Check for API keys
    if "openai" in MODELS[args.model] and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   Set it in .env file or as environment variable")
        return

    if "anthropic" in MODELS[args.model] and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment")
        print("   Set it in .env file or as environment variable")
        return

    model = MODELS[args.model]
    print(f"🚀 Running evaluations with {model}")
    print(f"📝 Logs will be saved to {args.log_dir}")
    print()

    # Determine which tasks to run
    if args.all_tasks:
        tasks = ALL_TASKS
        print(f"Running all {len(tasks)} individual tasks...")
    else:
        tasks = TASK_GROUPS[args.task]
        print(f"Running task group: {args.task} ({len(tasks)} tasks)")

    print()

    # Run evaluations
    for task_fn in tasks:
        task_name = task_fn.__name__
        print(f"Running: {task_name}")

        try:
            results = eval(
                task_fn(),
                model=model,
                log_dir=args.log_dir,
            )
            print(f"✅ {task_name} completed")
            print()
        except Exception as e:
            print(f"❌ {task_name} failed: {e}")
            print()

    print("✨ All evaluations complete!")
    print(f"📊 View results in {args.log_dir}")


if __name__ == "__main__":
    main()
