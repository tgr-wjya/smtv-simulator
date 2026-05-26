from dataclasses import dataclass, field
from typing import Dict


# Buff multiplier constants (used by both Combatant and CombatEngine)
BUFF_MULTIPLIERS = {
    -3: 0.6,
    -2: 0.7,
    -1: 0.85,
    0: 1.0,
    1: 1.2,
    2: 1.4,
    3: 1.6
}


@dataclass
class Combatant:
    """Represents an entity in combat with stats and buff state"""
    name: str
    base_stats: Dict[str, int]
    buff_levels: Dict[str, int] = field(default_factory=lambda: {
        'STR': 0, 'VIT': 0, 'MAG': 0, 'AGI': 0, 'LUC': 0
    })

    def get_effective_stat(self, stat: str) -> float:
        """Calculate effective stat value with buff multiplier applied"""
        base_value = self.base_stats[stat]
        buff_level = self.buff_levels[stat]
        multiplier = BUFF_MULTIPLIERS[buff_level]
        return base_value * multiplier
