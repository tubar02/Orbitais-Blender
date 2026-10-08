from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n, l, m = 2, 0, 0
	suffix = "real"
	dir_name = f"orbital_n{n}_l{l}_m{m}_{suffix}"
	batch = bl.reader.read_signed_obj_data(dir_name)

	all_verts, all_faces = [], []
	for sign in batch.keys():
		verts, faces = batch[sign]
		all_verts.extend(verts)
		all_faces.extend(faces)
	main_obj = bl.scene.create_mesh_object(all_verts, all_faces, name=f"Orbital_n{n}_l{l}_m{m}_{suffix}")

	pos_color = bl.materials.SIGNED_COLOR["red"]
	neg_color = bl.materials.SIGNED_COLOR["blue"]
	pos_mat = bl.materials.create_orbital_material(f"OrbitalMat_Pos", pos_color, 1)
	neg_mat = bl.materials.create_orbital_material(f"OrbitalMat_Neg", neg_color, 1)
	main_obj.data.materials.append(pos_mat)
	main_obj.data.materials.append(neg_mat)

	face_offset = 0
	for sign in batch.keys():
		_, faces = batch[sign]
		mat_index = 0 if sign == "pos" else 1
		for poly_idx in range(face_offset, face_offset + len(faces)):
			main_obj.data.polygons[poly_idx].material_index = mat_index
		face_offset += len(faces)
		main_obj.data.update()
		bl.scene.smooth_object(main_obj)

main()