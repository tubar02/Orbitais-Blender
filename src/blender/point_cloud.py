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

n = 2
l = 0
m = 0

file_name = f"orbital_n{n}_l{l}_m{m}"
load_obj(file_name, name=file_name)

'''
file_name = "orbital_n3_l2_m-2"
points = load_data(file_name)
create_point_cloud(points, name=file_name)
'''