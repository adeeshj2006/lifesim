#!/usr/bin/env python3
"""
Test script for the chemistry system.
"""

from chemistry import *


def test_elements_and_molecules():
    """Test basic element and molecule functionality."""
    print("=== Testing Elements and Molecules ===")

    # Test element creation
    elem_a = Element.A
    elem_b = Element.B
    print(f"Element A: {elem_a}")
    print(f"Element B: {elem_b}")

    # Test molecule creation from elements
    mol_a = Molecule({Element.A: 1})
    mol_b = Molecule({Element.B: 1})
    print(f"Molecule A: {mol_a}")
    print(f"Molecule B: {mol_b}")

    # Test molecule creation from string
    mol_ab = Molecule.from_string("AB")
    mol_bcf = Molecule.from_string("BCF")
    mol_a2 = Molecule.from_string("A2")
    print(f"Molecule AB: {mol_ab}")
    print(f"Molecule BCF: {mol_bcf}")
    print(f"Molecule A2: {mol_a2}")

    # Test molecule combination
    combined = mol_a + mol_b
    print(f"A + B = {combined}")

    # Test molecule subtraction
    subtracted = combined - mol_a
    print(f"(A + B) - A = {subtracted}")

    # Test equality
    ab1 = Molecule.from_string("AB")
    ab2 = Molecule({Element.A: 1, Element.B: 1})
    print(f"AB from string == AB from dict: {ab1 == ab2}")

    print()


def test_energy_calculations():
    """Test energy calculations."""
    print("=== Testing Energy Calculations ===")

    # Test elemental energies
    for element in Element:
        mol = Molecule({element: 1})
        energy = calculate_molecular_energy(mol)
        print(f"Energy of {element.value}: {energy}")

    # Test molecular energies
    molecules_to_test = ["A", "B", "AB", "A2", "BCF", "ABC"]
    for formula in molecules_to_test:
        mol = Molecule.from_string(formula)
        energy = calculate_molecular_energy(mol)
        print(f"Energy of {formula}: {energy}")

    print()


def test_reactions():
    """Test reaction functionality."""
    print("=== Testing Reactions ===")

    # Test predefined reactions
    for i, reaction in enumerate(COMMON_REACTIONS[:5]):  # Test first 5
        print(f"Reaction {i+1}: {reaction.description}")
        print(f"  Reactants: {' + '.join(str(r) for r in reaction.reactants)}")
        print(f"  Products:  {' + '.join(str(p) for p in reaction.products)}")
        print(f"  Energy change: {reaction.energy_change:.2f}")
        print(f"  Exothermic: {reaction.is_exothermic}")
        print(f"  Endothermic: {reaction.is_endothermic}")
        print()

    # Test reaction application
    print("--- Testing Reaction Application ---")
    molecules = [Molecule.from_string("A"), Molecule.from_string("A")]
    print(f"Starting molecules: {[str(m) for m in molecules]}")

    reactions = get_reactions_for_molecules(molecules)
    if reactions:
        reaction = reactions[0]
        print(f"Applying reaction: {reaction.description}")
        remaining, energy_change = apply_reaction(molecules, reaction)
        print(f"Resulting molecules: {[str(m) for m in remaining]}")
        print(f"Energy change: {energy_change:.2f}")
        print(f"(Positive = energy released)")

    print()


def test_chemical_system():
    """Test the ChemicalSystem interface."""
    print("=== Testing ChemicalSystem Interface ===")

    chem_sys = ChemicalSystem()

    # Test molecule retrieval
    mol_a = chem_sys.get_molecule("A")
    mol_ab = chem_sys.get_molecule("AB")
    print(f"Retrieved molecule A: {mol_a}")
    print(f"Retrieved molecule AB: {mol_ab}")

    # Test element retrieval
    elem_c = chem_sys.get_element("c")
    print(f"Retrieved element 'c': {elem_c}")

    # Test possible reactions
    test_mols = [chem_sys.get_molecule("A"), chem_sys.get_molecule("A")]
    reactions = chem_sys.get_possible_reactions(test_mols)
    print(f"Possible reactions for [A, A]: {len(reactions)} found")
    if reactions:
        print(f"First reaction: {reactions[0].description}")

    # Test energy calculations
    energy = chem_sys.calculate_energy(mol_ab)
    print(f"Energy of AB: {energy}")

    print()


def test_spontaneous_reactions():
    """Test spontaneous reaction likelihood."""
    print("=== Testing Spontaneous Reaction Likelihood ===")

    # Test an exothermic reaction (should be more likely)
    exothermic_rxn = None
    for rxn in COMMON_REACTIONS:
        if rxn.energy_change > 0:
            exothermic_rxn = rxn
            break

    # Test an endothermic reaction (should be less likely)
    endothermic_rxn = None
    for rxn in COMMON_REACTIONS:
        if rxn.energy_change < 0:
            endothermic_rxn = rxn
            break

    if exothermic_rxn:
        likelihood_low_temp = spontaneous_reaction_likelihood(exothermic_rxn, temperature=20, light_intensity=0)
        likelihood_high_temp = spontaneous_reaction_likelihood(exothermic_rxn, temperature=100, light_intensity=0)
        likelihood_light = spontaneous_reaction_likelihood(exothermic_rxn, temperature=20, light_intensity=50)

        print(f"Exothermic reaction: {exothermic_rxn.description}")
        print(f"  Energy change: {exothermic_rxn.energy_change:.2f}")
        print(f"  Likelihood (T=20, L=0): {likelihood_low_temp:.4f}")
        print(f"  Likelihood (T=100, L=0): {likelihood_high_temp:.4f}")
        print(f"  Likelihood (T=20, L=50): {likelihood_light:.4f}")

    if endothermic_rxn:
        likelihood_low_temp = spontaneous_reaction_likelihood(endothermic_rxn, temperature=20, light_intensity=0)
        likelihood_high_temp = spontaneous_reaction_likelihood(endothermic_rxn, temperature=100, light_intensity=0)
        likelihood_high_light = spontaneous_reaction_likelihood(endothermic_rxn, temperature=20, light_intensity=100)

        print(f"Endothermic reaction: {endothermic_rxn.description}")
        print(f"  Energy change: {endothermic_rxn.energy_change:.2f}")
        print(f"  Likelihood (T=20, L=0): {likelihood_low_temp:.4f}")
        print(f"  Likelihood (T=100, L=0): {likelihood_high_temp:.4f}")
        print(f"  Likelihood (T=20, L=100): {likelihood_high_light:.4f}")

    print()


def main():
    """Run all tests."""
    print("Testing Chemistry System\n")

    test_elements_and_molecules()
    test_energy_calculations()
    test_reactions()
    test_chemical_system()
    test_spontaneous_reactions()

    print("=== All tests completed ===")


if __name__ == "__main__":
    main()