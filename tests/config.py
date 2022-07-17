from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
TESTS_DIR = PROJECT_DIR / "tests"

INPUT_FILES_DIR = TESTS_DIR / "input_files"
REQUIREMENTS_IN_PATH = INPUT_FILES_DIR / "requirements.in"
REQUIREMENTS_OUT_PATH = INPUT_FILES_DIR / "requirements.txt"
