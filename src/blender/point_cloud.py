from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import bpy
import src.utils.io_utils as io

def load_data(file_name: str):
	file_path = io.get_data_path(file_name)
	
	points = []
	with open(file_path, 'r') as f:
		for line in f:
			x, y, z = map(float, line.strip().split(','))
			points.append((x, y, z))

	return points

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

file_name = "arbitrary_points2"
points = load_data(f"{file_name}.npy")
create_point_cloud(points)