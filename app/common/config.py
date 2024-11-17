'''Tools to manage config file'''

import json
import os
import re
import warnings
from app.common.preprocess import CompanyNamesMerger, QMRemover

PREMADE_CONFIGS = {}

for filename in os.listdir('app/configs'):
    if filename.endswith('.json'):
        with open(f'app/configs/{filename}', encoding='utf-8') as f:
            PREMADE_CONFIGS[filename[:-5]] = json.load(f)

MAPPINGS = {
    'preprocessing': {
        'CompanyNamesMerger': CompanyNamesMerger(),
        'QMRemover': QMRemover()
    }
}

class Configuration:
    def __init__(self, config_path: str | None) -> None:
        '''
        Initialize the configuration based on the given path.

        If the config_path is None, the configuration is empty.
        If the config_path is given, the configuration is loaded from the file and
        updated with the default configuration and the 'default' configuration from
        the pre-made configurations.
        '''

        self._config = {}

        if config_path:
            with open(config_path, encoding='utf-8') as f:
                self._config = json.load(f)

        for key in self._config.keys():
            if key.startswith('_'):
                warnings.warn('Trying to set a protected key: ' + key)
        
        # Get the name of the base configuration
        default_config_name = self._config.get('config', 'default')

        # Get the base configuration
        base_config = PREMADE_CONFIGS[default_config_name]
        if default_config_name != 'default':
            for key in base_config.keys():
                if key.startswith('_'):
                    warnings.warn('Trying to set a protected key: ' + key)

        # Update the base configuration with the default values from even more default configuration if they are not present
        # This is to ensure that all the default values are present in the base configuration
        base_config.update({key: value for key, value in PREMADE_CONFIGS['default'].items() if key not in base_config})

        # Update the configuration with the values from the base configuration if they are not present
        # This is to ensure that all the keys are present in the configuration
        self._config.update({key: value for key, value in base_config.items() if key not in self._config})

        # Replace string representations with actual objects
        for key, mapping in MAPPINGS.items():
            if key in self._config:
                representation = self._config[key]
                try:
                    if isinstance(representation, str):
                        self._config[key] = mapping[representation]
                    elif isinstance(representation, (list, tuple)):
                        self._config[key] = [mapping[r] for r in representation]
                    else:
                        raise ValueError
                except (KeyError, ValueError) as exception:
                    raise ValueError(f'Invalid representation for {key}: {representation}') from exception
            

    def __getitem__(self, key):
        if re.search('/', key):
            folder, filename  = key.split('/')
            real_folder = self._config[folder + '_folder']
            real_filename = self._config[filename + '_filename']
            res_path = os.path.join( real_folder, real_filename)
            if not res_path.startswith('/'):
                res_path = '/' + res_path
            return '.'+res_path
        return self._config[key]
    
