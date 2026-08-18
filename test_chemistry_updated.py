#!/usr/bin/env python3
"""
Test script for the updated chemistry system with energy tracking.
"""

from chemistry import *


def test_energy_tracking():
    """Test the updated energy tracking in chemical reactions."""
    print("=== Testing Energy Tracking in Chemical Reactions ===")

    # Test simple dimerization: A + A -> A2
    mol_a = Molecule.from_string("A")
    mol_a2 = Molecule.from_string("A2")

    print(f"Energy of A: {calculate_molecular_energy(mol_a)}")
    print(f"Energy of A2: {calculate_molecular_energy(mol_a2)}")

    # Create reaction
    rxn = ChemicalReaction([mol_a, mol_a], [mol_a2])
    print(f"Reaction: {rxn.description}")
    print(f"Chemical energy change: {rxn.energy_change:.2f}")

    # Apply reaction
    molecules = [mol_a, mol_a]
    print(f"Before reaction: {[str(m) for m in molecules]}")

    remaining, thermal_energy, chemical_energy = apply_reaction(molecules, rxn)
    print(f"After reaction: {[str(m) for m in remaining]}")
    print(f"Thermal energy change: {thermal_energy:.2f} (positive = released to environment)")
    print(f"Chemical energy change: {chemical_energy:.2f} (positive = stored in bonds)")

    # Verify energy conservation
    total_change = thermal_energy + chemical_energy
    print(f"Total energy change: {total_change:.2f} (should be ~0 for conservation)")
    print()

    # Test endothermic reaction: A2 -> A + A (reverse)
    print("--- Testing reverse reaction (bond breaking) ---")
    rxn_reverse = ChemicalReaction([mol_a2], [mol_a, mol_a])
    print(f"Reaction: {rxn_reverse.description}")
    print(f"Chemical energy change: {rxn_reverse.energy_change:.2f}")

    molecules = [mol_a2]
    print(f"Before reaction: {[str(m) for m in molecules]}")

    remaining, thermal_energy, chemical_energy = apply_reaction(molecules, rxn_reverse)
    print(f"After reaction: {[str(m) for m in remaining]}")
    print(f"Thermal energy change: {thermal_energy:.2f} (positive = released to environment)")
    print(f"Chemical energy change: {chemical_energy:.2f} (positive = stored in bonds)")

    # Verify energy conservation
    total_change = thermal_energy + chemical_energy
    print(f"Total energy change: {total_change:.2f} (should be ~0 for conservation)")
    print()

    # Test more complex reaction: B + C + F -> BCF
    print("--- Testing complex molecule formation ---")
    mol_b = Molecule.from_string("B")
    mol_c = Molecule.from_string("C")
    mol_f = Molecule.from_string("F")
    mol_bcf = Molecule.from_string("BCF")

    print(f"Energy of B: {calculate_molecular_energy(mol_b)}")
    print(f"Energy of C: {calculate_molecular_energy(mol_c)}")
    print(f"Energy of F: {calculate_molecular_energy(mol_f)}")
    print(f"Energy of BCF: {calculate_molecular_energy(mol_bcf)}")

    rxn_bcf = ChemicalReaction([mol_b, mol_c, mol_f], [mol_bcf])
    print(f"Reaction: {rxn_bcf.description}")
    print(f"Chemical energy change: {rxn_bcf.energy_change:.2f}")

    molecules = [mol_b, mol_c, mol_f]
    print(f"Before reaction: {[str(m) for m in molecules]}")

    remaining, thermal_energy, chemical_energy = apply_reaction(molecules, rxn_bcf)
    print(f"After reaction: {[str(m) for m in remaining]}")
    print(f"Thermal energy change: {thermal_energy:.2f}")
    print(f"Chemical energy change: {chemical_energy:.2f}")

    # Verify energy conservation
    total_change = thermal_energy + chemical_energy
    print(f"Total energy change: {total_change:.2f} (should be ~0 for conservation)")
    print()


def test_reaction_enumeration():
    """Test that reaction enumeration still works correctly."""
    print("=== Testing Reaction Enumeration ===")

    # Test with molecules that can react
    molecules = [Molecule.from_string("A"), Molecule.from_string("A")]
    reactions = get_reactions_for_molecules(molecules)
    print(f"With [A, A], found {len(reactions)} possible reactions:")
    for rxn in reactions:
        print(f"  {rxn.description}")
    print()

    # Test with molecules that can form a complex
    molecules = [Molecule.from_string("B"), Molecule.from_string("C"), Molecule.from_string("F")]
    reactions = get_reactions_for_molecules(molecules)
    print(f"With [B, C, F], found {len(reactions)} possible reactions:")
    for rxn in reactions:
        print(f"  {rxn.description}")
    print()


def main():
    """Run all tests."""
    print("Testing Updated Chemistry System with Energy Tracking\n")

    test_energy_tracking()
    test_reaction_enumeration()

    print("=== All tests completed ===")


if __name__ == "__main__":
    main()