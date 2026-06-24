import numpy as np
from skimage.measure import marching_cubes

class Space:
	def _update(self):
		self.x: np.ndarray = np.linspace(self.origem[0] - self.tam_espaco, self.origem[0] + self.tam_espaco, self.num_div)
		self.y: np.ndarray = np.linspace(self.origem[1] - self.tam_espaco, self.origem[1] + self.tam_espaco, self.num_div)
		self.z: np.ndarray = np.linspace(self.origem[2] - self.tam_espaco, self.origem[2] + self.tam_espaco, self.num_div)

		self.div: tuple[int, int, int] = (self.x[1] - self.x[0], self.y[1] - self.y[0], self.z[1] - self.z[0])

		self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing="ij")

		self.R = np.sqrt(self.X**2 + self.Y**2 + self.Z**2)
		self.THETA = np.zeros_like(self.R)
		self.THETA[self.R != 0] = np.arccos(self.Z[self.R != 0] / self.R[self.R != 0])
		self.PHI = np.arctan2(self.Y, self.X)

	def __init__(self, tam_espaco=15, num_div=50, origem=(0, 0, 0)):
		self.tam_espaco: int = tam_espaco
		self.num_div: int = num_div
		self.origem: tuple[float, float, float] = origem
		self._update()
	
	def static_space_update(self, n: int):
		if n < 4:
			self.num_div = 500
		else:
			self.num_div = 500 + (n - 3) * 100
		
		self.tam_espaco = 5 + (n - 1) * 10
		self._update()

	def apply_marching_cubes(self, func: np.ndarray, level: float):
		verts, faces, _, _ = marching_cubes(func, level, spacing=self.div)
		verts[:, 0] = self.x.min() # Ajusta para as coordenadas do espaço
		verts[:, 1] = self.y.min()
		verts[:, 2] = self.z.min()
		return verts, faces