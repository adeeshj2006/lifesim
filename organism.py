"""
Organism class for the life simulation.
Represents individual living entities with metabolism, genetics, and behavior.
"""

from typing import List, Dict, Optional, Tuple
import math
from chemistry import ChemicalSystem, Molecule, Element
from energy import EnergyAccount, EnergyType
from world import get_world


class Organism:
    """Represents a single organism in the simulation."""

    def __init__(self, x: int, y: int, z: int = 0):
        self.x = x
        self.y = y
        self.z = z
        self.world = get_world()

        # Physical properties
        self.mass = 1.0  # Arbitrary mass units
        self.size = 0.5  # Radius in grid units
        self.age = 0.0
        self.max_age = 100.0  # Maximum lifespan

        # Energy accounting
        self.energy = EnergyAccount()

        # Chemical inventory (internal)
        self.internal_chemicals: dict[Molecule, float] = {}

        # Genetic information (simplified)
        self.genome = {}  # Would contain genes for proteins, etc.

        # Phenotypic traits (expressed characteristics)
        self._tri
Finally.
        traits
        self.insulation = 0.5  # Thermal insulation (0-1)
        self.mobility = 0.5   # Movement capability (0-1)
        self.metabolic_efficiency = 0.5  # How efficiently energy is used

        # Initialize with some starting energy and chemicals
        self._initialize_organism()

    def _initialize_organism(self):
        """Set up the initial state of the organism."""
        # Start with some basic energy reserves
        self.energy.add_energy(EnergyType.CHEMICAL, 10.0)  # Starting chemical energy
        self.energy.add_energy(EnergyType.THERMAL, 5.0)    # Starting thermal energy

        # Start with some basic building blocks
        world = self.world
        # Absorb some basic elements from environment
        for element in [Element.A, Element.B, Element.C]:
            mol = Molecule({element: 1})
            conc = world.get_chemical_concentration(self.x, self.y, self.z, mol)
            if conc > 0:
                # Take some from environment
                amount = min(0.1, conc * 0.1)  # Take 10% or up to 0.1 units
                self.internal_chemicals[mol] = self.internal_chemicals.get(mol, 0.0) + amount
                # Decrease environmental concentration
                current = world.get_chemical_concentration(self.x, self.y, self.z, mol)
                world.set_chemical_concentration(self.x, self.y, self.z, mol, max(0, current - amount))

    def get_energy(self, energy_type: EnergyType) -> float:
        """Get available energy of a specific type."""
        return self.energy.get_energy(energy_type)

    def use_energy(self, energy_type: EnergyType, amount: float) -> bool:
        """Use energy from reserves. Returns True if successful."""
        return self.energy.use_energy(energy_type, amount)

    def get_mass(self) -> float:
        """Get the organism's mass."""
        return self.mass

    def update_metabolism(self, dt: float = 1.0):
        """Update metabolic processes."""
        # Age the organism
        self.age += dt

        # Check for death from old age
        if self.age >= self.max_age:
            self.die()
            return

        # Get environmental conditions
        world = self.world
        temp = world.get_temperature(self.x, self.y, self.z)
        light = world.get_light_intensity(self.x, self.y, self.z)

        # Basal metabolic rate (energy needed just to stay alive)
        bmr = self._calculate_basal_metabolic_rate(temp)
        if not self.use_energy(EnergyType.CHEMICAL, bmr * dt):
            # Not enough energy - start taking damage
            self._apply_damage(bmr * dt * 0.1)  # Damage proportional to energy deficit

        # Process internal chemical reactions (metabolism)
        self._process_internal_metabolism(dt)

        # Exchange energy with environment
        self._exchange_environmental_energy(dt)

        # Check if organism should die from lack of energy
        if self.energy.get_energy(EnergyType.CHEMICAL) <= 0.1:
            self.die()

    def _calculate_basal_metabolic_rate(self, temperature: float) -> float:
        """Calculate basal metabolic rate based on mass and temperature."""
        # Simplified metabolic scaling
        base_bmr = 0.1 * (self.mass ** 0.75)
        # Temperature correction (Q10 ~ 2)
        temp_factor = 2.0 ** ((temperature - 20.0) / 10.0)
        return base_bmr * temp_factor * self.metabolic_efficiency

    def _process_internal_metabolism(self, dt: float = 1.0):
        """Process internal chemical reactions (simplified metabolism)."""
        # In a full implementation, this would involve enzymatic reactions
        # For now, we'll do some simple glucose-like breakdown for energy

        # Simple model: convert some stored chemical energy to usable energy
        # This represents processes like glycolysis, Krebs cycle, etc.
        stored_energy = self.energy.get_energy(EnergyType.CHEMICAL)
        if stored_energy > 1.0:  # Only if we have sufficient reserves
            # Convert some stored energy to thermal (representing metabolic heat)
            conversion_rate = 0.01 * dt  # 1% per time unit
            amount_to_convert = stored_energy * conversion_rate
            if self.use_energy(EnergyType.CHEMICAL, amount_to_convert):
                self.energy.add_energy(EnergyType.THERMAL, amount_to_convert * 0.8)  # 80% efficiency

    def _exchange_environmental_energy(self, t: float = 1.0):
        """Exchange energy with the environment."""
        world = self.world
        pos = (self.x, self.y, self.z)
        energy_account = world.get_energy_account(self.x, self.y, self.z)

        # Heat exchange with environment
        internal_temp = self._estimate_body_temperature()
        external_temp = world.get_temperature(self.x, self.y, self.z)

        # Simple Newton's law of cooling
        temp_diff = internal_temp - external_temp
        heat_transfer_coeff = 0.1 * (1.0 - self.insulation)  # Better insulation = less transfer
        heat_exchange = heat_transfer_coeff * abs(temp_diff) * t

        if temp_diff > 0:  # We're hotter than environment
            # We lose heat to environment
            if self.use_energy(EnergyType.THERMAL, heat_exchange * 0.5):  # Only portion is usable thermal energy
                # Heat goes to environment
                env_energy = world.get_energy_account(self.x, self.y, self.z)
                env_energy.add_energy(EnergyType.THERMAL, heat_exchange * 0.5)
        elif temp_diff < 0:  # We're colder than environment
            # We gain heat from environment
            env_energy = world.get_energy_account(self.x, self.y, self.z)
            if env_energy.use_energy(EnergyType.THERMAL, heat_exchange * 0.5):
                self.energy.add_energy(EnergyType.THERMAL, heat_exchange * 0.5)

    def _estimate_body_temperature(self) -> float:
        """Estimate the organism's body temperature based on thermal energy."""
        # Very simplified: temperature proportional to thermal energy per unit mass
        thermal_energy = self.energy.get_energy(EnergyType.THERMAL)
        # Base temperature plus thermal energy contribution
        base_temp = 20.0  # Baseline
        temp_rise = thermal_energy / (self.mass * 0.1)  # Specific heat approximation
        return base_temp + temp_rise

    def move(self, dx: int, dy: int, dz: int = 0) -> bool:
        """
        Attempt to move the organism by the given offset.
        Returns True if successful, False if blocked or insufficient energy.
        """
        new_x = self.x + dx
        new_y = self.y + dy
        new_z = self.z + dz

        # Check bounds
        world = self.world
        if not (0 <= new_x < world.width and 0 <= new_y < world.height and 0 <= new_z < world.depth):
            return False

        # Calculate energy cost for movement
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        speed = 1.0  # Assume unit speed for simplicity
        energy_cost = self._calculate_movement_cost(distance, speed)

        # Check if we have enough energy
        if not self.use_energy(EnergyType.CHEMICAL, energy_cost):
            return False

        # Update position
        self.x, self.y, self.z = new_x, new_y, new_z
        return True

    def _calculate_movement_cost(self, distance: float, speed: float) -> float:
        """Calculate energy cost for movement."""
        # Simplified: kinetic energy + work against friction
        ke = 0.5 * self.mass * (speed ** 2)
        # Friction work: proportional to distance and weight
        friction_work = self.mass * 9.8 * 0.1 * distance  # Assuming some friction coefficient
        return (ke + friction_work) * (1.0 - self.mobility * 0.5)  # Better mobility = less cost

    def absorb_chemicals(self, radius: int = 1) -> dict[Molecule, float]:
        """
        Absorb chemicals from the surrounding environment.
        Returns dictionary of what was absorbed.
        """
        world = self.world
        absorbed = {}

        # Check surrounding area
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue  # Skip self position

                    nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
                    if not (0 <= nx < world.width and 0 <= ny < world.height and 0 <= nz < world.depth):
                        continue

                    # Check each chemical at this position
                    pos = (nx, ny, nz)
                    if pos in world.chemical_concentrations:
                        for molecule, concentration in list(result: dict[Molecule, float] = {}
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue

                    nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
                    if not (0 <= nx < world.width and 0 <= ny < world.height and 0 <= nz < world.depth):
                        continue

                    pos = (nx, ny, nz)
                    if pos in world.chemical_concentrations:
                        for molecule, concentration in list(world.chemical_concentrations[pos].items()):
                            if concentration > 0.001:  # Only absorb if significant concentration
                                # Amount absorbed depends on surface area and concentration gradient
                                internal_conc = self.internal_chemicals.get(molecule, 0.0)
                                # Simple diffusion: move from high to low concentration
                                if concentration > internal_conc:
                                    absorb_amount = min(
                                        concentration * 0.1,  # Don't take too much at once
                                        (concentration - internal_conc) * 0.5
                                    )
                                    if absorb_amount > 0.001:
                                        # Update internal stores
                                        self.internal_chemicals[molecule] = self.internal_chemicals.get(molecule, 0.0) + absorb_amount
                                        # Decrease environmental concentration
                                        new_conc = concentration - absorb_amount
                                        if new_conc <= 0.001:
                                            del world.chemical_concentrations[pos][molecule]
                                        else:
                                            world.chemical_concentrations[pos][molecule] = new_conc
                                        absorbed[molecule] = absorbed.get(molecule, 0.0) + absorb_amount
        return absorbed

    def secrete_chemicals(self, molecule: Molecule, amount: float) -> bool:
        """
        Secrete a chemical into the environment.
        Returns True if successful.
        """
        # Check if we have enough of this chemical internally
        available = self.internal_chemicals.get(molecule, 0.0)
        if available < amount:
            return False

        # Decrease internal stores
        self.internal_chemicals[molecule] = available - amount
        if self.internal_chemicals[molecule] < 0.001:
            del self.internal_chemicals[molecule]

        # Increase environmental concentration
        world = self.world
        current_conc = world.get_chemical_concentration(self.x, self.y, self.z, molecule)
        new_conc = current_conc + amount
        world.set_chemical_concentration(self.x, self.y, self.z, molecule, new_conc)

        return True

    def die(self):
        """Handle organism death."""
        # Release internal chemicals back to environment
        world = self.world
        for molecule, amount in list(self.internal_chemicals.items()):
            if amount > 0.001:
                current_conc = world.get_chemical_concentration(self.x, self.y, self.z, molecule)
                new_conc = current_conc + amount
                if new_conc <= 0.001:
                    # Remove if negligible
                    if (self.x, self.y, self.z) in world.chemical_concentrations:
                        if molecule in world.chemical_concentrations[(self.x, self.y, self.z)]:
                            del world.chemical_concentrations[(self.x, self.y, self.z)][molecule]
                else:
                    world.chemical_concentrations[(self.x, self.y, self.z)][molecule] = new_conc

        # In a full implementation, we'd also handle decomposition, etc.
        # For now, just mark as dead
        self.is_alive = False

    def is_alive(self) -> bool:
        """Check if the organism is alive."""
        return getattr(self, 'is_alive', True)

    def get_info(self) -> dict:
        """Get information about the organism for debugging/display."""
        return {
            'position': (self.x, self.y, self.z),
            'age': self.age,
            'mass': self.mass,
            'energy': {
                'total': self.energy.total_energy(),
                'chemical': self.energy.get_energy(EnergyType.CHEMICAL),
                'thermal': self.energy.get_energy(EnergyType.THERMAL),
                'kinetic': self.energy.get_energy(EnergyType.KINETIC),
                'electrical': self.energy.get_energy(EnergyType.ELECTRICAL),
                'light': self.energy.get_energy(EnergyType.LIGHT)
            },
            'internal_chemicals': dict(self.internal_chemicals),
            'environment': {
                'temperature': self.world.get_temperature(self.x, self.y, self.z),
                'light': self.world.get_light_intensity(self.x, self.y, self.z)
            }
        }


# Global organism list (in a real implementation, this would be managed by a population manager)
_organisms = []

def add_organism(organism: Organism):
    """Add an organism to the global list."""
    _organisms.append(organism)

def get_organisms() -> List[Organism]:
    """Get all organisms."""
    return _organisms

def update_organisms(dt: float = 1.0):
    """Update all organisms."""
    for organism in _organisms[:]:  # Copy list to allow removal during iteration
        if organism.is_alive():
            organism.update_metabolism(dt)
        else:
            _organisms.remove(organism)