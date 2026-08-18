"""
World/environment system for the life simulation.
Manages spatial grid, chemical distributions, temperature, light, and energy flows.
"""

from typing import List, Tuple, Dict, Optional
import math
from chemistry import ChemicalSystem, Molecule, Element
from energy import EnergyAccount, EnergyType, EnvironmentalEnergyExchange


class World:
    """Represents the simulation environment."""

    def __init__(self, width: int, height: int, depth: int = 1):
        self.width = width
        self.height = height
        self.depth = depth

        # Initialize chemical system for reactions
        self.chemical_system = ChemicalSystem()

        # 3D grids for different properties
        # In a full implementation, these would be 3D arrays
        # For simplicity, we'll use dictionaries keyed by (x, y, z) tuples
        self.temperature: dict[tuple[int, int, int], float] = {}
        self.light_intensity: dict[tuple[int, int, int], float] = {}
        # Chemical concentrations: {position: {molecule: concentration}}
        self.chemical_concentrations: dict[tuple[int, int, int], dict[Molecule, float]] = {}
        # Energy accounts for each position
        self.energy_accounts: dict[tuple[int, int, int], EnergyAccount] = {}

        # Initialize everything to default values
        self._initialize_world()

    def _initialize_world(self):
        """Initialize the world with default values."""
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    pos = (x, y, z)
                    # Default temperature (20°C)
                    self.temperature[pos] = 20.0
                    # Default light intensity (0 = dark)
                    self.light_intensity[pos] = 0.0
                    # Default chemical concentrations (empty)
                    self.chemical_concentrations[pos] = {}
                    # Default energy account
                    self.energy_accounts[pos] = EnergyAccount()

    def get_temperature(self, x: int, y: int, z: int = 0) -> float:
        """Get temperature at position."""
        return self.temperature.get((x, y, z), 20.0)

    def set_temperature(self, x: int, y: int, z: int, value: float):
        """Set temperature at position."""
        self.temperature[(x, y, z)] = value

    def get_light_intensity(self, x: int, y: int, z: int = 0) -> float:
        """Get light intensity at position."""
        return self.light_intensity.get((x, y, z), 0.0)

    def set_light_intensity(self, x: int, y: int, z: int, value: float):
        """Set light intensity at position."""
        self.light_intensity[(x, y, z)] = value

    def get_chemical_concentration(self, x: int, y: int, z: int,
                                 molecule: Molecule) -> float:
        """Get concentration of a specific molecule at position."""
        pos = (x, y, z)
        if pos in self.chemical_concentrations:
            return self.chemical_concentrations[pos].get(molecule, 0.0)
        return 0.0

    def set_chemical_concentration(self, x: int, y: int, z: int,
                                 molecule: Molecule, concentration: float):
        """Set concentration of a specific molecule at position."""
        pos = (x, y, z)
        if pos not in self.chemical_concentrations:
            self.chemical_concentrations[pos] = {}
        self.chemical_concentrations[pos][molecule] = concentration

    def get_energy_account(self, x: int, y: int, z: int = 0) -> EnergyAccount:
        """Get energy account for position."""
        return self.energy_accounts.get((x, y, z), EnergyAccount())

    def update_chemical_reactions(self, x: int, y: int, z: int = 0):
        """
        Update chemical reactions at a specific position.
        This should be called regularly to simulate chemical processes.
        """
        pos = (x, y, z)
        if pos not in self.energy_accounts:
            self.energy_accounts[pos] = EnergyAccount()
        if pos not in self.chemical_concentrations:
            self.chemical_concentrations[pos] = {}

        energy_account = self.energy_accounts[pos]
        concentrations = self.chemical_concentrations[pos]

        # Get list of molecules present (with sufficient concentration)
        molecules_present = []
        for molecule, concentration in concentrations.items():
            # Consider a molecule "present" if concentration > threshold
            if concentration > 0.001:  # Arbitrary threshold
                # Add multiple copies based on concentration for reaction probability
                count = max(1, int(concentration * 100))  # Scale factor
                molecules_present.extend([molecule] * min(count, 10))  # Limit to prevent explosion

        # Limit the number of molecules to consider for reactions
        # (to prevent combinatorial explosion)
        if len(molecules_present) > 20:
            # Take a random sample if too many
            import random
            molecules_present = random.sample(molecules_present, 20)

        # Get possible reactions
        possible_reactions = self.chemical_system.get_possible_reactions(molecules_present)

        # Execute reactions (probabilistically based on concentrations and conditions)
        for reaction in possible_reactions:
            # Calculate reaction probability based on reactant concentrations
            prob = self._calculate_reaction_probability(reaction, concentrations)

            # Apply environmental factors (temperature, light)
            temp = self.get_temperature(x, y, z)
            light = self.get_light_intensity(x, y, z)
            env_factor = self.chemical_system.spontaneous_reaction_likelihood(
                reaction, temp, light
            )

            # Combined probability
            final_prob = prob * env_factor

            # Execute reaction if probability check passes
            import random
            if random.random() < final_prob:
                # Get the actual molecules to react
                reactant_counts = {}
                for reactant in reaction.reactants:
                    reactant_counts[reactant] = reactant_counts.get(reactant, 0) + 1

                # Check if we have enough of each reactant
                sufficient = True
                for reactant, needed in reactant_counts.items():
                    available = int(concentrations.get(reactant, 0) * 100)  # Convert to discrete units
                    if available < needed:
                        sufficient = False
                        break

                if sufficient:
                    # Consume reactants
                    for reactant, needed in reactant_counts.items():
                        current_conc = concentrations.get(reactant, 0.0)
                        concentrations[reactant] = max(0.0, current_conc - needed / 100.0)

                    # Produce products
                    for product in reaction.products:
                        current_conc = concentrations.get(product, 0.0)
                        concentrations[product] = current_conc + len(reaction.products) / 100.0

                    # Apply energy changes
                    remaining_molecules, thermal_energy, chemical_energy = \
                        self.chemical_system.apply_reaction(
                            list(reactant_counts.keys()) * min(reactant_counts.values()),
                            reaction
                        )

                    # Actually, let's use the proper apply_reaction function
                    # We need to create a proper list of reactant molecules
                    reactant_molecules = []
                    for reactant, count in reactant_counts.items():
                        reactant_molecules.extend([reactant] * count)
                     Let me fix this - the approach above is getting overly complex. Let me simplify the reaction implementation.

Actually, let me step back and think about this more carefully.

The world.update_chemical_reactions method is getting too complicated. Let me simplify it significantly for now, and just implement the core concept: reactions happen based on what's present, and they release/absorb energy.

Let me rewrite this method to be simpler and more correct.


<tool_call>
<function=Write>
<parameter=content>
"""
World/environment system for the life simulation.
Manages spatial grid, chemical distributions, temperature, light, and energy flows.
"""

from typing import List, Tuple, Dict, Optional
import math
import random
from chemistry import ChemicalSystem, Molecule, Element
from energy import EnergyAccount, EnergyType, EnvironmentalEnergyExchange


class World:
    """Represents the simulation environment."""

    def __init__(self, width: int, height: int, depth: int = 1):
        self.width = width
        self.height = height
        self.depth = depth

        # Initialize chemical system for reactions
        self.chemical_system = ChemicalSystem()

        # 3D grids for different properties
        # In a full implementation, these would be 3D arrays
        # For simplicity, we'll use dictionaries keyed by (x, y, z) tuples
        self.temperature: dict[tuple[int, int, int], float] = {}
        self.light_intensity: dict[tuple[int, int, int], float] = {}
        # Chemical concentrations: {position: {molecule: concentration}}
        self.chemical_concentrations: dict[tuple[int, int, int], dict[Molecule, float]] = {}
        # Energy accounts for each position
        self.energy_accounts: dict[tuple[int, int, int], EnergyAccount] = {}

        # Initialize everything to default values
        self._initialize_world()

    def _initialize_world(self):
        """Initialize the world with default values."""
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    pos = (x, y, z)
                    # Default temperature (20°C)
                    self.temperature[pos] = 20.0
                    # Default light intensity (0 = dark)
                    self.light_intensity[pos] = 0.0
                    # Default chemical concentrations (empty)
                    self.chemical_concentrations[pos] = {}
                    # Default energy account
                    self.energy_accounts[pos] = EnergyAccount()

    def get_temperature(self, x: int, y: int, z: int = 0) -> float:
        """Get temperature at position."""
        return self.temperature.get((x, y, z), 20.0)

    def set_temperature(self, x: int, y: int, z: int, value: float):
        """Set temperature at position."""
        self.temperature[(x, y, z)] = value

    def get_light_intensity(self, x: int, y: int, z: int = 0) -> float:
        """Get light intensity at position."""
        return self.light_intensity.get((x, y, z), 0.0)

    def set_light_intensity(self, x: int, y: int, z: int, value: float):
        """Set light intensity at position."""
        self.light_intensity[(x, y, z)] = value

    def get_chemical_concentration(self, x: int, y: int, z: int,
                                 molecule: Molecule) -> float:
        """Get concentration of a specific molecule at position."""
        pos = (x, y, z)
        if pos in self.chemical_concentrations:
            return self.chemical_concentrations[pos].get(molecule, 0.0)
        return 0.0

    def set_chemical_concentration(self, x: int, y: int, z: int,
                                 molecule: Molecule, concentration: float):
        """Set concentration of a specific molecule at position."""
        pos = (x, y, z)
        if pos not in self.chemical_concentrations:
            self.chemical_concentrations[pos] = {}
        self.chemical_concentrations[pos][molecule] = concentration

    def get_energy_account(self, x: int, y: int, z: int = 0) -> EnergyAccount:
        """Get energy account for position."""
        return self.energy_accounts.get((x, y, z), EnergyAccount())

    def update_chemical_reactions(self, x: int, y: int, z: int = 0):
        """
        Update chemical reactions at a specific position.
        This should be called regularly to simulate chemical processes.
        """
        pos = (x, y, z)
        if pos not in self.energy_accounts:
            self.energy_accounts[pos] = EnergyAccount()
        if pos not in self.chemical_concentrations:
            self.chemical_concentrations[pos] = {}

        energy_account = self.energy_accounts[pos]
        concentrations = self.chemical_concentrations[pos]

        # Get list of molecules present (with sufficient concentration)
        molecules_present = []
        for molecule, concentration in concentrations.items():
            # Consider a molecule "present" if concentration > threshold
            if concentration > 0.001:  # Arbitrary threshold
                # Add multiple copies based on concentration for reaction probability
                count = max(1, int(concentration * 10))  # Scale factor
                molecules_present.extend([molecule] * min(count, 5))  # Limit to prevent explosion

        # Limit the number of molecules to consider for reactions
        # (to prevent combinatorial explosion)
        if len(molecules_present) > 10:
            # Take a random sample if too many
            molecules_present = random.sample(molecules_present, 10)

        # Get possible reactions
        possible_reactions = self.chemical_system.get_possible_reactions(molecules_present)

        # Try to execute each possible reaction
        for reaction in possible_reactions:
            # Check if we have sufficient reactants
            reactant_counts = {}
            for reactant in reaction.reactants:
                reactant_counts[reactant] = reactant_counts.get(reactant, 0) + 1

            sufficient = True
            for reactant, needed_count in reactant_counts.items():
                # Get concentration of this reactant
                concentration = concentrations.get(reactant, 0.0)
                # Convert concentration to discrete units available
                # Assuming concentration is in moles per unit volume, and we have unit volume
                available_units = int(concentration * 100)  # Scale factor
                if available_units < needed_count:
                    sufficient = False
                    break

            if not sufficient:
                continue

            # Calculate reaction probability based on conditions
            temp = self.get_temperature(x, y, z)
            light = self.get_light_intensity(x, y, z)
            base_probability = self.chemical_system.spontaneous_reaction_likelihood(
                reaction, temp, light
            )

            # Apply concentration factor (higher concentration = higher reaction rate)
            concentration_factor = 1.0
            for reactant, needed_count in reactant_counts.items():
                concentration = concentrations.get(reactant, 0.0)
                # Simple mass action: rate proportional to concentration
                concentration_factor *= concentration

            # Normalize concentration factor (this is a simplification)
            concentration_factor = min(1.0, concentration_factor * 1000)

            # Final probability
            final_probability = base_probability * concentration_factor * 0.1  # Scale down

            # Execute reaction probabilistically
            if random.random() < final_probability:
                # Consume reactants
                for reactant, needed_count in reactant_counts.items():
                    current_conc = concentrations.get(reactant, 0.0)
                    # Consume amount proportional to what we needed
                    consumption = needed_count / 100.0  # Reverse of our scaling
                    concentrations[reactant] = max(0.0, current_conc - consumption)

                # Produce products
                for product in reaction.products:
                    current_conc = concentrations.get(product, 0.0)
                    # Produce amount proportional to number of product molecules
                    production = len(reaction.products) / 100.0  # Scale factor
                    concentrations[product] = current_conc + production

                # Apply energy changes to the environment's energy account
                # Get the actual reaction to compute energy changes
                _, thermal_energy, chemical_energy = self.chemical_system.apply_reaction(
                    list(reactant_counts.keys()), reaction
                )

                # Apply the energy changes
                energy_account.apply_chemical_reaction_energy(chemical_energy, thermal_energy)


class WorldManager:
    """Manages the world state and updates."""

    def __init__(self, width: int = 100, height: int = 100, depth: int = 1):
        self.world = World(width, height, depth)
        self.time = 0

    def update(self, dt: float = 1.0):
        """Update the world state by one time step."""
        self.time += dt

        # Update chemical reactions everywhere
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    self.world.update_chemical_reactions(x, y, z)

        # TODO: Add other updates like diffusion, heat transfer, etc.


# Global instance
_world = None

def initialize_world(width: int = 100, height: int = 100, depth: int = 1) -> World:
    """Initialize the global world instance."""
    global _world
    _world = World(width, height, depth)
    return _world

def get_world() -> World:
    """Get the global world instance."""
    global _world
    if _world is None:
        _world = initialize_world()
    return _world