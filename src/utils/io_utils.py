from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

def ensure_dir(dir_path: Path):
	if not dir_path.exists():
		dir_path.mkdir(parents=True, exist_ok=True)

def get_data_path(file_name: str) -> Path:
	ensure_dir(DATA_DIR)
	file = DATA_DIR / file_name
	return file

def main():
	print(sys.builtin_module_names)

if __name__ == "__main__":
	main()