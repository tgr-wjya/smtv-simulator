# SMTV Vengeance GUI Implementation Plan

**Goal:** Implement a responsive, modern desktop GUI for SMTV Vengeance damage simulation to allow custom Nahobino designing and live damage calculations.

---

## Task 1: Update requirements.txt
- [ ] Add `customtkinter` dependency to `requirements.txt`.
- [ ] Install dependency: `pip install -r requirements.txt`.

---

## Task 2: Create GUI Skeleton (`src/gui.py`)
- [ ] Add CustomTkinter imports and basic app class window setting:
  ```python
  import customtkinter as ctk
  import matplotlib.pyplot as plt
  from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
  ```
- [ ] Set up theme and dark mode:
  ```python
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("blue")
  ```
- [ ] Define the responsive three-column grid layout inside the main `App` class.

---

## Task 3: Implement Left Panel (Nahobino Designer)
- [ ] Create layout frame for Attacker inputs.
- [ ] Implement Level slider (1-99) with active label indicator.
- [ ] Implement raw stat sliders / spinboxes for STR, MAG, and LUC.
- [ ] Add Skill Element dropdown (`Phys, Fire, Ice, Elec, Wind, Light, Dark, Force, Magic`).
- [ ] Add Skill Power dropdown (Light [30], Medium [70], Heavy [120], Severe [200]).
- [ ] Add Skill Potential slider/spinner (-9 to +9).
- [ ] Add Charge state radio buttons (None, Charge, Concentrate, Impaler's Glory).
- [ ] Add passive ability checkboxes (Critical Zealot, Murderous Glee).

---

## Task 4: Implement Middle Panel (Target & Buffs Designer)
- [ ] Create layout frame for Defender inputs.
- [ ] Implement Defender Level slider (1-99) with active label indicator.
- [ ] Implement VIT raw stat spinner/slider.
- [ ] Add Resistance dropdown (immune, drain, repel, resist, neutral, weak).
- [ ] Add Guarding checkbox.
- [ ] Add Doubler Bug Active checkbox.
- [ ] Implement Attacker STR Buff slider (-3 to +3).
- [ ] Implement Defender VIT Debuff slider (-3 to +3).

---

## Task 5: Implement Right Panel Results Grid
- [ ] Create layout frame for damage cards.
- [ ] Design three distinct results cards with colored background panels:
  - Normal Hit Card (standard gray/blue).
  - Critical Hit Card (orange/red accent).
  - Expected Damage Card (green accent).
- [ ] Add labels for large-format numerical output values.

---

## Task 6: Integrate Matplotlib Canvas
- [ ] Add empty Matplotlib figure inside the right panel frame.
- [ ] Bind using `FigureCanvasTkAgg` to allow drawing inside the CustomTkinter frame layout.

---

## Task 7: Build Data Hookups & Live Callback Logic
- [ ] Write the core `update_simulation()` callback method.
- [ ] Connect all inputs (sliders, checkboxes, radio selections, dropdowns) to trigger `update_simulation()` on change.
- [ ] Inside callback:
  - Instantiate `Combatant` for attacker using current left panel inputs.
  - Instantiate `Combatant` for defender using middle panel inputs.
  - Instantiate `CombatEngine` with active skill power.
  - Calculate damages using `calculate_vengeance_damage()`.
  - Update Right Panel result card texts.
  - Compute damage outputs across Attacker STR Buff range (-3 to +3).
  - Re-plot and draw the Matplotlib progressive damage line chart.

---

## Task 8: Update CLI Runner (`src/runner.py`)
- [ ] Modify `src/runner.py` parser to accept a `--gui` flag.
- [ ] In `main()`, check `args.gui`. If true, import `src.gui` and launch the CustomTkinter loop.

---

## Task 9: Verification
- [ ] Run verification tests.
- [ ] Start UI: `python -m src.runner --gui`.
- [ ] Drag sliders and verify instant updates of cards and graphs.
