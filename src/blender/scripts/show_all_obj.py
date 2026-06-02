from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main(n_max: int = 4):
	rows = {}
	for n in range(1, n_max + 1):
		n_col = bl.scene.make_collection(f"n_{n}")
		rows[n] = {}
		for l in range(0, n):
			l_col = bl.scene.make_collection(f"n_{n}_l_{l}")
			rows[n][l] = []

			if l_col.name not in n_col.children: # coloca coleção de l dentro da coleção n, se ainda não estiver
				try:
					bpy.context.scene.collection.children.unlink(l_col)
				except Exception:
					pass
				n_col.children.link(l_col)

			for m in bl.layout.m_order(l):
				file_name = f"orbital_n{n}_l{l}_m{m}"
				try:
					verts, faces = bl.reader.load_obj_data(file_name)
				except FileNotFoundError:
					print(f"Arquivo não encontrado: {file_name}.obj")
					continue

				obj = bl.scene.create_mesh_object(verts, faces, name=file_name)
				bl.scene.move_to_collection(obj, l_col)
				rows[n][l].append(obj)
				bl.scene.smooth_object(obj)
				print(f"Carregado: {file_name}.obj")
	bl.layout.arrange_orbital_grid(rows)

main()