from pathlib import Path
import sys
import bpy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n, l, m = 3, 2, -1
	suffix = "real"
	orbital_name = f"orbital_n{n}_l{l}_m{m}_{suffix}"
	mode = "batch_obj"

	bl.loader.load_single_orbital(orbital_name, mode)

main()