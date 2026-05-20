import matplotlib.pyplot as plt # Funções de plotagem
from matplotlib.widgets import Slider

import numpy as np # Manipulação matemática
from scipy.special import sph_harm_y, genlaguerre, factorial

from skimage.measure import marching_cubes # Para extração de isosuperfícies

import src.io.paths as io


def probability_density(wavefunction: np.ndarray, real: bool = False, m: int = 0) -> np.ndarray:
	# Densidade de probabilidade
	if real:
		if m > 0:
			wavefunction = np.real(wavefunction)
		elif m < 0:
			wavefunction = np.imag(wavefunction)
	density = np.abs(wavefunction) ** 2
	return density

def main():
	n, l, m = map(int, input("Digite os números quânticos n, l e m (separados por espaço): ").split())

	assert n > 0, "n deve ser um inteiro positivo"
	assert 0 <= l < n, "l deve ser um inteiro tal que 0 <= l < n"
	assert -l <= m <= l, "m deve ser um inteiro tal que -l <= m <= l"

	atualiza_espaco(n)

	wavefunction = hydrogen_wavefunction(n, l, m)
	density = probability_density(wavefunction, True, m)
	percent = 0.01
	level = percent * np.max(density)
	mask = density >= level

	print("Deseja plotar a função de onda? (s/n)")
	if input().lower() == 's':
		mode = int(input("\nEscolha o modo de plotagem\n1: Scatter 3D\n2: Fatias 2D\n3: Isosuperfície\nDigite o número do modo: "))
		plot_scalar_func(density, mode=mode, mask=mask)
	
	print("Deseja salvar a função de onda em um arquivo? (s/n)")
	if input().lower() == 's':
		mode = int(input("\nEscolha o modo\n1: Isossuperfície única\n2: Variação da porcentagem\nDigite o número do modo: "))

		if mode == 1:
			save_obj(density, f"orbital_n{n}_l{l}_m{m}", level=level)
		elif mode == 2:
			for i in range(10):
				save_obj(density, f"orbital_n{n}_l{l}_m{m}", level=level, mode=mode, percent=percent)
				percent += 0.1
				level = percent * np.max(density)

def _main():
	mascara = threshold_3d(arbitrary_scalar, tol=1e-2)
	plot_scalar_func(arbitrary_scalar, mode=3, mask=mascara)
	save_to_file(mascara, "arbitrary_points2")
	save_obj(arbitrary_scalar, "arbitrary_points2")

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