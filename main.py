"""
Main simulation loop for the life simulation.
"""

import time
import random
import math
from typing import List
from config import ConfigManager
from world import World, get_world
from organism import Organism, update_organisms
from chemistry import ChemicalSystem, Molecule, Element
from energy import EnergyAccount, EnergyType


# Global configuration
config_manager = ConfigManager()
config = config_manager.config


def create_default_world() -> World:
    """Create a world with default configuration."""
    world_config = config.get('world', {})
    width = world_config.get('default_width', 50)
    height = world_config.get('default_height', 50)
    depth = world_config.get('default_depth', 1)

    world = World(width, height, depth)

    # Initialize chemical concentrations from config
    init_chemicals = config.get('world.initial_chemicals', {
        'A': 1.0, 'B': 0.8, 'C': 0.5, 'D': 0.3, 'E': 0.2, 'F': 0.1, 'G': 0.1
    })

    # Add chemicals in a grid pattern
    step_x = max(1, width // 5)
    step_y = max(1, height // 5)
    for x in range(0, width, step_x):
        for y in range(0, height, step_y):
            for elem_symbol, concentration in init_chemicals.items():
                try:
                    element = Element(elem_symbol)
                    molecule = Molecule({element: 1})
                    # Add some random variation
                    varied_conc = concentration * (0.5 + random.random())
                    current = world.get_chemical_concentration(x, y, 0, molecule)
                    new_conc = min(current + varied_conc * 0.1, 10.0)
                    world.set_chemical_concentration(x, y, 0, molecule, new_conc)
                except ValueError:
                    continue  # Skip invalid element symbols

    # Set up temperature variation (warmer in center)
    base_temp = config.get('world.default_temperature', 20.0)
    temp_var = config.get('world.temperature_variation', 5.0)
    for x in range(width):
        for y in range(height):
            # Distance from center (normalized)
            cx, cy = width // 2, height // 2
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            max_dist = math.sqrt((width//2)**2 + (height//2)**2)
            if max_dist > 0:
                norm_dist = min(dist / max_dist, 1.0)
                # Center is warmer, edges are cooler
                temp = base_temp + (temp_var * (1.0 - norm_dist * 0.5))
                # Add some random noise
                temp += (random.random() - 0.5) * 2.0
                temp = max(0.0, temp)  # Ensure non-negative
                world.set_temperature(x, y, 0, temp)

    # Set initial light levels (will be updated in main loop)
    light_level = config.get('world.default_light_level', 0.5)
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                # Add some variation
                varied_light = light_level * (0.8 + random.random() * 0.4)
                varied_light = min(1.0, max(0.0, varied_light))
                world.set_light_intensity(x, y, z, varied_light)

    return world


def create_initial_population(count: int = 20):
    """Create the initial population of organisms."""
    from organism import add_organism
    world = get_world()

    # Get organism config
    org_config = config.get('organism', {})
    default_mass = org_config.get('default_mass', 1.0)
    default_size = org_config.get('default_size', 0.5)
    max_age = org_config.get('max_age', 100.0)
    starting_energy = org_config.get('starting_energy', 15.0)
    starting_thermal = org_config.get('starting_thermal', 5.0)
    default_insulation = org_config.get('default_insolation', 0.5)
    default_mobility = org_config.get('default_mobility', 0.5)
    default_metabolic_eff = org_config.get('default_metabolic_efficiency', 0.5)

    for _ in range(count):
        # Place away from edges
        margin = 5
        x = random.randint(margin, max(margin + 1, width - margin - 1))
        y = random.randint(margin, max(margin + 1, height - margin - 1))
        z = 0

        organism = Organism(x, y, z)

        # Apply configuration
        organism.mass = default_mass
        organism.size = default_size
        organism.max_age = max_age
        organism.insolation = default_insolation
        organism.mobility = default_mobility
        organism.metabolic_efficiency = default_metabolic_eff

        # Set initial energy
        organism.energy.add_energy(EnergyType.CHEMICAL, float(starting_energy))
        organism.energy.add_energy(EnergyType.THERMAL, float(starting_thermal))

        # Add to population
        add_organism(organism)


def update_world_processes(dt: float):
    """Update global world processes."""
    world = get_world()

    # Update light cycles (day/night)
    _update_light_cycles(world, dt)

    # TODO: Add other global processes like:
    # - Seasonal temperature changes
    # - Weather systems
    # - Large-scale nutrient cycles


def _update_light_cycles(world: World, dt: float):
    """Update light levels to simulate day/night cycles."""
    if not config.get('world.day_night_cycle', True):
        return

    # Calculate time of day (0.0 to 1.0 over 24 hours)
    hours_since_epoch = time.time() / 3600.0
    hours_in_day = (hours_since_epoch % 24.0)
    day_fraction = 0.5  # 50% day, 50% night by default

    is_daytime = (hours_in_day < (24.0 * day_fraction))

    # Base light levels
    day_light_level = 1.0
    night_light_level = 0.1

    base_light = day_light_level if is_daytime else night_light_level

    # Apply to all positions with some variation
    for x in range(world.width):
        for y in range(world.height):
            for z in range(world.depth):
                # Add temporal and spatial variation for realism
                time_variation = 0.1 * (0.5 - random.random())  # ±10% over time
                space_variation = 0.15 * (0.5 - random.random())  # ±15% spatial
                total_variation = time_variation + space_variation

                final_light = max(0.0, min(1.0, base_light + total_variation))
                world.set_light_intensity(x, y, z, final_light)


def run_simulation(steps: int = None, dt: float = None, verbose: bool = True):
    """Run the main simulation loop."""
    # Use defaults if not specified
    if steps is None:
        steps = config.get('simulation.max_steps', 1000)
    if dt is None:
        dt = config.get('simulation.time_step', 1.0)

    print("Initializing world...")
    world = create_default_world()

    print("Creating initial population...")
    create_initial_population()

    print(f"Starting simulation for {steps} steps (dt={dt}s)...")
    print(f"World size: {world.width}×{world.height}×{world.depth}")
    print(f"Configuration: {len(config.config)} sections loaded")

    start_time = time.time()
    try:
        for step in range(steps):
            # Update global world processes
            update_world_processes(dt)

            # Update all organisms
            update_organisms(dt)

            # Progress reporting
            if verbose and step % max(1, int(steps * 0.1)) == 0:  # Every 10%
                elapsed = time.time() - start_time
                from organism import get_organisms
                alive_count = len([o for o in get_organisms() if o.is_alive()])
                fps = 1.0 / (elapsed / max(step, 1)) if elapsed > 0 and step > 0 else 0
                print(f"Step {step}/{steps}, Pop: {alive_count}, "
                      f"Time: {elapsed:.1f}s, FPS: {fps:.1f}")

            # Detailed statistics periodically
            if step > 0 and step % max(1, int(steps * 0.2)) == 0:  # Every 20%
                _print_status_report(step, start_time)

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nSimulation error: {e}")
        import traceback
        traceback.print_exc()

    end_time = time.time()
    print(f"\nSimulation finished in {end_time - start_time:.1f} seconds")
    _print_final_report(start_time, end_time)


def _print_status_report(step: int, start_time: float):
    """Print a status report during simulation."""
    world = get_world()
    from organism import get_organisms

    organisms = get_organisms()
    alive_organisms = [o for o in organisms if o.is_alive()]

    print(f"\n--- Status Report --- Step {step} ---")
    print(f"Elapsed time: {time.time() - start_time:.1f}s")

    if alive_organisms:
        print(f"Population: {len(alive_organisms)} alive / {len(organisms)} total")

        # Basic stats
        avg_age = sum(o.age for o in alive_organisms) / len(alive_organisms)
        avg_energy = sum(o.energy.total_energy() for o in alive_organisms) / len(alive_organisms)
        print(f"Average age: {avg_age:.1f}")
        print(f"Average energy: {avg_energy:.2f}")

        # Simple energy breakdown
        chem_energy = sum(o.energy.get_energy(EnergyType.CHEMICAL) for o in alive_organisms)
        thermal_energy = sum(o.energy.get_energy(EnergyType.THERMAL) for o in alive_organisms)
        print(f"Total chemical energy: {chem_energy:.1f}")
        print(f"Total thermal energy: {thermal_energy:.1f}")

    # Environment sample
    center_x, center_y = world.width // 2, world.height // 2
    temp = world.get_temperature(center_x, center_y, 0)
    light = world.get_light_intensity(center_x, center_y, 0)
    print(f"Center env: {temp:.1f}°C, light: {light:.2f}")

    print("-" * 30)


def _print_final_report(start_time: float, end_time: float):
    """Print final simulation report."""
    print("\n" + "="*50)
    print("FINAL SIMULATION REPORT")
    print("="*50)
    print(f"Total simulation time: {end_time - start_time:.1f} seconds")

    world = get_world()
    from organism import get_organisms

    organisms = get_organisms()
    alive_organisms = [o for o in organisms if o.is_alive()]

    print(f"Final population: {len(alive_organisms)}/{len(organisms)} alive")

    if alive_organisms:
        print(f"\nFinal Population Statistics:")
        avg_age = sum(o.age for o in alive_organisms) / len(alive_organisms)
        avg_mass = sum(o.mass for o in alive_organisms) / len(alive_organisms)
        avg_energy = sum(o.energy.total_energy() for o in alive_organisms) / len(alive_organisms)
        print(f"  Average age: {avg_age:.1f}")
        print(f"  Average mass: {avg_mass:.2f}")
        print(f"  Average energy: {avg_energy:.2f}")

        # Energy breakdown
        print(f"\nEnergy Totals:")
        for et in [EnergyType.CHEMICAL, EnergyType.THERMAL, EnergyType.KINETIC,
                  EnergyType.ELECTRICAL, EnergyType.LIGHT]:
            total = sum(o.energy.get_energy(et) for o in alive_organisms)
            print(f"  {et.value.name}: {total:.1f}")

    print(f"\nFinal World State:")
    print(f"  Size: {world.width}×{world.height}×{world.depth}")

    # Sample environment
    center_x, center_y = world.width // 2, world.height // 2
    final_temp = world.get_temperature(center_x, center_y, 0)
    final_light = world.get_light_intensity(center_x, center_y, 0)
    print(f"  Center conditions: {final_temp:.1f}°C, light: {final_light:.2f}")

    # Chemical summary
    total_chemical_mass = 0.0
    unique_chemicals = set()
    sample_positions = list(world.chemical_concentrations.keys())
    if sample_positions:
        # Sample up to 100 positions
        for pos in sample_positions[:min(100, len(sample_positions))]:
            concs = world.chemical_concentrations[pos]
            for mol, conc in concs.items():
                if conc > 0.001:
                    total_chemical_mass += conc
                    unique_chemicals.add(mol)

        print(f"  Chemical diversity: {len(unique_chemicals)} types")
        print(f"  Total chemical mass: {total_chemical_mass:.1f} units")

    print("="*50)


if __name__ == "__main__":
    print("Life Simulation Framework")
    print("========================")
    print("Starting demonstration run...")
    print()

    # Run a demonstration
    run_simulation(steps=200, dt=1.0, verbose=True)

    print("\nDemonstration complete.")
    print("To run a longer simulation, modify the parameters in the code.")