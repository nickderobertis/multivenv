from pathlib import Path
from typing import List

from multivenv._config import TargetConfig, VenvConfig
from multivenv.exc import CompiledRequirementsNotFoundException


# TODO: Add options to make requirement finding for sync more flexible (strict versus loose)
def find_requirements_file(config: VenvConfig) -> Path:
    current_target = TargetConfig.from_system()
    not_found: List[Path] = []
    for possible_path in config.possible_requirements_out_paths_for(current_target):
        if possible_path.exists():
            return possible_path
        not_found.append(possible_path)

    raise CompiledRequirementsNotFoundException(
        f"Could not find requirements file at any of {not_found}"
    )
