from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n = 5
	l = 4
	m = 2
	orbital_name = f"orbital_n{n}_l{l}_m{m}"
	verts, faces = bl.reader.load_obj_data(orbital_name)
	bl.scene.create_mesh_object(verts, faces, name=orbital_name)

main()