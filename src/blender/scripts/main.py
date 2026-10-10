from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main():
	n, l, m = 1, 0, 0
	suffix = "real"
	orbital_name = f"orbital_n{n}_l{l}_m{m}_{suffix}"
	mode = "point_cloud"

	bl.loader.load_single_orbital(orbital_name, mode)

main()