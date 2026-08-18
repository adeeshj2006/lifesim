"""
Configuration system for the life simulation.
Manages parameters and settings for all subsystems.
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manages configuration for the simulation."""

    def __init__(self):
        self.config = {
            # Simulation settings
            'simulation': {
                'world_size': (100, 100, 1),
                'max_steps': 10000,
                'time_step': 1.0,
                'enable_logging': True,
                'log_interval': 100
            },

            # Chemistry settings
            'chemistry': {
                'default_temperature': 20.0,  # Celsius
                'reaction_rate_scale': 1.0,
                'diffusion_rate': 0.01,
                'light_sensitivity': 1.0
            },

            # Energy settings
            'energy': {
                'base_metabolic_rate': 0.1,
                'thermal_conductivity': 0.1,
                'energy_transfer_efficiency': 0.8
            },

            # World settings
            'world': {
                'initial_chemicals': {
                    'A': 1.0,
                    'B': 0.8,
                    'C': 0.5,
                    'D': 0.3,
                    'E': 0.2,
                    'F': 0.1,
                    'G': 0.1
                },
                'temperature_range': (10.0, 30.0),  # Celsius
                'light_cycle': {
                    'day_length': 12.0,  # hours
                    'night_length': 12.0,  # hours
                    'day_intensity': 1.0,
                    'night_intensity': 0.1
                }
            },

            # Organism settings
            'organism': {
                'initial_energy': 15.0,
                'max_age': 100.0,
                'starting_mass': 1.0,
                'mutation_rate': 0.001,
                'reproduction_energy_threshold': 50.0
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        target = self.config
        try:
            for k in keys[:-1]:
                target = target[k]
            target[keys[-1]] = value
        except (KeyError, TypeError):
            # Create nested structure if needed
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value

    def load_from_file(self, filename: str) -> bool:
        """Load configuration from a JSON file."""
        if not os.path.exists(filename):
            return False

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self._merge_dict(self.config, data)
            return True
        except Exception as e:
            print(f"Error loading config from {filename}: {e}")
            return False

    def save_to_file(self, filename: str) -> bool:
        """Save configuration to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config to {filename}: {e}")
            return False

    def _merge_dict(self, base: dict, update: dict):
        """Recursively merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value

    def get_all(self) -> dict:
        """Get a copy of the entire configuration."""
        return json.loads(json.dumps(self.config))  # Deep copy


# Global configuration instance
_config = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return _config

def load_config(filename: str) -> bool:
    """Load configuration from file."""
    return _config.load_from_file(filename)

def save_config(filename: str) -> bool:
    """Save configuration to file."""
    return _config.save_to_file(filename)

# Convenience functions for common configurations
def get_simulation_config() -> dict:
    """Get simulation configuration."""
    return _config.get('simulation', {})

def get_chemistry_config() -> dict:
    """Get chemistry configuration."""
    return _config.get('chemistry', {})

def get_energy_config() -> dict:
    """Get energy configuration."""
    return _config.get('energy', {})

def get_world_config() -> dict:
    """Get world configuration."""
    return _config.get('world', {})

def get_organism_config() -> dict:
    """Get organism configuration."""
    return _config.get('organism', {})


# Example usage:
# config = get_config()
# temp = config.get('chemistry.default_temperature')
# config.set('chemistry.reaction_rate_scale', 1.5)