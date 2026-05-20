from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

def ensure_dir(dir_path: Path):
	if not dir_path.exists():
		dir_path.mkdir(parents=True, exist_ok=True)

def get_data_path(file_name: str) -> Path:
	ensure_dir(DATA_DIR)
	file = DATA_DIR / file_name
	return file

def get_data_batch(dir_name: str):
	dir_path = get_data_path(dir_name)
	if not dir_path.is_dir():
		raise ValueError(f"{dir_name} não é um diretório válido.")
	for file in dir_path.iterdir():
		yield file

def main():
	for file in get_data_batch("orbital_n2_l1_m0"):
		print(file)

if __name__ == "__main__":
	main()