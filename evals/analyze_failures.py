#!/usr/bin/env python3
"""Analyze failed eval cases"""
import json
import glob
import os
from pathlib import Path

log_dir = Path("./logs")
log_files = sorted(log_dir.glob("*.eval"), key=os.path.getmtime, reverse=True)[:12]

print("Analyzing recent eval failures...\n")

for log_file in log_files:
    with open(log_file) as f:
        data = json.load(f)

    task = data['eval']['task']
    accuracy = data['results']['scores'][0]['metrics']['accuracy']['value']

    if accuracy < 1.0:  # Has failures
        print(f"{'='*80}")
        print(f"Task: {task}")
        print(f"Accuracy: {accuracy:.1%}")
        print(f"{'='*80}\n")

        for sample in data['samples']:
            score = sample.get('scores', [{}])[0].get('value', {})

            # Check if failed (works for both 'includes' and 'match' scorers)
            passed = score.get('includes', score.get('match', True))

            if not passed:
                print(f"❌ Sample {sample['id']}:")
                print(f"Input: {sample['input'][:300]}...")
                print(f"Expected: {sample['target']}")
                print(f"Got: {sample['output']['completion']}")
                print()
