from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.io.paths as io
import src.blender as bl

def export_fbx(obj, orbital_name, mode):
	file_name = f"{orbital_name}_{mode}.fbx"
	output_path = io.get_path(file_name, io.UNITY_DATA_DIR)

	bl.scene.select_object(obj)
	result = bpy.ops.export_scene.fbx(filepath=str(output_path), 
	                                  use_selection=True, global_scale=1.0)

	if "FINISHED" not in result:
		raise RuntimeError(f"Failed to export {file_name} to FBX format.")
	
	return output_path

def export_many_fbx(orbitals: dict, mode: str):
	for key in orbitals:
		n, l, m, basis = key
		obj = orbitals[key]
		orbital_name = f"orbital_n{n}_l{l}_m{m}_{basis}"
		export_fbx(obj, orbital_name, mode)