from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl
import src.io.paths as io

def load_single_orbital(orbital_name, mode):
	dir_path = io.DATA_DIR / mode

	if mode == "point_cloud":
		points = bl.reader.read_data(orbital_name)
		bl.scene.create_point_cloud(points, name=orbital_name)
		return
	elif mode == "single_obj":
		verts, faces = bl.reader.read_obj_data(orbital_name)
		obj = bl.scene.create_mesh_object(verts, faces, name=orbital_name)
		bl.scene.smooth_object(obj)
		return

	parts = bl.reader.read_obj_parts(orbital_name, dir_path)
	obj, face_ranges = bl.scene.create_mesh_from_parts(parts, orbital_name)

	if mode == "signed_obj":
		specs = bl.materials.signed_material_specs(parts)
	elif mode == "batch_obj":
		specs = bl.materials.batch_material_specs(parts)

	bl.materials.apply_materials_from_specs(obj, specs, face_ranges)
	bl.scene.smooth_object(obj)

