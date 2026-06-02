from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n, l, m = 3, 2, 0
	dir_name = f"orbital_n{n}_l{l}_m{m}"
	batch = bl.reader.load_obj_batch_data(dir_name)
	
	levels  = bl.reader.lvl_list(dir_name) # Níveis para normalizar cores
	min_level, max_level = min(levels), max(levels)

	all_verts, all_faces = [], []
	for lvl in levels:
		verts, faces = batch[lvl]
		all_verts.extend(verts)
		all_faces.extend(faces)
	main_obj = bl.scene.create_mesh_object(all_verts, all_faces, name=f"Orbitaln{n}_l{l}_m{m}")

	materials_cache = {}
	face_offset = 0
	for lvl in levels:
		norm_lvl = (lvl - min_level) / (max_level - min_level) if max_level != min_level else 0
		color_rgb = bl.materials.interpolate_color(norm_lvl)
		alpha = 0.3 + 0.7 * norm_lvl  # mais transparente para níveis baixos
		mat_key = (round(color_rgb[0], 2), round(color_rgb[1], 2), round(color_rgb[2], 2), round(alpha, 2))
		
		if mat_key not in materials_cache:
			mat = bl.materials.create_orbital_material(f"OrbitalMat_{lvl}", color_rgb, alpha)
			materials_cache[mat_key] = len(main_obj.data.materials)
			main_obj.data.materials.append(mat)

		_, faces = batch[lvl]
		for poly_idx in range(face_offset, face_offset + len(faces)):
			main_obj.data.polygons[poly_idx].material_index = materials_cache[mat_key]
		face_offset += len(faces)
		main_obj.data.update()
		bl.scene.smooth_object(main_obj)

main()