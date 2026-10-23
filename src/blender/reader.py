import re
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))
	
import src.io.paths as io

def read_data(file_name: str) -> list[tuple[float, float, float]]:
	file_path = io.get_path(f"{file_name}.npy", io.POINT_CLOUD_DIR)
	
	points = []
	with open(file_path, 'r') as f:
		for line in f:
			x, y, z = map(float, line.strip().split(','))
			points.append((x, y, z))

	return points

def read_obj_data(file_name: str | Path) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
	if isinstance(file_name, Path):
		file_path = file_name
	else:
		file_path = io.get_path(f"{file_name}.obj", io.SINGLE_OBJ_DIR)

	verts = []
	faces = []

	with open(file_path, 'r') as f:
		for line in f:
			if line.startswith('v '):
				_, x, y, z = line.strip().split()
				verts.append((float(x), float(y), float(z)))
			elif line.startswith('f '):
				_, v1, v2, v3 = line.strip().split()
				faces.append((int(v1) - 1, int(v2) - 1, int(v3) - 1))

	return verts, faces

def read_obj_parts(dir_name: str, dir_path: Path):
    parts = []

    for file_path in io.get_data_subdir(dir_name, dir_path):
        verts, faces = read_obj_data(file_path)

        parts.append({"name": file_path.stem, "vertices": verts, "faces": faces,})

    return parts

ORBITAL_PATTERN = re.compile(r"orbital_n(\d+)_l(\d+)_m(-?\d+)_(real|complex)")

def discover_orbitals(basis: str, dir_path: Path):
	entries = (p for p in dir_path.iterdir())
	orbitals = []

	for entry in entries:
		match = ORBITAL_PATTERN.fullmatch(entry.stem)
		n, l, m = map(int, match.groups()[:3])
		orb_basis = match.group(4)

		if orb_basis != basis:
			continue

		orbitals.append((n, l, m, orb_basis, entry.stem))
	return sorted(orbitals)