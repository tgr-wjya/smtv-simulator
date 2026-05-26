import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
import os


def generate_scenario_comparison(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate bar chart comparing damage across scenarios.

    Args:
        results: List of scenario results
        output_path: Path to save PNG file
    """
    if not results:
        print("No results to visualize")
        return

    scenario_names = [r['scenario_name'] for r in results]
    normal_damages = [r['damages']['normal'] for r in results]
    weakness_damages = [r['damages']['normal_weakness'] for r in results]
    crit_damages = [r['damages']['crit'] for r in results]
    crit_weakness_damages = [r['damages']['crit_weakness'] for r in results]
    percent_changes = [r['percent_change'] for r in results]

    x = np.arange(len(scenario_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot grouped bars
    rects1 = ax.bar(x - 1.5*width, normal_damages, width, label='Normal')
    rects2 = ax.bar(x - 0.5*width, weakness_damages, width, label='Weakness')
    rects3 = ax.bar(x + 0.5*width, crit_damages, width, label='Crit')
    rects4 = ax.bar(x + 1.5*width, crit_weakness_damages, width, label='Crit + Weakness')

    # Add percent change labels above normal damage bars
    for i, (rect, pct) in enumerate(zip(rects1, percent_changes)):
        height = rect.get_height()
        label = f"+{pct:.1f}%" if pct >= 0 else f"{pct:.1f}%"
        ax.text(rect.get_x() + rect.get_width()/2., height,
                label, ha='center', va='bottom', fontsize=8, rotation=45)

    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Damage', fontsize=12)
    ax.set_title('Damage Comparison Across Scenarios', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Scenario comparison chart saved to: {output_path}")
