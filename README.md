# Life Simulation

A sophisticated artificial life simulation inspired by Biblical's YouTube channel, featuring chemistry-based metabolism, energy cycling, neural network brains, sensory systems, and genetic inheritance.

## Overview

This simulation models artificial life forms with:
- **Chemistry-based metabolism**: 7 base elements (A-G) that form molecules with energy values
- **Energy cycling**: Multiple energy types (chemical, thermal, kinetic, electrical, light) that transform between forms
- **Environmental interaction**: Organisms absorb/secrete chemicals, exchange energy with environment
- **Neural network brains**: Configurable neural networks controlling behavior
- **Sensory systems**: Vision, sound, and chemical senses with genetic sensitivity modulation
- **Genetic inheritance**: Trait transmission with mutation capabilities
- **Dynamic world**: Spatial grid with chemical distributions, temperature, and light fields

## Core Systems

### 1. Chemistry System (`chemistry.py`)
- **Elements**: A, B, C, D, E, F, G (Enum-based)
- **Molecules**: Combinations of elements with calculated energy content
- **Reactions**: Chemical transformations with energy changes (exothermic/endothermic)
- **Energy Tracking**: Reactions release/absorb thermal and chemical energy

### 2. Energy System (`energy.py`)
- **Energy Types**: CHEMICAL, THERMAL, KINETIC, ELECTRICAL, LIGHT
- **EnergyAccount**: Tracks reserves, production, consumption for each type
- **Transformations**: Converters between energy types with efficiency factors
- **Metabolic Costs**: Calculates energy needs for biological processes
- **Environmental Exchange**: Heat transfer, light absorption

### 3. Organism System (`organism.py`)
- **Physical Properties**: Position, mass, size, age
- **Energy Management**: Integrated EnergyAccount for metabolic processes
- **Internal Storage**: Chemical inventory for biochemical processes
- **Phenotypic Traits**: 
  - Insulation (thermal retention)
  - Mobility (movement efficiency)
  - Metabolic Efficiency (energy utilization)
- **Metabolism**: 
  - Aging and lifespan limits
  - Basal metabolic rate (temperature-dependent)
  - Internal chemical processing
  - Environmental energy exchange
- **Behavior**:
  - Movement with energy cost calculation
  - Chemical absorption from environment
  - Chemical secretion to environment
  - Life/death cycles

### 4. 4. World/Environment System (`world.py`)
- **Spatial Grid**: 3D dictionary-based storage for efficiency
- **Environmental Fields**:
  - Temperature distribution (with gradients)
  - Light intensity (day/night cycles)
  - Chemical concentrations (per molecule type)
  - Energy accounts (per grid position)
- **Chemical Reactions**: 
  - Probabilistic reaction execution based on concentrations
  - Temperature and light dependence
  - Energy exchange with environment

### 5. Configuration System (`config.py`)
- **Hierarchical Parameters**: Nested configuration for all subsystems
- **Dot Notation Access**: Easy configuration access (`config.get('chemistry.reaction_rate')`)
- **Persistence**: JSON save/load functionality
- **Default Values**: Sensible defaults for all parameters

### 6. Main Simulation Loop (`main.py`)
- **World Initialization**: Creates environment with gradients
- **Population Seeding**: Generates initial organisms with configured traits
- **Update Cycle**: 
  - World processes (light cycles, etc.)
  - Organism updates (metabolism, behavior, etc.)
  - Statistical reporting
- **Configurable Parameters**: Steps, time step, verbosity

## Current Implementation Status

### ✅ Completed Core Systems:
- Chemistry System (elements, molecules, reactions, energy tracking)
- Energy System (multiple energy types, transformations, accounting)
- Configuration System (parameter management)
- World/Environment System (spatial grid, fields, reactions)
- Organism System (metabolism, energy management, chemical exchange)
- Main Simulation Loop (coordination, reporting)

### 🔧 Needs Repair (File Corruption Issues):
Two files have corruption from interrupted edits that need fixing:

1. **organism.py** - Two corrupted sections:
   - Phenotypic traits initialization (lines ~37-43): Commented out incorrectly
   - Chemical absorption method (lines ~225-230): Mixed code/comment artifacts

2. **world.py** - Corrupted reaction method:
   - `update_chemical_reactions()` method contains explanatory comments mixed with code
   - Needs cleanup to functional implementation

### 📋 Planned Future Systems (Not Yet Implemented):
- **Neural Network Brain System** (Tasks #4, #11): Configurable neural networks for behavior control
- **Sensory System Components** (Tasks #5, #13): Vision, hearing, chemical senses with genetic modulation
- **Genetic Inheritance System** (Tasks #6, #12): Trait transmission, mutation, evolution
- **Utility Functions Module** (Task #17): Mathematical helpers, data structures

## Files Overview

```
├── chemistry.py      # Element/molecule/reaction system
├── energy.py         # Energy accounting and transformations
├── config.py         # Configuration management
├── world.py          # Environmental simulation
├── organism.py       # Organism biology and behavior
├── main.py           # Simulation entry point and loop
├── README.md         # This file
├── LICENSE           # MIT License
├── test_*.py         # Chemistry system tests
└── utils/            # Utility functions (to be implemented)
    ├── brain.py      # Neural network implementation (planned)
    ├── sensors.py    # Sensory system implementation (planned)
    └── action.py     # Action/motor system (planned)
```

## Getting Started

### Prerequisites
- Python 3.6+
- No external dependencies (uses only standard library)

### Running the Simulation

```bash
# Clone or download this repository
cd lifesim

# Run the demonstration simulation
python3 main.py
```

The simulation will:
1. Create a world with temperature/light gradients
2. Spawn an initial population of organisms
3. Run for a configurable number of steps (default: 200)
4. Report population statistics periodically
5. Show final simulation report

### Configuration

Modify `config.py` to adjust:
- World size and environmental properties
- Chemical initial concentrations
- Organism traits and energy parameters
- Simulation duration and time step
- Logging frequency

## Design Principles

### 1. Energy-First Philosophy
All biological processes consume or produce energy. Nothing happens for free.

### 2. Chemistry-Driven Metabolism
Organisms are chemical machines - their behaviors emerge from molecular interactions.

### 3. Emergent Complexity
Complex behaviors arise from simple rules governing chemistry, energy, and interaction.

### 4. Parameter-Driven Behavior
All aspects are configurable through the configuration system, enabling experimentation.

## Energy Flow Example

1. **Environmental Reactions**: Chemicals react, releasing thermal energy
2. **Organism Absorption**: Organisms absorb chemicals from environment
3. **Metabolic Processing**: Internal chemical reactions produce energy
4. **Energy Use**: Powers movement, maintenance, reproduction
5. **Environmental Exchange**: Waste heat/chemicals returned to environment
6. **Cycle Continues**: Environmental chemistry

## Customization

### Adding New Elements
1. Add to `Element` enum in `chemistry.py`
2. Define properties in config if needed
3. System automatically handles new molecule combinations

### Modifying Reaction Rules
1. Edit `ChemicalSystem.get_possible_reactions()` in `chemistry.py`
2. Adjust energy yields in `ChemicalReaction` calculations
3. Modify temperature/light sensitivity in `ChemicalSystem`

### Changing Organism Behavior
1. Adjust phenotypic traits in `config.py` under `organism`
2. Modify metabolic calculations in `organism.py`
3. Alter movement costs or sensory ranges

## Future Development Roadmap

### Phase 1: Core Stability (Current)
- Fix file corruptions in organism.py and world.py
- Stabilize core simulation loop
- Add basic statistics and visualization

### Phase 2: Neural Intelligence 
- Implement neural network brain in `brain.py`
- Connect sensory inputs to neural network outputs
- Enable learned behaviors through simple reinforcement

### Phase 3: Sensory Richness
- Implement vision system (light detection)
- Implement chemical sensing (gradient following)
- Implement audio/vibration sensing
- Genetic modulation of sensory sensitivity

### Phase 4: Evolutionary Dynamics
- Implement genetic inheritance with mutation
- Natural selection through differential reproduction
- Speciation and adaptation observation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure core simulation still runs
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Inspired by the artificial life simulations and concepts presented on Biblical's YouTube channel.
Special thanks to the open-source artificial life community for foundational concepts.