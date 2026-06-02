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