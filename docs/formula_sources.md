# SMTV Formula Sources

Accessed: 2026-05-27

## Damage Formula (STR / VIT)

- https://megamitensei.fandom.com/wiki/Shin_Megami_Tensei_V/Battle_Mechanics
- Notes: Community documentation of SMTV battle mechanics, including physical damage structure.

## Buff / Debuff Multipliers

- https://gamefaqs.gamespot.com/switch/315041-shin-megami-tensei-v/faqs/79611
- Notes: Community guide documenting -3..+3 stage multipliers.

## Critical Rate Behavior

- Source type: community testing and gameplay analysis.
- Implemented formula in simulator: `5% + (attacker_LUC - defender_LUC) × 0.2%`, clamped to [0%, 100%].

## Weakness and Crit Multipliers

- Source type: in-game observation plus community references.
- Default values in simulator configs: weakness = 1.5, crit = 1.5.
