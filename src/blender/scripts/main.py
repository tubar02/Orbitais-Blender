from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n, l, m = 3, 2, 0
	suffix = "real"
	orbital_name = f"orbital_n{n}_l{l}_m{m}_{suffix}"
	mode = "signed_obj"

	obj = bl.loader.load_single_orbital(orbital_name, mode)
	output_path = bl.exporter.export_fbx(obj, orbital_name, mode)
	print(f"Succesfully exported obj to {output_path}")

main()