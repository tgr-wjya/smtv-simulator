from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Combatant:
    """Represents an entity in combat with stats and buff state"""
    name: str
    base_stats: Dict[str, int]
    buff_levels: Dict[str, int] = field(default_factory=lambda: {
        'STR': 0, 'VIT': 0, 'MAG': 0, 'AGI': 0, 'LUC': 0
    })
