
from os import path
from typing import List

import yaml


class GeneralSettings:

    def __init__(self, yaml_config):
        self.errors: List[str] = []

        # Default Settings
        self.input_dir = None
        self.output_dir = None
        self.recursive = False
        self.show_replacements = False
        self.default_strategy = 'simple'
        self.default_transition_probability = 0.5

        self.load_general_settings(yaml_config)

        if not self.validate:
            raise ValueError("Invalid configuration:\n\t:" "\n\t".join(self.errors))

    def load_general_settings(self, config):
        if config['general']:
            config_general = config['general']
            self.input_dir = config_general['input_directory']
            self.output_dir = config_general['output_directory']
            self.recursive = True if config_general['recursive'] else False
            self.show_replacements = True if config_general['show_replacements'] else False
            self.default_strategy = config_general['default_strategy']
            self.default_transition_probability = config_general['default_transition_probability']

    def validate(self):

        # Validate input_dir
        if self.input_dir is None:
            self.errors.append('Invalid configuration: general.input_directory is missing from configuration file. Please add it.')
        elif not path.exists(self.input_dir):
            self.errors.append('Invalid configuration: general.input_directory does not exist. Please provide a valid directory.')

        # Validate output dir
        if self.output_dir is None:
            self.errors.append('Invalid configuration: general.output_directory is missing from configuration file. Please add it.')

        return len(self.errors) < 1


class BratSyntheticConfig:

    def __init__(self, config_yaml_file_path: str):
        config_yaml_file_path = path.expanduser(path.expandvars(config_yaml_file_path))
        with open(config_yaml_file_path, 'r') as config_yaml_file:
            config = yaml.safe_load(config_yaml_file.read())
            self.general = GeneralSettings(config)


