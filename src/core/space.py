import numpy as np
from skimage.measure import marching_cubes

class Space:
	def _validate(self):
		if not isinstance(self.num_div, int) or self.num_div < 2:
			raise ValueError("num_div deve ser um inteiro >= 2.")

		if not np.isfinite(self.tam_espaco) or self.tam_espaco <= 0:
			raise ValueError("tam_espaco deve ser positivo e finito.")

		if np.shape(self.origem) != (3,):
			raise ValueError("origem deve conter três coordenadas.")

		if not np.all(np.isfinite(self.origem)):
			raise ValueError("As coordenadas da origem devem ser finitas.")

	def _update(self):
		self._validate()
		
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
	
	def static_space_update(self, n: int, num_div: int | None = None):
		if num_div is None:
			if n < 4:
				self.num_div = 500
			else:
				self.num_div = 500 + (n - 3) * 100
		else:
			self.num_div = num_div

		self.tam_espaco = 5 + (n - 1) * 10
		self._update()

	def apply_marching_cubes(self, scalar_field: np.ndarray, level: float, gradient_direction: str = "ascent"):
		if scalar_field.shape != self.R.shape:
			raise ValueError("O campo escalar deve ter a mesma forma que o espaço.")

		if not np.all(np.isfinite(scalar_field)):
			raise ValueError("O campo escalar deve conter apenas valores finitos.")

		min_value, max_value = np.min(scalar_field), np.max(scalar_field)
		if not (min_value < level < max_value):
			raise ValueError(f"O nível {level} deve estar entre o valor mínimo {min_value} e o valor máximo {max_value} do campo escalar.")

		verts, faces, _, _ = marching_cubes(scalar_field, level, spacing=self.div, gradient_direction=gradient_direction)
		verts[:, 0] += self.x.min() # Ajusta para as coordenadas do espaço
		verts[:, 1] += self.y.min()
		verts[:, 2] += self.z.min()
		return verts, faces