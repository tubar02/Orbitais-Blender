import bpy

def new_empty_object(name: str = "EmptyObject"):
	mesh = bpy.data.meshes.new(f"{name}Mesh")
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.collection.objects.link(obj)
	return mesh, obj

def create_mesh_object(verts, faces, name="NewObject"):
	mesh, obj = new_empty_object(name)
	mesh.from_pydata(verts, [], faces)
	mesh.update()
	return obj

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