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

def move_collection_to_collection(child_col, parent_col):
	if not any(col == child_col for col in parent_col.children):
		try:
			bpy.context.scene.collection.children.unlink(child_col)
		except Exception:
			pass
		parent_col.children.link(child_col)

def organize_collections(orbitals, mode=None):
	prefix = f"{mode}_" if mode else ""
	mode_col = make_collection(mode) if mode else None

	for (n, l, _, _), obj in orbitals.items():
		n_col = make_collection(f"{prefix}n_{n}")
		l_col = make_collection(f"{prefix}n_{n}_l_{l}")

		if mode_col is not None:
			move_collection_to_collection(n_col, mode_col)
		move_collection_to_collection(l_col, n_col)
		move_to_collection(obj, l_col)
	
def smooth_object(obj):
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.object.shade_smooth()
	obj.select_set(False)

def select_object(obj):
	bpy.ops.object.select_all(action='DESELECT')
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj
	
def create_point_cloud(points, name="PointCloud"):
	mesh = bpy.data.meshes.new(f"{name}Mesh")
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.collection.objects.link(obj)

	mesh.from_pydata(points, [], [])
	mesh.update()
	return obj

def create_point_cloud(points, name="PointCloud",  radius=0.12):
	if not points:
		raise ValueError("Nuvem de pontos vazia.")

	vertices = []
	faces = []

	# Cada ponto vira um pequeno octaedro.
	# Tudo pertence a uma única malha.
	octa_faces = [
		(4, 0, 2), (4, 2, 1),
		(4, 1, 3), (4, 3, 0),
		(5, 2, 0), (5, 1, 2),
		(5, 3, 1), (5, 0, 3)
	]

	for x, y, z in points:
		offset = len(vertices)

		vertices.extend([
			(x + radius, y, z),
			(x - radius, y, z),
			(x, y + radius, z),
			(x, y - radius, z),
			(x, y, z + radius),
			(x, y, z - radius)
		])

		faces.extend(tuple(offset + index for index in face) for face in octa_faces)

	return create_mesh_object(vertices, faces, name=name)

def sphere_instancing(points, radius=0.1, name="SphereInstance"):
	bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0, 0, 0))
	sphere = bpy.context.active_object
	sphere.name = name

	for point in points:
		instance = sphere.copy()
		instance.location = point
		bpy.context.collection.objects.link(instance)

def create_mesh_from_parts(parts, name):
    all_verts = []
    all_faces = []
    face_ranges = {}

    for part in parts:
        vertex_offset = len(all_verts)
        face_start = len(all_faces)

        all_verts.extend(part["vertices"])

        for face in part["faces"]:
            all_faces.append(tuple(index + vertex_offset for index in face))

        face_ranges[part["name"]] = range(face_start, len(all_faces))

    obj = create_mesh_object(all_verts, all_faces, name=name)

    return obj, face_ranges