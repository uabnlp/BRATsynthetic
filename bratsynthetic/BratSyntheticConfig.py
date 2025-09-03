
from os import path
from pathlib import Path
import random
from typing import List

import yaml


class OverrideSettings:
    """
    Setting that override the general settings for a particular maker class.
    """

    def __init__(self, cls_config):
        self.strategy = cls_config['strategy'] if 'strategy' in cls_config else None
        self.transition_probability = cls_config['transition_probability'] if 'transition_probability' in cls_config else None

class GeneralSettings:
    """
    This class keeps the setting for the YAML configuration file, specified by --config_file CLI option.

    Here are the variables for the configuration:
        input_directory - str, input directory of BRAT files with .txt and corresponding .ann files - Required
        output_directory - str, output directory of BRAT files with .txt and corresponding .ann files - Required
        default_strategy - str (default=simple), the surrogate replacement strategy.
                            Chose between simple, markov, consistent, random.
        default_transition_probability - float (default=0.5),  only applies to default_strategy=markov, alters the
                            transition probability
        seed - int (default=random integer), random seed for choosing replacement values, but can be set for reproducibility.
        suppress_phi_notice - boolean (default=False), Default behaviour is to print PHI notices on each .TXT file,
                            set to True to suppress generating the notices.
    """

    def __init__(self, yaml_config):
        self.errors: List[str] = []

        # Default Settings
        self.input_dir = None
        self.output_dir = None
        self.recursive = False
        self.show_replacements = False
        self.default_strategy = 'simple'
        self.default_transition_probability = 0.5
        self.seed = random.randint(0, 2**32 - 1)  #Afraid of negative seeds...
        self.suppress_phi_notice = False

        self.load_general_settings(yaml_config)

        if not self.validate():
            raise ValueError("Invalid configuration:\n\t" "\n\t".join(self.errors))

    def load_general_settings(self, config):
        if config['general']:
            config_general = config.get('general', {})
            # Convert to absolute paths to handle relative paths properly
            self.input_dir = str(Path(config_general['input_directory']).resolve()) if config_general['input_directory'] else None
            self.output_dir = str(Path(config_general['output_directory']).resolve()) if config_general['output_directory'] else None
            if 'recursive' in config_general:
                self.recursive = config_general['recursive']
            if 'show_replacements' in config_general:
                self.show_replacements = config_general['show_replacements']
            if 'default_strategy' in config_general:
                self.default_strategy = config_general['default_strategy']
            if 'default_transition_probability' in config_general:
                self.default_transition_probability = config_general['default_transition_probability']
            if 'seed' in config_general:
                self.seed = config_general['seed']

            self.suppress_phi_notice = config_general.get("suppress_phi_notice", self.suppress_phi_notice)

    def validate(self):

        # Validate input_dir
        if self.input_dir is None:
            self.errors.append('Invalid configuration: general.input_directory is missing from configuration file. Please add it.')
        else:
            # Convert relative to absolute path and check if it exists
            input_path = Path(self.input_dir)
            if not input_path.exists():
                self.errors.append(f'Invalid configuration: general.input_directory "{self.input_dir}" does not exist. Please provide a valid directory.')

        # Validate output dir - create if it doesn't exist (for relative paths)
        if self.output_dir is None:
            self.errors.append('Invalid configuration: general.output_directory is missing from configuration file. Please add it.')
        else:
            try:
                # Create output directory if it doesn't exist
                Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.errors.append(f'Invalid configuration: Cannot create output directory {self.output_dir}: {e}')

        if not isinstance(self.suppress_phi_notice, bool):
            raise TypeError(f"suppress_phi_notice is not a bool, instead it is a {type(self.suppress_phi_notice)}")


        return len(self.errors) < 1


class BratSyntheticConfig:

    def __init__(self, config_yaml_file_path: str):
        config_yaml_file_path = path.expanduser(path.expandvars(config_yaml_file_path))
        with open(config_yaml_file_path, 'r') as config_yaml_file:
            config = yaml.safe_load(config_yaml_file.read())
            self.general = GeneralSettings(config)
            self.override_settings = {}
            for key in config.keys():
                if key != 'general':
                    self.override_settings[key] = OverrideSettings(config[key])

    def strategy_name_for_class(self, cls) -> str:
        cls_name = cls.__name__
        strat = None
        if cls_name in self.override_settings:
            strat = self.override_settings[cls_name].strategy
        if strat is None:
            strat = self.general.default_strategy

        return strat



