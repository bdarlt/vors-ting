
Purpose: Complete reference for all config options

```yaml
# Example section
convergence:
  method: "consensus"  # or "similarity", "hybrid"
  threshold: 0.8       # 0.0-1.0
  small_group_handling:
    strategy: "floor"  # floor/ceil/unanimous_under
    unanimous_threshold: 5
```

Include:

    All config sections with descriptions

    Default values

    Example configurations for common use cases

    Validation rules)