#!/usr/bin/env python3
"""Analyze eval results to show 3TL vs CSV comparison"""

results = {
    # CSV tasks
    "type_inference_csv": {"accuracy": 1.0, "samples": 2, "tokens": 214},
    "relationship_inference_csv": {"accuracy": 1.0, "samples": 1, "tokens": 169},
    "data_validation_csv": {"accuracy": 1.0, "samples": 1, "tokens": 210},
    "multi_table_csv": {"accuracy": 1.0, "samples": 1, "tokens": 147},
    
    # 3TL tasks
    "type_reading_3tl": {"accuracy": 1.0, "samples": 3, "tokens": 426},
    "relationship_reading_3tl": {"accuracy": 1.0, "samples": 2, "tokens": 400},
    "data_validation_3tl": {"accuracy": 1.0, "samples": 1, "tokens": 208},
    "multi_table_3tl": {"accuracy": 1.0, "samples": 2, "tokens": 493},
    
    # 3TL-only features
    "enum_understanding": {"accuracy": 1.0, "samples": 2, "tokens": 417},
    "precision_understanding": {"accuracy": 0.5, "samples": 2, "tokens": 508},
    
    # Comparison
    "schema_generation_comparison": {"accuracy": 0.5, "samples": 2, "tokens": 583},
}

print("=" * 80)
print("3TL vs CSV Evaluation Results (Claude 3 Haiku)")
print("=" * 80)
print()

# CSV tasks
csv_total_samples = 5
csv_total_correct = 5
csv_total_tokens = 740
csv_accuracy = csv_total_correct / csv_total_samples

print("📊 CSV Format Tasks:")
print(f"  Accuracy: {csv_accuracy:.1%} ({csv_total_correct}/{csv_total_samples})")
print(f"  Total tokens: {csv_total_tokens}")
print(f"  Avg tokens/sample: {csv_total_tokens/csv_total_samples:.1f}")
print()

# 3TL tasks (comparable to CSV)
ttl_total_samples = 8
ttl_total_correct = 8
ttl_total_tokens = 1527
ttl_accuracy = ttl_total_correct / ttl_total_samples

print("📊 3TL Format Tasks (comparable):")
print(f"  Accuracy: {ttl_accuracy:.1%} ({ttl_total_correct}/{ttl_total_samples})")
print(f"  Total tokens: {ttl_total_tokens}")
print(f"  Avg tokens/sample: {ttl_total_tokens/ttl_total_samples:.1f}")
print()

# 3TL-only features
ttl_only_samples = 4
ttl_only_correct = 3  # enum=2/2, precision=1/2
ttl_only_tokens = 925

print("📊 3TL-Only Features (enum, precision):")
print(f"  Accuracy: {ttl_only_correct/ttl_only_samples:.1%} ({ttl_only_correct}/{ttl_only_samples})")
print(f"  Total tokens: {ttl_only_tokens}")
print(f"  Avg tokens/sample: {ttl_only_tokens/ttl_only_samples:.1f}")
print()

print("=" * 80)
print("KEY FINDINGS:")
print("=" * 80)
print()
print("✅ Both CSV and 3TL achieved 100% accuracy on comparable tasks")
print("   - This shows Claude Haiku can understand both formats well")
print()
print("✅ 3TL enables features CSV cannot express:")
print("   - Enum constraints: 100% accuracy (2/2)")
print("   - Precision specs: 50% accuracy (1/2)")
print()
print("⚠️  Token usage is higher for 3TL:")
print(f"   - CSV: {csv_total_tokens/csv_total_samples:.1f} tokens/sample")
print(f"   - 3TL: {ttl_total_tokens/ttl_total_samples:.1f} tokens/sample")
print(f"   - Overhead: +{((ttl_total_tokens/ttl_total_samples)/(csv_total_tokens/csv_total_samples)-1)*100:.1f}%")
print()
print("💡 VALUE PROPOSITION:")
print("   - 3TL doesn't improve accuracy on basic tasks (both 100%)")
print("   - 3TL ADDS capabilities CSV lacks (enums, precision, refs)")
print("   - Token overhead: ~29% more (acceptable for added features)")
print("   - Best for: complex schemas where explicit types matter")
print()

