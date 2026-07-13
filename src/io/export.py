from pathlib import Path
import numpy as np

from src.grid.space import Space
import src.io.paths as io

def save_point_cloud(space: Space, nome_arq: str, mask: np.ndarray):
	points = np.column_stack((space.X[mask], space.Y[mask], space.Z[mask]))
	file_path = io.get_path(f"{nome_arq}.npy", io.POINT_CLOUD_DIR)
	np.savetxt(file_path, points, delimiter=",")

def write_obj(file_path: Path, vertices: np.ndarray, faces: np.ndarray):
	with open(file_path, 'w') as f:
		for vert in vertices:
			f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
		for face in faces:
			f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def save_obj(space: Space, nome_arq: str, func: np.ndarray, level: float):
	verts, faces = space.apply_marching_cubes(func, level)

	file_path = io.get_path(f"{nome_arq}.obj", io.SINGLE_OBJ_DIR)
	write_obj(file_path, verts, faces)

def save_batch(space: Space, nome_dir: str, func: np.ndarray, layers: int = 10, start_percent: float = 0.01):
	levels = np.linspace(start_percent * np.max(func), np.max(func), layers, endpoint=False)
	percents = np.round(np.linspace(0.01, 1.0, 10, endpoint=False) * 100).astype(int)

	dir_path = io.get_path(f"{nome_dir}", io.BATCH_OBJ_DIR)
	io.ensure_dir(dir_path)

	for level, percent in zip(levels, percents):
		verts, faces = space.apply_marching_cubes(func, level)
		file_path = dir_path / f"lvl{percent}.obj"
		write_obj(file_path, verts, faces)

SAVE_MODES = {
	"point_cloud": lambda *args, **ctx: save_point_cloud(
		*args,
		mask=ctx["mask"]
	),
	"single_obj": lambda *args, **ctx: save_obj(
		*args,
		func=ctx["func"],
		level=ctx.get("level", 0.01 * np.max(ctx["func"]))
	),
	"batch_obj": lambda *args, **ctx: save_batch(
		*args,
		func=ctx["func"],
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