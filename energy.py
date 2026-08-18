"""
Energy system for the life simulation.
Handles energy transformations, metabolic costs, and energy accounting.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import math


class EnergyType(Enum):
    """Different forms of energy in the system."""
    CHEMICAL = "chemical"    # Energy stored in molecular bonds
    THERMAL = "thermal"      # Heat energy
    KINETIC = "kinetic"      # Energy of motion
    ELECTRICAL = "electrical" # Neural/signal transmission energy
    LIGHT = "light"          # Electromagnetic radiation energy


@dataclass
class EnergyAccount:
    """Tracks energy budget for an entity (organism, environment patch, etc.)."""
    # Energy reserves by type
    reserves: Dict[EnergyType, float] = field(default_factory=lambda: {
        EnergyType.CHEMICAL: 0.0,
        EnergyType.THERMAL: 0.0,
        EnergyType.KINETIC: 0.0,
        EnergyType.ELECTRICAL: 0.0,
        EnergyType.LIGHT: 0.0
    })

    # Total energy consumed/produced (for tracking)
    total_consumed: float = 0.0
    total_produced: float = 0.0

    def get_energy(self, energy_type: EnergyType) -> float:
        """Get available energy of a specific type."""
        return self.reserves.get(energy_type, 0.0)

    def add_energy(self, energy_type: EnergyType, amount: float) -> bool:
        """
        Add energy to reserves.
        Returns True if successful, False if amount would be negative.
        """
        if amount < 0:
            return self.use_energy(energy_type, -amount)

        self.reserves[energy_type] = self.reserves.get(energy_type, 0.0) + amount
        self.total_produced += amount
        return True

    def use_energy(self, energy_type: EnergyType, amount: float) -> bool:
        """
        Use energy from reserves.
        Returns True if sufficient energy was available, False otherwise.
        """
        available = self.reserves.get(energy_type, 0.0)
        if available < amount:
            return False

        self.reserves[energy_type] = available - amount
        self.total_consumed += amount
        return True

    def apply_chemical_reaction_energy(self, chemical_energy_change: float,
                                     thermal_energy_change: float) -> bool:
        """
        Apply energy changes from a chemical reaction.
        chemical_energy_change: change in bond energy (positive = energy stored)
        thermal_energy_change: heat exchanged (positive = released to environment)
        Returns True if successful.
        """
        # Apply chemical energy change
        chem_success = self.add_energy(EnergyType.CHEMICAL, chemical_energy_change)
        # Apply thermal energy change
        therm_success = self.add_energy(EnergyType.THERMAL, thermal_energy_change)
        return chem_success and therm_success

    def transfer_energy(self, other: 'EnergyAccount', energy_type: EnergyType,
                       amount: float) -> bool:
        """
        Transfer energy to another EnergyAccount.
        Returns True if successful.
        """
        if self.use_energy(energy_type, amount):
            other.add_energy(energy_type, amount)
            return True
        return False

    def total_energy(self) -> float:
        """Get total energy across all types."""
        return sum(self.reserves.values())

    def is_viable(self) -> bool:
        """Check if the entity has sufficient energy to maintain basic functions."""
        # For now, consider viable if has any chemical energy
        return self.reserves.get(EnergyType.CHEMICAL, 0.0) > 0


class EnergyTransformer:
    """Handles transformations between different energy types."""

    @staticmethod
    def chemical_to_thermal(chemical_energy: float, efficiency: float = 0.8) -> float:
        """Convert chemical energy to thermal energy (exothermic reactions)."""
        return chemical_energy * efficiency

    @staticmethod
    def thermal_to_chemical(thermal_energy: float, efficiency: float = 0.3) -> float:
        """Convert thermal energy to chemical energy (endothermic processes like photosynthesis)."""
        return thermal_energy * efficiency

    @staticmethod
    def chemical_to_kinetic(chemical_energy: float, efficiency: float = 0.6) -> float:
        """Convert chemical energy to kinetic energy (muscle contraction)."""
        return chemical_energy * efficiency

    @staticmethod
    def chemical_to_electrical(chemical_energy: float, efficiency: float = 0.7) -> float:
        """Convert chemical energy to electrical energy (neural signaling)."""
        return chemical_energy * efficiency

    @staticmethod
    def light_to_chemical(light_energy: float, efficiency: float = 0.5) -> float:
        """Convert light energy to chemical energy (photosynthesis-like)."""
        return light_energy * efficiency


class MetabolicCosts:
    """Calculate energy costs for various biological processes."""

    @staticmethod
    def basal_metabolic_rate(mass: float, temperature: float) -> float:
        """
        Calculate basal metabolic rate (energy/time).
        Based on metabolic scaling theory: BMR = a * M^b * f(T)
        """
        # Base metabolic rate scaling (Kleiber's law-ish)
        base_rate = 0.1 * (mass ** 0.75)

        # Temperature correction (Q10 rule - approximately doubles every 10°C)
        # Assuming optimal temp around 20°C
        temp_factor = 2.0 ** ((temperature - 20.0) / 10.0)
        temp_factor = max(0.1, min(3.0, temp_factor))  # Clamp to reasonable range

        return base_rate * temp_factor

    @staticmethod
    def movement_cost(distance: float, speed: float, mass: float,
                     terrain_resistance: float = 1.0) -> float:
        """
        Calculate energy cost for movement.
        Based on work against friction and inertia.
        """
        # Kinetic energy component: 0.5 * m * v^2
        ke = 0.5 * mass * (speed ** 2)

        # Work against friction: force * distance
        # Friction force proportional to weight and resistance
        friction_work = mass * 9.8 * terrain_resistance * distance  # Assuming g=9.8

        # Additional cost for acceleration/deceleration
        # Simplified as proportional to distance
        acceleration_cost = 0.1 * mass * distance

        return (ke + friction_work + acceleration_cost) * 0.5  # Efficiency factor

    @staticmethod
    def thermoregulation_cost(delta_temp: float, surface_area: float,
                             insulation: float, time_period: float) -> float:
        """
        Calculate energy cost to maintain temperature against gradient.
        Based on heat transfer equations: Q = h * A * ΔT * t
        """
        # Heat transfer coefficient (lower with better insulation)
        h = 5.0 * (1.0 - insulation)  # Base 5 W/m²/K, reduced by insulation
        h = max(0.1, h)  # Prevent zero or negative

        # Heat energy needed
        heat_energy = h * surface_area * abs(delta_temp) * time_period

        # Convert to metabolic cost (assuming some efficiency)
        return heat_energy * 0.3  # 30% efficiency for heating/cooling

    @staticmethod
    def synthesis_cost(molecule: 'Molecule') -> float:
        """
        Calculate energy cost to synthesize a molecule.
        Based on bond energies and complexity.
        """
        # Base cost per atom
        atom_cost = len(molecule.composition) * 2.0

        # Additional cost for complexity (more bonds to form)
        bond_cost = (molecule.size - len(molecule.composition)) * 1.5

        # Penalty for unstable molecules (positive energy content)
        # In our chemistry system, unstable molecules have positive formation energy
        from chemistry import calculate_molecular_energy
        instability_penalty = max(0, calculate_molecular_energy(molecule))

        return atom_cost + bond_cost + instability_penalty * 0.1

    @staticmethod
    def neural_processing_cost(activation_level: float,
                              network_size: int) -> float:
        """
        Calculate energy cost for neural processing.
        Based on ion pumping to maintain gradients.
        """
        # Base cost proportional to network size and activity
        base_cost = 0.01 * network_size * activation_level

        # Additional cost for signal propagation
        propagation_cost = 0.005 * network_size * activation_level ** 2

        return base_cost + propagation_cost


class EnvironmentalEnergyExchange:
    """Handle energy exchange with the environment."""

    @staticmethod
    def heat_conduction(temperature_internal: float, temperature_external: float,
                       surface_area: float, conductivity: float,
                       thickness: float, time_period: float) -> float:
        """
        Calculate heat transfer via conduction.
        Q = k * A * ΔT * t / d
        """
        delta_temp = temperature_internal - temperature_external
        return (conductivity * surface_area * abs(delta_temp) * time_period) / max(0.001, thickness)

    @staticmethod
    def heat_convection(temperature_surface: float, temperature_fluid: float,
                       surface_area: float, convection_coeff: float,
                       time_period: float) -> float:
        """
        Calculate heat transfer via convection.
        Q = h * A * ΔT * t
        """
        delta_temp = temperature_surface - temperature_fluid
        return convection_coeff * surface_area * abs(delta_temp) * time_period

    @staticmethod
    def thermal_radiation(temperature: float, surface_area: float,
                         emissivity: float, time_period: float) -> float:
        """
        Calculate heat transfer via radiation.
        Q = ε * σ * A * T^4 * t (Stefan-Boltzmann law)
        """
        # Stefan-Boltzmann constant
        sigma = 5.670374419e-8  # W/m²/K⁴
        # Convert to our energy units (scaling factor)
        scaled_sigma = sigma * 1e-6  # Adjust for our timescale/units

        energy = emissivity * surface_area * scaled_sigma * (temperature ** 4) * time_period
        return max(0, energy)  # Only emit, don't absorb negative radiation

    @staticmethod
    def light_absorption(light_intensity: float, surface_area: float,
                        absorption_coeff: float, time_period: float) -> float:
        """
        Calculate energy absorbed from light.
        """
        return light_intensity * surface_area * absorption_coeff * time_period
```