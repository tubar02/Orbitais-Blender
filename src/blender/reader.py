from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
	
import src.io.paths as io

def load_data(file_name: str) -> list[tuple[float, float, float]]:
	file_path = io.get_path(f"{file_name}.npy")
	
	points = []
	with open(file_path, 'r') as f:
		for line in f:
			x, y, z = map(float, line.strip().split(','))
			points.append((x, y, z))

	return points

def load_obj(file_name: str, name: str ="LoadedObject"):
	file_path = io.get_path(f"{file_name}.obj")

	verts = []
	faces = []

	with open(file_path, 'r') as f:
		for line in f:
			if line.startswith('v '):
				_, x, y, z = line.strip().split()
				verts.append((float(x), float(y), float(z)))
			elif line.startswith('f '):
				_, v1, v2, v3 = line.strip().split()
				faces.append((int(v1) -1, int(v2) -1, int(v3) -1))	

	mesh = bpy.data.meshes.new(f"{name}Mesh")
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.collection.objects.link(obj)
	mesh.from_pydata(verts, [], faces)
	mesh.update()
	
	return obj

def load_obj_batch(dir_name: str, name="LoadedObject"):
	# Níveis para normalizar cores
	levels = []
	for file in io.get_data_batch(dir_name):
		levels.append(int(file.stem.lstrip('lvl')))
	min_level, max_level = min(levels), max(levels)

	# Mesh principal
	main_mesh = bpy.data.meshes.new(f"{name}Mesh")
	main_obj = bpy.data.objects.new(name, main_mesh)
	bpy.context.collection.objects.link(main_obj)

	all_verts = []
	all_faces = []
	vert_offset = 0
	face_materials = []  # rastreia qual material cada face usa
	
	# Dicionário para reutilizar materiais
	materials_cache = {}

	i = 0
	for file in io.get_data_batch(dir_name):
		lvl = levels[i]
		norm_lvl = (lvl - min_level) / (max_level - min_level) if max_level > min_level else 0
		color_rgb = interpolate_color(norm_lvl)
		alpha = 0.3 + 0.7 * norm_lvl  # mais transparente para níveis baixos
		mat_key = (round(color_rgb[0], 2), round(color_rgb[1], 2), round(color_rgb[2], 2), round(alpha, 2))

		if mat_key not in materials_cache:
			mat_name = f"{name}_lvl{lvl}"
			mat = create_orbital_material(mat_name, color_rgb, alpha)
			materials_cache[mat_key] = len(main_obj.data.materials)
			main_obj.data.materials.append(mat)

		mat_index = materials_cache[mat_key]
		
		# Lê o OBJ
		verts = []
		faces = []
		with open(file, 'r') as f:
			for line in f:
				if line.startswith('v '):
					_, x, y, z = line.strip().split()
					verts.append((float(x), float(y), float(z)))
				elif line.startswith('f '):
					_, v1, v2, v3 = line.strip().split()
					face_indices = [int(v1) + vert_offset - 1, int(v2) + vert_offset - 1, int(v3) + vert_offset - 1]
					faces.append(face_indices)
		
		all_verts.extend(verts)
		for face in faces:
			face_materials.append(mat_index)
		all_faces.extend(faces)
		vert_offset += len(verts)
		i += 1

	main_mesh.from_pydata(all_verts, [], all_faces)

	# Atribui materiais às faces
	for face_idx, mat_idx in enumerate(face_materials):
		main_mesh.polygons[face_idx].material_index = mat_idx

	main_mesh.update()
	smooth_object(main_obj)
	return main_obj