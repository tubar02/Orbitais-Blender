from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main(mode: str,n_max: int = 4, suffix = "real"):
	rows = {}
	for n in range(1, n_max + 1):
		n_col = bl.scene.make_collection(f"n_{n}")
		rows[n] = {}
		for l in range(0, n):
			l_col = bl.scene.make_collection(f"n_{n}_l_{l}")
			bl.scene.move_collection_to_collection(l_col, n_col)

			rows[n][l] = []

			for m in bl.layout.m_order(l):
				orbital_name = f"orbital_n{n}_l{l}_m{m}_{suffix}"
				obj = bl.loader.load_single_orbital(orbital_name, mode)
				bl.scene.move_to_collection(obj, l_col)
				rows[n][l].append(obj)
				bl.scene.smooth_object(obj)
				print(f"Carregado: {orbital_name}.obj")
	bl.layout.arrange_orbital_grid(rows)

main("point_cloud", 2)