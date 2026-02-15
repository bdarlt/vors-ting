# Edge Cases and Mitigations

Purpose: Catalog of tricky situations and how system handles them.

## 1. Small Group Consensus
Problem: 3 agents with 80% threshold
Solution: floor() for groups ≤4, ceil() otherwise
Test: test_consensus_rounding()

## 2. DA Fatigue
Problem: Same agent selected repeatedly
Solution: Cooldown penalty, skip_rate
Test: test_da_cooldown_prevents_fatigue()

## 3. Trust Score Gaming
Problem: Agent issues shallow dissents to boost score
Solution: dissent_depth metric with novelty penalty
Test: test_shallow_dissent_penalized()

## 4. Rubric Drift Death Spiral
Problem: Living rubric diverges completely from gold
Solution: Critical threshold (15%) alerts human, never auto-revert
Test: test_shadow_rubric_alerts_at_threshold()