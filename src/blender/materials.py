import bpy

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

def create_orbital_material(name: str, color: tuple[float, float, float], alpha: float):
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

SIGNED_COLOR = {"red": (1.0, 0.0, 0.0), "blue": (0.0, 0.0, 1.0)}

def batch_material_specs(parts):
	levels = [int(part["name"].lstrip("lvl")) for part in parts]
	min_level, max_level = min(levels), max(levels)

	specs = {}
	for part, lvl in zip(parts, levels):
		norm_lvl = (lvl - min_level) / (max_level - min_level) if max_level != min_level else 0
		color = interpolate_color(norm_lvl)
		alpha = 0.3 + 0.7 * norm_lvl  # mais transparente para níveis baixos
		specs[part["name"]] = {"color": color, "alpha": alpha}

	return specs

def signed_material_specs(parts):
	colors = {"neg": (0.0, 0.0, 1.0), "pos": (1.0, 0.0, 0.0)}
	specs = {}
	for part in parts:
		specs[part["name"]] = {"color": colors[part["name"]], "alpha": 1.0}
	return specs

def apply_materials_from_specs(obj, specs, face_ranges):
	print(f"Applying materials to object: {obj.name}")
	for part_name in specs:
		if part_name not in face_ranges:
			continue

		color = specs[part_name]["color"]
		alpha = specs[part_name]["alpha"]
		mat = create_orbital_material(f"OrbitalMat_{part_name}", color, alpha)
		mat_idx = len(obj.data.materials)
		obj.data.materials.append(mat)

		for face_idx in face_ranges[part_name]:
			obj.data.polygons[face_idx].material_index = mat_idx

		obj.data.update()