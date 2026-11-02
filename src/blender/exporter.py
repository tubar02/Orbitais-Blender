from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.io.paths as io
import src.blender as bl

def export_fbx(obj, orbital_name, mode, output_dir: Path | None = None, global_scale: float = 1.0):
	file_name = f"{orbital_name}_{mode}.fbx"
	target_dir = (output_dir if output_dir is not None else io.UNITY_DATA_DIR)
	output_path = io.get_path(file_name, target_dir)

	bl.scene.select_object(obj)
	result = bpy.ops.export_scene.fbx(filepath=str(output_path), 
	                                  use_selection=True, global_scale=global_scale)

	if "FINISHED" not in result:
		raise RuntimeError(f"Falha ao exportar {file_name} para FBX.")
	if not output_path.is_file() or output_path.stat().st_size == 0:
		raise RuntimeError(f"FBX ausente ou vazio: {output_path}")
	
	return output_path

def export_many_fbx(orbitals: dict, mode: str):
	for key in orbitals:
		n, l, m, basis = key
		obj = orbitals[key]
		orbital_name = f"orbital_n{n}_l{l}_m{m}_{basis}"
		export_fbx(obj, orbital_name, mode)