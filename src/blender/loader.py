from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl
import src.io.paths as io

def main():
	n, l, m = 2, 1, 0
	suffix = "real"
	dir_name = f"orbital_n{n}_l{l}_m{m}_{suffix}"
	dir_path = io.SIGNED_OBJ_DIR
	mode = "signed"

	parts = bl.reader.read_obj_parts(dir_path, dir_name)
	obj, face_ranges = bl.scene.create_mesh_from_parts(parts, dir_name)

	if mode == "signed":
		specs = bl.materials.signed_material_specs(parts)
	elif mode == "batch":
		specs = bl.materials.batch_material_specs(parts)

	

# main()