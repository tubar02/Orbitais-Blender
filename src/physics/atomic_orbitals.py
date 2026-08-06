import numpy as np
from scipy.special import sph_harm_y, genlaguerre, factorial

from src.grid.space import Space

A_0 = 1 # Raio de Bohr (normalizado)

def normalization(n: int, l: int) -> float:
	# Normalização para as funções de onda atômicas
	normal = np.sqrt((2 / (n * A_0)) ** 3 * factorial(n - l - 1) / (2 * n * factorial(n + l)))
	return normal

def radial_part(n: int, l: int, r: np.ndarray) -> np.ndarray:
	# Parte radial das funções de onda atômicas
	radial = np.zeros_like(r)
	normal = normalization(n, l)
	laguerre = genlaguerre(n - l - 1, 2 * l + 1)
	radial = normal * ((2 * r) / (n * A_0)) ** l * np.exp(-r / (n * A_0)) * laguerre((2 * r) /(n * A_0))
	return radial

def angular_part(l: int, m: int, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
	# Parte angular das funções de onda atômicas
	angular = sph_harm_y(l, m, theta, phi)
	return angular

def hydrogen_wavefunction(n: int, l: int, m: int, space: Space) -> np.ndarray:
	# Função de onda do átomo de hidrogênio
	radial = radial_part(n, l, space.R)
	angular = angular_part(l, m, space.THETA, space.PHI)
	wavefunction = radial * angular
	return wavefunction