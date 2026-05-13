from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import bpy
import src.utils.io_utils as io

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

def arrange_orbital_grid(rows, margin_x=8, margin_y=12, margin_l=18):
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

load_orbital_grid()

'''
file_name = "orbital_n3_l2_m-2"
points = load_data(file_name)
create_point_cloud(points, name=file_name)
'''