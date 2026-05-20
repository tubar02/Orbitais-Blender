import numpy as np
from skimage.measure import marching_cubes

from src.grid.space import Space
import src.io.paths as io

def save_to_file(space: Space, mask: np.ndarray, nome_arq: str):
	points = np.column_stack((space.X[mask], space.Y[mask], space.Z[mask]))
	file_path = io.get_data_path(f"{nome_arq}.npy")
	np.savetxt(file_path, points, delimiter=",")

def save_obj(space: Space, func: np.ndarray, nome_arq: str, level: float = 0, mode: int = 1, percent: float | None = None):
	assert mode in (1, 2)

	dx = space.x[1] - space.x[0]
	dy = space.y[1] - space.y[0]
	dz = space.z[1] - space.z[0]

	verts, faces, _, _ = marching_cubes(func, level=level, spacing=(dx, dy, dz))
	
	verts[:, 0] += space.x.min()
	verts[:, 1] += space.y.min()
	verts[:, 2] += space.z.min()

	if mode == 1:
		file_path = io.get_data_path(f"{nome_arq}.obj")
	elif mode == 2:
		dir_path = io.get_data_path(f"{nome_arq}")
		io.ensure_dir(dir_path)
		file_path = dir_path / f"{nome_arq}_lvl{int(100 * percent)}.obj"

	with open(file_path, 'w') as f:
		for vert in verts:
			f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
		for face in faces:
			f.write(f"f {face[0]} {face[1]} {face[2]}\n")