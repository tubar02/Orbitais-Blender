from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl
import src.io.paths as io

VALID_MODES = {"point_cloud", "single", "multilayer", "signed"}

def load_single_orbital(orbital_name, mode, input_dir: Path | None = None):
	if mode not in VALID_MODES:
		raise ValueError(f"Modo de representação inválido: {mode}")

	if mode == "point_cloud":
		points = bl.reader.read_data(orbital_name)
		obj = bl.scene.create_point_cloud(points, name=orbital_name)

	elif mode == "single":
		file_path = (input_dir / f"{orbital_name}.obj" if input_dir is not None else orbital_name)
		verts, faces = bl.reader.read_obj_data(file_path)
		obj = bl.scene.create_mesh_object(verts, faces, name=orbital_name)
		bl.scene.smooth_object(obj)

	else: 
		dir_path = input_dir if input_dir is not None else io.DATA_DIR / mode
		parts = bl.reader.read_obj_parts(orbital_name, dir_path)
		obj, face_ranges = bl.scene.create_mesh_from_parts(parts, orbital_name)

		if mode == "signed":
			specs = bl.materials.signed_material_specs(parts)
		elif mode == "multilayer":
			specs = bl.materials.multilayer_material_specs(parts)

		bl.materials.apply_materials_from_specs(obj, specs, face_ranges)
		bl.scene.smooth_object(obj)
		
	return obj

def load_all_orbitals(basis, mode, input_dir: Path | None = None):
	orbitals = {}
	dir_path = (input_dir if input_dir is not None else io.DATA_DIR / mode)
	available = bl.reader.discover_orbitals(basis, dir_path)

	for n, l, m, orb_basis, name in available:
		obj = load_single_orbital(name, mode)
		orbitals[(n, l, m, orb_basis)] = obj
	return orbitals