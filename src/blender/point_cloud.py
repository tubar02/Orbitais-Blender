from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import bpy
import src.io.paths as io

def load_data(file_name: str):
	file_path = io.get_data_path(f"{file_name}.npy")
	
	points = []
	with open(file_path, 'r') as f:
		for line in f:
			x, y, z = map(float, line.strip().split(','))
			points.append((x, y, z))

	return points

def load_obj(file_name: str, name="LoadedObject"):
	file_path = io.get_data_path(f"{file_name}.obj")

	verts = []
	faces = []

	with open(file_path, 'r') as f:
		for line in f:
			if line.startswith('v '):
				_, x, y, z = line.strip().split()
				verts.append((float(x), float(y), float(z)))
			elif line.startswith('f '):
				_, v1, v2, v3 = line.strip().split()
				faces.append((int(v1), int(v2), int(v3)))	

	mesh = bpy.data.meshes.new(f"{name}Mesh")
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.collection.objects.link(obj)
	mesh.from_pydata(verts, [], faces)
	mesh.update()
	
	return obj

def create_point_cloud(points, name="PointCloud"):
	mesh = bpy.data.meshes.new(f"{name}Mesh")
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.collection.objects.link(obj)

	mesh.from_pydata(points, [], [])
	mesh.update()

def sphere_instancing(points, radius=0.1, name="SphereInstance"):
	bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0, 0, 0))
	sphere = bpy.context.active_object
	sphere.name = name

	for point in points:
		instance = sphere.copy()
		instance.location = point
		bpy.context.collection.objects.link(instance)

def make_collection(name: str):
	if name in bpy.data.collections:
		return bpy.data.collections[name]

	col = bpy.data.collections.new(name)
	bpy.context.scene.collection.children.link(col)
	return col

def move_to_collection(obj, collection):
	# remove das coleções atuais
	for col in obj.users_collection:
		col.objects.unlink(obj)

	collection.objects.link(obj)
	
def smooth_object(obj):
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.object.shade_smooth()
	obj.select_set(False)

def m_order(l: int) -> list[int]:
	order = [0]
	for m in range(1, l + 1):
		order.extend([-m, m])
	return order

def arrange_orbital_grid(rows, margin_x=8, margin_y=30, margin_l=18):
	y_cursor = 0

	for n, groups_l in rows.items():
		x_cursor = 0
		row_height = 0

		for l, objs in groups_l.items():
			for obj in objs:
				width = obj.dimensions.x
				height = obj.dimensions.y

				obj.location.x = x_cursor + width / 2
				obj.location.y = y_cursor
				obj.location.z = 0

				x_cursor += width + margin_x
				row_height = max(row_height, height)

			# espaço extra entre blocos de l
			x_cursor += margin_l

		y_cursor -= row_height + margin_y

def load_orbital_grid(n_max=4):
	rows = {}

	for n in range(1, n_max + 1):
		n_col = make_collection(f"n_{n}")
		rows[n] = {}

		for l in range(0, n):
			l_col = make_collection(f"n_{n}_l_{l}")
			rows[n][l] = []

			# coloca coleção de l dentro da coleção n, se ainda não estiver
			if l_col.name not in n_col.children:
				try:
					bpy.context.scene.collection.children.unlink(l_col)
				except Exception:
					pass
				n_col.children.link(l_col)

			for m in m_order(l):
				file_name = f"orbital_n{n}_l{l}_m{m}"

				try:
					obj = load_obj(file_name, name=file_name)
				except FileNotFoundError:
					print(f"Arquivo não encontrado: {file_name}.obj")
					continue
				
				move_to_collection(obj, l_col)
				rows[n][l].append(obj)

				smooth_object(obj)

				print(f"Carregado: {file_name}")

	arrange_orbital_grid(rows)

def interpolate_color(t: float) -> tuple[float, float, float]:
	if t < 0.5:
		# Azul para ciano
		r = 0
		g = t * 2  # 0 → 1
		b = 1 - t * 2  # 1 → 0
	else:
		# Ciano para amarelo
		r = (t - 0.5) * 2  # 0 → 1
		g = 1
		b = 0
	
	return (r, g, b)

def create_orbital_material(name: str, color: tuple, alpha: float):
	mat = bpy.data.materials.new(name)
	mat.use_nodes = True
	mat.blend_method = 'BLEND'
	mat.show_transparent_back = True
	
	# Cria nodes
	links = mat.node_tree.links
	nodes = mat.node_tree.nodes

	# Limpa nodes padrão
	nodes.clear()
	
	# Node de saída
	output_node = nodes.new(type='ShaderNodeOutputMaterial')
	output_node.location = (300, 0)
	
	# BSDF principal
	bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
	bsdf.location = (0, 0)
	bsdf.inputs['Base Color'].default_value = (*color, 1.0)
	bsdf.inputs['Alpha'].default_value = alpha
	bsdf.inputs['Emission Color'].default_value = (*color, 1.0)  # Cor de emissão
	bsdf.inputs['Emission Strength'].default_value = 0.3  # Ajusta o brilho da emissão
	
	# Conecta
	links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
	
	return mat

def load_obj_batch(dir_name: str, name="LoadedObject"):
	# Níveis para normalizar cores
	levels = []
	for file in io.read_data_batch(dir_name):
		levels.append(int(file.stem.split('_')[-1].lstrip('lvl')))
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
	for file in io.read_data_batch(dir_name):
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
					face_indices = [int(v1) + vert_offset, int(v2) + vert_offset, int(v3) + vert_offset]
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

dir_name = "orbital_n2_l1_m0"
obj = load_obj_batch(dir_name, dir_name)