from pathlib import Path
import numpy as np
from tqdm import tqdm

from src.core.space import Space
import src.io.paths as io

def save_point_cloud(space: Space, nome_arq: str, mask: np.ndarray):
	points = np.column_stack((space.X[mask], space.Y[mask], space.Z[mask]))
	file_path = io.get_path(f"{nome_arq}.npy", io.POINT_CLOUD_DIR)
	np.savetxt(file_path, points, delimiter=",")

def write_obj(file_path: Path, vertices: np.ndarray, faces: np.ndarray, leave: bool = True):
	with open(file_path, 'w') as f:
		for vert in tqdm(vertices, desc=f"Salvando vértices em {file_path.name}", colour="green", leave=leave):  # Barra de progresso
			f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
		for face in tqdm(faces, desc=f"Salvando faces em {file_path.name}", colour="green", leave=leave):
			f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def save_obj(space: Space, nome_arq: str, scalar_field: np.ndarray, level: float, leave: bool = True):
	verts, faces = space.apply_marching_cubes(scalar_field, level)

	file_path = io.get_path(f"{nome_arq}.obj", io.SINGLE_OBJ_DIR)
	write_obj(file_path, verts, faces, leave=leave)

def save_batch(space: Space, nome_dir: str, scalar_field: np.ndarray, layers: int = 10, start_percent: float = 0.01):
	levels = np.linspace(start_percent * np.max(scalar_field), np.max(scalar_field), layers, endpoint=False)
	percents = np.round(np.linspace(0.01, 1.0, 10, endpoint=False) * 100).astype(int)

	dir_path = io.get_path(f"{nome_dir}", io.BATCH_OBJ_DIR)
	io.ensure_dir(dir_path)

	for level, percent in tqdm(list(zip(levels, percents)), desc=f"Salvando camadas em {nome_dir}", colour="cyan"):
		verts, faces = space.apply_marching_cubes(scalar_field, level)
		file_path = dir_path / f"lvl{percent}.obj"
		write_obj(file_path, verts, faces, leave=False)

SAVE_MODES = {
	"point_cloud": lambda *args, **ctx: save_point_cloud(
		*args,
		mask=ctx["mask"]
	),
	"single_obj": lambda *args, **ctx: save_obj(
		*args,
		scalar_field=ctx["scalar_field"],
		level=ctx.get("level", 0.01 * np.max(ctx["scalar_field"]))
	),
	"batch_obj": lambda *args, **ctx: save_batch(
		*args,
		scalar_field=ctx["scalar_field"],
		layers=ctx.get("layers", 10),
		start_percent=ctx.get("start_percent", 0.01)
	),
}

def save_options(mode: str, *args, **kwargs):
	try:
		SAVE_MODES[mode](*args, **kwargs)
	except KeyError:
		raise ValueError(f"Modo {mode} inexistente.")

def main():
	percents = np.round(np.linspace(0.01, 1.0, 10, endpoint=False) * 100).astype(int)

	print(percents)
	
if __name__ == "__main__":
	main()