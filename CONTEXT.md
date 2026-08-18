# Life Simulation Project Context

## Overview
This document captures the current state of the life simulation project as of 2026-06-24, to allow continuation of work at a later time.

## Project Description
Artificial life simulation inspired by Biblical's YouTube channel featuring:
- Chemistry-based metabolism with 7 base elements (A-G)
- Multi-type energy cycling (chemical, thermal, kinetic, electrical, light)
- Environmental interaction and feedback loops
- Planned neural network brains, sensory systems, and genetic inheritance

## ✅ Completed Systems

### 1. Chemistry System (`chemistry.py`)
- Elements A-G implemented as Enum
- Molecule class with composition tracking and energy calculation
- ChemicalReaction tracking energy changes
- ChemicalSystem for reaction discovery and application
- Proper energy tracking: reactions release/absorb thermal/chemical energy
- Fixed Enum hash issue by sorting by .value
- Energy integration with environment accounts

### 2. Energy System (`energy.py`)
- EnergyType enum: CHEMICAL, THERMAL, KINETIC, ELECTRICAL, LIGHT
- EnergyAccount class with proper get/add/use/transfer methods
- EnergyTransformer for cross-type conversions (efficiencies implemented)
- MetabolicCosts for biological process energy calculations
- EnvironmentalEnergyExchange for heat/light transfer
- Critical fix: Added `apply_chemical_reaction_energy()` method
- Fixed "reservses" typos throughout (corrected to "reserves")

### 3. Configuration System (`config.py`)
- ConfigManager with nested dictionary storage
- Dot notation get()/set() methods
- JSON load/save functionality
- Default configurations for all subsystems
- Convenience functions for subsystem access

### 4. World/Environment System (`world.py`) - PARTIALLY COMPLETE
- 3D sparse grid using dictionaries keyed by (x,y,z) tuples
- Storage for: temperature, light intensity, chemical concentrations, energy accounts
- get/set methods for all environmental properties
- **Issue**: `update_chemical_reactions()` method corrupted (needs repair)
- Default initialization with temperature gradients and chemical distribution

### 5. Organism System (`organism.py`) - PARTIALLY COMPLETE
- Organism class with position, mass, size, age
- Integrated EnergyAccount for metabolic processes
- Internal chemical storage and genetic placeholder
- Phenotypic traits: insulation, mobility, metabolic efficiency
- **Issue**: Two sections corrupted (need repair):
  1. Phenotypic traits initialization (lines ~37-43): commented out incorrectly
  2. Chemical absorption method (lines ~225-230): mixed code/comment artifacts
- Metabolism: aging, BMR calculation, internal processing, energy exchange
- Movement with energy cost calculation
- Chemical absorption/secretion with environment
- Death handling: releases internal chemicals to environment
- Global organism management (add_organism, get_organisms, update_organisms)

### 6. Main Simulation Loop (`main.py`)
- World initialization with environmental gradients
- Initial population creation with configured traits
- Update cycle: world processes → organism updates
- Light/day-night cycle simulation
- Progress reporting and final statistics
- Configurable parameters (steps, time step, verbosity)

## 🔧 Known Issues Requiring Repair

### File Corruptions (Prevent Execution)

#### organism.py
1. **Lines 37-43: Phenotypic Traits**
   ```python
   # CURRENT STATE (CORRUPTED):
   # Phenotypic traits (expressed characteristics)
   # self._tri
   # Finally.
   # traits
   # self.insulation = 0.5  # Thermal insulation (0-1)
   # self.mobility = 0.5   # Movement capability (0-1)
   # self.metabolic_efficiency = 0.5  # How efficiently energy is used
   
   # SHOULD BE:
   # Phenotypic traits (expressed characteristics)
   self.insulation = 0.5  # Thermal insulation (0-1)
   self.mobility = 0.5   # Movement capability (0-1)
   self.metabolic_efficiency = 0.5  # How efficiently energy is used
   ```

2. **Lines 225-230: absorb_chemicals() Method**
   ```python
   # CURRENT STATE (CORRUPTED):
   # Check each chemical at this position
   # pos = (nx, ny, nz)
   # if pos in world.chemical_concentrations:
   #     for molecule, concentration in list(result: dict[Molecule, float] = {}
   # for dx in range(-radius, radius + 1):
   #     for dy in range(-radius, radius + 1):
   
   # SHOULD BE:
   # Check each chemical at this position
   # pos = (nx, ny, nz)
   # if pos in world.chemical_concentrations:
   #     for molecule, concentration in world.chemical_concentrations[pos].items():
   ```

#### world.py
- **update_chemical_reactions() method**: Contains explanatory comments mixed with code, showing evidence of incomplete rewrite attempts
- Needs cleanup to functional implementation that:
  1. Identifies possible reactions based on present molecules
  2. Calculates reaction probability based on concentrations, temperature, light
  3. Executes reactions probabilistically
  4. Transfers energy to/from the environment's energy account
  5. Updates chemical concentrations appropriately

## 📋 Planned Future Systems (Not Implemented)

Based on original task list:
- **Task #4, #11**: Neural network brain system with configurable architecture
- **Task #5, #13**: Sensory system components (vision, sound, chemical) with genetic sensitivity modulation
- **Task #6, #12**: Genetic inheritance system for trait transmission and mutation
- **Task #17**: Utility functions and helper modules

## 📂 Current File Status

```
├── chemistry.py      # ✅ COMPLETE - Chemistry/molecule/reaction system
├── energy.py         # ✅ COMPLETE - Energy accounting and transformations
├── config.py         # ✅ COMPLETE - Configuration management
├── world.py          # ⚠️ PARTIAL - Environmental simulation (corrupted reaction method)
├── organism.py       # ⚠️ PARTIAL - Organism biology and behavior (two corruption sections)
├── main.py           # ✅ COMPLETE - Simulation entry point and loop
├── README.md         # ✅ COMPLETE - Project documentation
├── LICENSE           # ✅ COMPLETE - MIT License
├── test_*.py         # ✅ COMPLETE - Chemistry system tests
└── utils/            # 📋 EMPTY - Utility functions (to be implemented)
    ├── brain.py      # 📋 PLANNED - Neural network implementation
    ├── sensors.py    # 📋 PLANNED - Sensory system implementation
    └── action.py     # 📋 PLANNED - Action/motor system
```

## 🔬 Verification Completed

1. **Chemistry Tests**: All tests pass (element validation, molecule energy, reaction balancing, application, temperature/light sensitivity)
2. **Import Verification**: Core modules import successfully (chemistry, energy, config)
3. **Integration Points Verified**:
   - Chemical reactions → EnergyAccount updates (via `apply_chemical_reaction_energy`)
   - Organism ↔ Environment chemical exchange (absorption/secretion)
   - Organism energy metabolism ↔ Environmental heat exchange
   - World light cycles → Organism light-dependent processes
   - Configuration-driven parameterization across systems

## 🚀 Next Steps for Continuation

### Immediate Priority (Fix Corruptions):
1. Repair organism.py phenotypic traits initialization (uncomment lines 37-43)
2. Repair organism.py absorb_chemicals() method (fix lines 225-230)
3. Repair world.py update_chemical_reactions() method (clean up commentary, implement functional version)

### Verification After Fixes:
1. Run `python3 main.py` to verify simulation starts and runs
2. Observe initialization output: world creation, population spawning
3. Monitor simulation for: chemical reactions, organism metabolism, energy flows
4. Check periodic statistics reporting
5. Review final simulation report

### After Core Stabilization:
1. Implement planned systems in order:
   - Neural network brain (`utils/brain.py`)
   - Sensory system (`utils/sensors.py`)
   - Genetic inheritance (extend organism.py or create new module)
   - Utility functions (`utils/` module)
2. Enhance reporting and visualization
3. Add more sophisticated behaviors and interactions

## 💡 Key Technical Details

### Energy Flow
1. Environmental chemical reactions release/absorb thermal energy
2. Organisms absorb chemicals from environment
3. Internal metabolic processes convert chemical to usable energy
4. Energy powers movement, maintenance, reproduction
5. Waste heat/chemicals returned to environment
6. Continuous cycle maintains system dynamism

### Metabolic Calculations
- Basal Metabolic Rate: BMR = 0.1 × mass^0.75 × 2^((temp-20)/10)
- Temperature correction follows Q10 rule (~doubling every 10°C)
- Movement cost: kinetic energy + work against friction + acceleration cost
- Thermoregulation: based on heat transfer equations Q = h × A × ΔT × t

### Reaction System
- Probabilistic execution based on reactant concentrations
- Temperature and light affecting reaction likelihood
- Energy transfer: reaction products affect environment's energy accounts
- Concentration thresholds prevent negligible reactions

## 📝 Notes for Future Work

### When Implementing Neural Systems:
- Consider connecting sensory inputs to neural network outputs
- Simple reinforcement learning for behavior modification
- Configurable architecture (layers, neurons, activation functions)

### When Implementing Sensory Systems:
- Vision: light detection with resolution and sensitivity
- Chemical sensing: gradient following for chemo-taxis
- Audio/vibration: pressure wave detection
- Genetic modulation: traits affecting sensory thresholds and sensitivity

### When Implementing Genetics:
- DNA-inspired representation of traits
- Mutation mechanisms (point mutations, insertions, deletions)
- Inheritance with crossover and mutation
- Fitness-based selection tying to energy/energy efficiency

## 📁 Repository State
- Branch: master
- No staged changes
- Modified files: chemistry.py, config.py, main.py, organism.py, world.py (these are the ones we've been working on)
- Untracked files: __pycache__/, energy.py (duplicate?), test_chemistry.py, test_chemistry_updated.py
- Note: energy.py appears both as modified and untracked - likely due to editing history

---
*This context file created to preserve work state and enable continuation. Last updated: 2026-06-24*