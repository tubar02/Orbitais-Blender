import json
import os
import tempfile
from pathlib import Path

def load_json(path: Path) -> dict:
	with Path(path).open("r", encoding="utf-8") as file:
		return json.load(file)

def save_json(path: Path, data: dict) -> None:
	path = Path(path)
	path.parent.mkdir(parents=True, exist_ok=True)

	temp_path = None

	try:
		with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False) as file:
			temp_path = Path(file.name)
			json.dump(data, file, indent=4, ensure_ascii=False)
			file.write("\n")

		os.replace(temp_path, path)

	finally:
		if temp_path is not None:
			temp_path.unlink(missing_ok=True)