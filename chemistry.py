"""
Chemistry system for the life simulation.
Handles chemical elements, molecules, reactions, and energy transfer.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import itertools


class Element(Enum):
    """The 7 base elements in the system."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


@dataclass
class Molecule:
    """Represents a chemical molecule composed of elements."""
    # Dictionary mapping elements to their counts in the molecule
    composition: Dict[Element, int] = field(default_factory=dict)

    def __post_init__(self):
        # Remove elements with zero count
        self.composition = {elem: count for elem, count in self.composition.items() if count > 0}

    @property
    def is_element(self) -> bool:
        """True if this molecule is a single element."""
        return len(self.composition) == 1 and list(self.composition.values())[0] == 1

    @property
    def size(self) -> int:
        """Total number of atoms in the molecule."""
        return sum(self.composition.values())

    def __add__(self, other: 'Molecule') -> 'Molecule':
        """Combine two molecules."""
        new_composition = self.composition.copy()
        for elem, count in other.composition.items():
            new_composition[elem] = new_composition.get(elem, 0) + count
        return Molecule(new_composition)

    def __sub__(self, other: 'Molecule') -> 'Molecule':
        """Subtract one molecule from another."""
        new_composition = self.composition.copy()
        for elem, count in other.composition.items():
            new_count = new_composition.get(elem, 0) - count
            if new_count <= 0:
                new_composition.pop(elem, None)
            else:
                new_composition[elem] = new_count
        return Molecule(new_composition)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Molecule):
            return False
        return self.composition == other.composition

    def __hash__(self) -> int:
        # Sort by enum value to ensure consistent hashing
        return hash(tuple(sorted(self.composition.items(), key=lambda x: x[0].value)))

    def __str__(self) -> str:
        if not self.composition:
            return ""

        parts = []
        for elem in sorted(self.composition.keys(), key=lambda e: e.value):
            count = self.composition[elem]
            if count == 1:
                parts.append(elem.value)
            else:
                parts.append(f"{elem.value}{count}")
        return "".join(parts)

    @classmethod
    def from_string(cls, formula: str) -> 'Molecule':
        """Create a molecule from a string formula like 'AB2' or 'BCF'."""
        import re
        composition = {}

        # Parse formula like "AB2C" -> [('A', ''), ('B', '2'), ('C', '')]
        pattern = r'([A-G])(\d*)'
        matches = re.findall(pattern, formula)

        for elem_str, count_str in matches:
            elem = Element(elem_str)
            count = int(count_str) if count_str else 1
            composition[elem] = composition.get(elem, 0) + count

        return cls(composition)


# Energy values for elements and molecules (in arbitrary energy units)
# Higher values mean more stable/stored energy
BASE_ELEMENT_ENERGY = {
    Element.A: 10,
    Element.B: 8,
    Element.C: 12,
    Element.D: 6,
    Element.E: 15,
    Element.F: 9,
    Element.G: 7,
}

# Cache for molecular energies to avoid recomputation
_molecular_energy_cache: Dict[Molecule, float] = {}


def calculate_molecular_energy(molecule: Molecule) -> float:
    """
    Calculate the energy content of a molecule.
    Simple model: sum of element energies + bonding energy adjustments.
    """
    if molecule in _molecular_energy_cache:
        return _molecular_energy_cache[molecule]

    # Base energy from constituent elements
    total_energy = 0
    for elem, count in molecule.composition.items():
        total_energy += BASE_ELEMENT_ENERGY[elem] * count

    # Bonding energy: negative bonus for stability (bond formation releases energy)
    # This is a simplified model - in reality would be much more complex
    size = molecule.size
    if size > 1:
        # Negative bonus for forming bonds (stability - lowers energy)
        bonding_bonus = -(size - 1) * 2
        total_energy += bonding_bonus

    _molecular_energy_cache[molecule] = total_energy
    return total_energy


def get_energy_change(
    reactants: List[Molecule],
    products: List[Molecule]
) -> float:
    """
    Calculate the energy change for a chemical reaction.
    Returns: energy released (positive) or absorbed (negative)
    """
    reactant_energy = sum(calculate_molecular_energy(r) for r in reactants)
    product_energy = sum(calculate_molecular_energy(p) for p in products)

    # Energy released = energy of reactants - energy of products
    # Positive = exothermic (releases energy)
    # Negative = endothermic (absorbs energy)
    return reactant_energy - product_energy


@dataclass
class ChemicalReaction:
    """Represents a chemical reaction."""
    reactants: List[Molecule]
    products: List[Molecule]
    description: str = ""

    def __post_init__(self):
        if not self.description:
            reactant_str = " + ".join(str(r) for r in self.reactants)
            product_str = " + ".join(str(p) for p in self.products)
            self.description = f"{reactant_str} -> {product_str}"

    @property
    def energy_change(self) -> float:
        """Energy change for this reaction (positive = exothermic)."""
        return get_energy_change(self.reactants, self.products)

    @property
    def is_exothermic(self) -> bool:
        """True if reaction releases energy."""
        return self.energy_change > 0

    @property
    def is_endothermic(self) -> bool:
        """True if reaction absorbs energy."""
        return self.energy_change < 0


# Predefined common reactions
COMMON_REACTIONS: List[ChemicalReaction] = [
    # Simple dimerizations
    ChemicalReaction([Molecule.from_string("A"), Molecule.from_string("A")],
                     [Molecule.from_string("A2")]),
    ChemicalReaction([Molecule.from_string("B"), Molecule.from_string("B")],
                     [Molecule.from_string("B2")]),
    ChemicalReaction([Molecule.from_string("C"), Molecule.from_string("C")],
                     [Molecule.from_string("C2")]),

    # Some example compounds
    ChemicalReaction([Molecule.from_string("A"), Molecule.from_string("B")],
                     [Molecule.from_string("AB")]),
    ChemicalReaction([Molecule.from_string("B"), Molecule.from_string("C"),
                     Molecule.from_string("F")],
                     [Molecule.from_string("BCF")]),
    ChemicalReaction([Molecule.from_string("A"), Molecule.from_string("D"),
                     Molecule.from_string("E")],
                     [Molecule.from_string("ADE")]),
]

# Reverse reactions for completeness
for reaction in list(COMMON_REACTIONS):  # Copy to avoid modifying during iteration
    reverse_reaction = ChemicalReaction(reaction.products, reaction.reactants,
                                      reaction.description.split(" -> ")[1] + " -> " +
                                      reaction.description.split(" -> ")[0])
    COMMON_REACTIONS.append(reverse_reaction)


def get_reactions_for_molecules(
    molecules: List[Molecule]
) -> List[ChemicalReaction]:
    """
    Get all possible reactions that can occur with the given molecules.
    """
    possible_reactions = []

    for reaction in COMMON_REACTIONS:
        # Check if we have enough of each reactant
        reactant_counts = {}
        for reactant in reaction.reactants:
            reactant_counts[reactant] = reactant_counts.get(reactant, 0) + 1

        available_counts = {}
        for molecule in molecules:
            available_counts[molecule] = available_counts.get(molecule, 0) + 1

        # Check if we have sufficient reactants
        has_sufficient = True
        for reactant, needed_count in reactant_counts.items():
            if available_counts.get(reactant, 0) < needed_count:
                has_sufficient = False
                break

        if has_sufficient:
            possible_reactions.append(reaction)

    return possible_reactions


def apply_reaction(
    molecules: List[Molecule],
    reaction: ChemicalReaction
) -> tuple[List[Molecule], float, float]:
    """
    Apply a chemical reaction to a list of molecules.
    Returns: (remaining_molecules, thermal_energy_change, chemical_energy_change)
    Thermal energy change: positive = released to environment, negative = absorbed from environment
    Chemical energy change: change in intrinsic chemical energy of molecules
    """
    # Make a copy to work with
    remaining = molecules.copy()

    # Remove reactants
    for reactant in reaction.reactants:
        if reactant in remaining:
            remaining.remove(reactant)
        else:
            # Not enough reactants - this shouldn't happen if checked properly
            return molecules, 0.0, 0.0

    # Add products
    remaining.extend(reaction.products)

    # Calculate energy changes
    # Chemical energy change: energy stored in bonds
    initial_chemical_energy = sum(calculate_molecular_energy(r) for r in reaction.reactants)
    final_chemical_energy = sum(calculate_molecular_energy(p) for p in reaction.products)
    chemical_energy_change = final_chemical_energy - initial_chemical_energy  # Positive = energy stored in bonds

    # Thermal energy change: heat released/absorbed (opposite of chemical energy change for conservation)
    # In exothermic reactions: chemical energy decreases, thermal energy increases (released)
    # In endothermic reactions: chemical energy increases, thermal energy decreases (absorbed)
    thermal_energy_change = -chemical_energy_change  # Conservation of energy

    return remaining, thermal_energy_change, chemical_energy_change


def spontaneous_reaction_likelihood(
    reaction: ChemicalReaction,
    temperature: float,
    light_intensity: float
) -> float:
    """
    Calculate the likelihood of a spontaneous reaction occurring
    based on environmental conditions.

    Returns a value between 0 and 1 representing probability per time step.
    """
    # Base likelihood based on energy change
    # Exothermic reactions (energy released) are more likely
    # Endothermic reactions (energy absorbed) less likely unless energized

    energy_change = reaction.energy_change

    # Base probability - exothermic reactions more likely
    if energy_change > 0:  # Exothermic
        base_prob = min(0.1, energy_change / 100.0)  # Cap at 0.1
    else:  # Endothermic
        base_prob = max(0.0, energy_change / 500.0)  # Very low unless helped

    # Modifiers based on environment
    # Heat increases reaction rates (Arrhenius-like behavior)
    heat_factor = 1.0 + (temperature / 100.0)  # Assuming temperature in reasonable range

    # Light can drive certain reactions (photochemistry)
    light_factor = 1.0 + (light_intensity / 50.0)  # Assuming light intensity in reasonable range

    # Combine factors
    likelihood = base_prob * heat_factor * light_factor

    # Ensure reasonable bounds
    return max(0.0, min(1.0, likelihood))


class ChemicalSystem:
    """Main interface for the chemistry system."""

    def __init__(self):
        self.molecule_cache: Dict[str, Molecule] = {}

    def get_molecule(self, formula: str) -> Molecule:
        """Get or create a molecule from its formula string."""
        if formula not in self.molecule_cache:
            self.molecule_cache[formula] = Molecule.from_string(formula)
        return self.molecule_cache[formula]

    def get_element(self, element_char: str) -> Element:
        """Get an element from its character representation."""
        try:
            return Element(element_char.upper())
        except ValueError:
            raise ValueError(f"Invalid element: {element_char}. Must be A-G.")

    def get_possible_reactions(self, molecules: List[Molecule]) -> List[ChemicalReaction]:
        """Get all possible reactions for a set of molecules."""
        return get_reactions_for_molecules(molecules)

    def calculate_energy(self, molecule: Molecule) -> float:
        """Calculate the energy of a molecule."""
        return calculate_molecular_energy(molecule)

    def calculate_reaction_energy(self, reaction: ChemicalReaction) -> float:
        """Calculate the energy change for a reaction."""
        return reaction.energy_change

    def apply_reaction(
        self, molecules: List[Molecule], reaction: ChemicalReaction
    ) -> tuple[List[Molecule], float, float]:
        """
        Apply a chemical reaction and return the results with energy changes.
        Returns: (remaining_molecules, thermal_energy_change, chemical_energy_change)
        Thermal energy change: positive = released to environment, negative = absorbed from environment
        Chemical energy change: change in intrinsic chemical energy of molecules
        """
        return apply_reaction(molecules, reaction)