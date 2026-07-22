from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))
	
import src.io.paths as io

def load_data(file_name: str) -> list[tuple[float, float, float]]:
	file_path = io.get_path(f"{file_name}.npy", io.POINT_CLOUD_DIR)
	
	points = []
	with open(file_path, 'r') as f:
		for line in f:
			x, y, z = map(float, line.strip().split(','))
			points.append((x, y, z))

	return points

def load_obj_data(file_name: str | Path, offset: int | None = None) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
	if isinstance(file_name, Path):
		file_path = file_name
	else:
		file_path = io.get_path(f"{file_name}.obj", io.SINGLE_OBJ_DIR)

	verts = []
	faces = []
	if offset is None:
		offset = 0

	with open(file_path, 'r') as f:
		for line in f:
			if line.startswith('v '):
				_, x, y, z = line.strip().split()
				verts.append((float(x), float(y), float(z)))
			elif line.startswith('f '):
				_, v1, v2, v3 = line.strip().split()
				faces.append((int(v1) + offset - 1, int(v2) + offset - 1, int(v3) + offset - 1))

	return verts, faces

def lvl_list(dir_name: str) -> list[int]:
	levels = []
	for file in io.get_data_subdir(dir_name, io.BATCH_OBJ_DIR):
		levels.append(int(file.stem.lstrip('lvl')))
	return levels

def load_obj_batch_data(dir_name: str):
	batch: dict[int, tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]] = {}
	vert_offset = 0

	for file in io.get_data_subdir(dir_name, io.BATCH_OBJ_DIR):
		lvl = int(file.stem.lstrip('lvl'))
		# Lê o OBJ diretamente do caminho real
		verts, faces = load_obj_data(file, offset=vert_offset)
		batch[lvl] = (verts, faces)
		vert_offset += len(verts)

	return batch