from pathlib import Path
import numpy as np
from skimage.measure import marching_cubes

from src.grid.space import Space
import src.io.paths as io

def save_to_file(space: Space, mask: np.ndarray, nome_arq: str):
	points = np.column_stack((space.X[mask], space.Y[mask], space.Z[mask]))
	file_path = io.get_path(f"{nome_arq}.npy")
	np.savetxt(file_path, points, delimiter=",")

def write_obj(file_path: Path, vertices: np.ndarray, faces: np.ndarray):
	with open(file_path, 'w') as f:
		for vert in vertices:
			f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
		for face in faces:
			f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def save_obj(space: Space, func: np.ndarray, nome_arq: str, level: float):
	dx, dy, dz = space.div
	verts, faces, _, _ = marching_cubes(func, level=level, spacing=(dx, dy, dz))
	
	verts[:, 0] += space.x.min() # Ajusta as coordenadas para o sistema de coordenadas do espaço
	verts[:, 1] += space.y.min()
	verts[:, 2] += space.z.min()

	file_path = io.get_path(f"{nome_arq}.obj")
	write_obj(file_path, verts, faces)

def save_batch(space: Space, func: np.ndarray, nome_dir: str, layers: int = 10, start_percent: float = 0.01):
	levels = np.linspace(start_percent * np.max(func), np.max(func), layers, endpoint=False)
	percents = np.round(np.linspace(0.01, 1.0, 10, endpoint=False) * 100).astype(int)

	dx, dy, dz = space.div

	for level, percent in zip(levels, percents):
		verts, faces, _, _ = marching_cubes(func, level=level, spacing=(dx, dy, dz))

		verts[:, 0] += space.x.min() # Ajusta as coordenadas para o sistema de coordenadas do espaço
		verts[:, 1] += space.y.min()
		verts[:, 2] += space.z.min()

		dir_path = io.get_path(f"{nome_dir}")
		io.ensure_dir(dir_path)
		file_path = dir_path / f"lvl{percent}.obj"
		write_obj(file_path, verts, faces)

def main():
	percents = np.round(np.linspace(0.01, 1.0, 10, endpoint=False) * 100).astype(int)

	print(percents)
	
if __name__ == "__main__":
	main()