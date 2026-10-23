from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

import src.blender as bl

def main(mode: str, basis: str):
	orbitals = bl.loader.load_all_orbitals(basis, mode)
	rows = bl.layout.group_orbitals(orbitals)
	bl.layout.arrange_orbital_grid(rows)
	bl.scene.organize_collections(orbitals)
	bl.exporter.export_many_fbx(orbitals, mode)

main("signed", "real")