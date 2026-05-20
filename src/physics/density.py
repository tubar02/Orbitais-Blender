import numpy as np

def probability_density(wavefunction: np.ndarray, real: bool = False, m: int = 0) -> np.ndarray:
	# Densidade de probabilidade
	if real:
		if m > 0:
			wavefunction = np.real(wavefunction)
		elif m < 0:
			wavefunction = np.imag(wavefunction)
	density = np.abs(wavefunction) ** 2
	return density