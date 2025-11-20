#!/usr/bin/env python3
"""
Test that eval tasks are correctly structured (without calling APIs)
"""

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

def test_task(task_fn):
    """Test that a task function creates a valid Task"""
    task = task_fn()
    assert task is not None, f"{task_fn.__name__} returned None"
    assert hasattr(task, 'dataset'), f"{task_fn.__name__} missing dataset"
    assert len(task.dataset) > 0, f"{task_fn.__name__} has empty dataset"

    # Check each sample
    for i, sample in enumerate(task.dataset):
        assert hasattr(sample, 'input'), f"{task_fn.__name__} sample {i} missing input"
        assert hasattr(sample, 'target'), f"{task_fn.__name__} sample {i} missing target"
        assert sample.input, f"{task_fn.__name__} sample {i} has empty input"
        assert sample.target, f"{task_fn.__name__} sample {i} has empty target"

    return len(task.dataset)

def main():
    tasks = [
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
    ]

    print("Testing eval task structure...\n")

    total_samples = 0
    for task_fn in tasks:
        try:
            num_samples = test_task(task_fn)
            total_samples += num_samples
            print(f"✓ {task_fn.__name__:<35} ({num_samples} samples)")
        except AssertionError as e:
            print(f"✗ {task_fn.__name__:<35} FAILED: {e}")
            return 1
        except Exception as e:
            print(f"✗ {task_fn.__name__:<35} ERROR: {e}")
            return 1

    print(f"\n✅ All {len(tasks)} tasks valid ({total_samples} total samples)")
    print("\nTo run evals, set API keys and use:")
    print("  python run_evals.py --model claude-3-5-sonnet")
    print("  python run_evals.py --model gpt-4")
    return 0

if __name__ == "__main__":
    exit(main())
