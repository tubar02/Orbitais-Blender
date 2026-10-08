from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))
	
import src.io.paths as io

def lvl_list(dir_name: str) -> list[int]:
	levels = []
	for file in io.get_data_subdir(dir_name, io.BATCH_OBJ_DIR):
		levels.append(int(file.stem.lstrip('lvl')))
	return levels

def norm_lvl(batch_parts):
	levels = [int(part["name"].lstrip("lvl")) for part in batch_parts]
	min_lvl, max_lvl = min(levels), max(levels)
	normalized_levels = [(lvl - min_lvl) / (max_lvl - min_lvl) for lvl in levels]

	return normalized_levels