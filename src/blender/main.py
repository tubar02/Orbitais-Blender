from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n = 3
	l = 1
	m = 1
	#prefix = "orbital"
	prefix = "orbital_complex"
	orbital_name = f"{prefix}_n{n}_l{l}_m{m}"

	verts, faces = bl.reader.load_obj_data(orbital_name)
	obj = bl.scene.create_mesh_object(verts, faces, name=orbital_name)
	bl.scene.smooth_object(obj)

main()