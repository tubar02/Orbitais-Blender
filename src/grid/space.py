import numpy as np # Manipulação matemática

class Space:
	def _update(self):
		self.x = np.linspace(self.origem - self.tam_espaco, self.origem + self.tam_espaco, self.num_div)
		self.y = np.linspace(self.origem - self.tam_espaco, self.origem + self.tam_espaco, self.num_div)
		self.z = np.linspace(self.origem - self.tam_espaco, self.origem + self.tam_espaco, self.num_div)

		self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing="ij")

		self.R = np.sqrt(self.X**2 + self.Y**2 + self.Z**2)
		self.THETA = np.zeros_like(self.R)
		self.THETA[self.R != 0] = np.arccos(self.Z[self.R != 0] / self.R[self.R != 0])
		self.PHI = np.arctan2(self.Y, self.X)

	def __init__(self, tam_espaco=15, num_div=500, origem=0):
		self.tam_espaco = tam_espaco
		self.num_div = num_div
		self.origem = origem
		self._update()
	
	def static_space_update(self, n: int):
		if n < 4:
			pass
		else:
			self.num_div = 500 + (n - 3) * 100
		
		self.tam_espaco = 5 + (n - 1) * 10
		self._update()