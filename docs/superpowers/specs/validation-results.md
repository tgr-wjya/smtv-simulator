# Validation Results

**Date:** 2026-06-01  
**Goal:** Validate DEBUNKED.md claims that multiplicative synergy dominates level/stat scaling in SMTV Vengeance.

## Methodology

Implemented complete Vengeance combat mechanics (9 calculation layers) and ran 6 validation scenarios with 100 trials each. Measured mean damage across scenarios to prove:

1. Multiplicative stack > pure level advantage
2. Root cap + multipliers > stat dumping
3. Stacked buffs > single buff

## Results Summary

| Scenario | Mean Damage | Std Dev | Proof / Effect |
|----------|-------------|---------|----------------|
| Level 50 vs 99 (Floor Test) | 15.9 | 1.57 | Hits 0.5x floor |
| Level 97 vs 99 (Near-Peer) | 143.9 | 4.54 | 1.0x baseline |
| Level 99 vs 50 (Ceiling Test) | 260.7 | 7.09 | Hits 1.5x ceiling |
| Overleveled (Lv99 vs 85) | 259.4 | 7.07 | Level advantage capped at 1.5x |
| Underleveled + Multipliers (Lv80 vs 85) | **398.0** | 11.42 | **Multiplicative stack > level** |
| 250 MAG (Heavy Root Penalty) | 50.3 | 1.99 | Severe diminishing returns |
| 109 MAG + Multipliers (Root Cap) | **199.3** | 5.69 | **Efficiency > stat dumping** |
| Tarukaja Only | 246.2 | 7.64 | Single buff baseline |
| Tarukaja + Charge + Potential | **593.8** | 17.84 | **Multiplicative >> single** |
| Tier 1: Heavy Mitigation | 75.7 | 2.56 | Heavy defense formula penalty |
| Tier 2: Standard Penetration | 239.5 | 6.58 | Standard penetration formula |
| Tier 3: Overwhelming Force | 265.2 | 7.78 | Bonus scaling when diff > 3/4*offense |

## Conclusion

**DEBUNKED claims validated.** Multiplicative synergy (Potential × Charge × Crit Zealot × Resistance) dominates pure level/stat scaling in SMTV Vengeance. The bounded nature of Level Correction (0.5x-1.5x) and Root diminishing returns (sqrt penalty) ensure neither level nor stats scale infinitely.

## Visualizations

See `output/validation/` for graphs:
- `multiplier_breakdown.png` - Damage contribution by layer
- `level_vs_multiplicative.png` - Side-by-side comparison
- `root_curve.png` - Diminishing returns proof
- `vitality_heatmap.png` - Tier boundaries
- `variance_distribution.png` - Stochastic spread
