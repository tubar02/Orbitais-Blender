import matplotlib.pyplot as plt # Funções de plotagem
from matplotlib.widgets import Slider

import numpy as np # Manipulação matemática
from scipy.special import sph_harm_y, genlaguerre, factorial

from skimage.measure import marching_cubes # Para extração de isosuperfícies

import src.io.paths as io

def auto_orbitals():
	for n in range(1, 5):
		atualiza_espaco(n)
		for l in range(0, n):
			for m in range(-l, l + 1):
				wavefunction = hydrogen_wavefunction(n, l, m)
				density = probability_density(wavefunction, True, m=m)
				level = 0.01 * np.max(density)
				save_obj(density, f"orbital_n{n}_l{l}_m{m}", level=level)
				print(f"Gerado orbital n={n}, l={l}, m={m}")

if __name__ == '__main__':
	main()