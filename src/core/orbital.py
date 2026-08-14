import numpy as np
from scipy.special import sph_harm_y, genlaguerre, factorial

from dataclasses import dataclass, field
from enum import Enum

from src.grid.space import Space
from src.physics.atomic_orbitals import normalization

A_0 = 1 # Raio de Bohr (normalizado)

class OrbitalBasis(Enum):
	REAL = "real"
	COMPLEX = "complex"

@dataclass
class Orbital:
	n: int
	l: int
	m: int
	space: Space
	basis: OrbitalBasis = OrbitalBasis.REAL

	wavefunction: np.ndarray = field(init=False, repr=False)
	density: np.ndarray = field(init=False, repr=False)

	def __post_init__(self):
		self._validate()
		self._calculate()

	def _validate(self):
		if self.n <= 0:
			raise ValueError("O número quântico principal n deve ser positivo.")
		if self.l < 0 or self.l >= self.n:
			raise ValueError("O número quântico azimutal l deve estar no intervalo [0, n-1].")
		if abs(self.m) > self.l:
			raise ValueError("O número quântico magnético m deve estar no intervalo [-l, l].")

	def _calculate(self):
		radial = self._radial_part()
		angular = self._angular_part()

		self.wavefunction = radial * angular
		self.density = np.abs(self.wavefunction) ** 2

	def _normalization(self) -> float:
		# Normalização para as funções de onda atômicas
		normal = np.sqrt((2 / (self.n * A_0)) ** 3 * factorial(self.n - self.l - 1) / (2 * self.n * factorial(self.n + self.l)))
		return normal

	def _radial_part(self) -> np.ndarray:
		# Parte radial das funções de onda atômicas
		radial = np.zeros_like(self.space.R)
		normal = self._normalization()
		laguerre = genlaguerre(self.n - self.l - 1, 2 * self.l + 1)
		radial = normal * ((2 * self.space.R) / (self.n * A_0)) ** self.l * np.exp(-self.space.R / (self.n * A_0)) * laguerre((2 * self.space.R) /(self.n * A_0))
		return radial

	def _angular_part(self) -> np.ndarray:
		# Parte angular das funções de onda atômicas
		if self.basis == OrbitalBasis.COMPLEX:
			return self._complex_angular_part()
		elif self.basis == OrbitalBasis.REAL:
			return self._real_angular_part()

		raise ValueError(f"Base desconhecida: {self.basis}")

	def _complex_angular_part(self) -> np.ndarray:
		# Parte angular das funções de onda atômicas (complexa)
		angular = sph_harm_y(self.l, self.m, self.space.THETA, self.space.PHI)
		return angular

	def _real_angular_part(self) -> np.ndarray:
		pass