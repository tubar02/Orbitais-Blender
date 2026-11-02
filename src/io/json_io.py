import json
from pathlib import Path

def load_json(path: Path) -> dict:
	with Path(path).open("r", encoding="utf-8") as file:
		return json.load(file)