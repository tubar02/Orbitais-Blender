import matplotlib.pyplot as plt # Funções de plotagem
from matplotlib.widgets import Slider

import numpy as np # Manipulação matemática
from scipy.special import sph_harm_y, genlaguerre, factorial

from skimage.measure import marching_cubes # Para extração de isosuperfícies

import src.utils.io_utils as io

# Parâmetros
TAM_ESPACO = 10
NUM_DIV = 500
ORIGEM = 0
A_0 = 1 # Raio de Bohr

# Gera eixos de coordenadas
x = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
y = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
z = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)

# Gera espaço euclidiano
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

arbitrary_scalar = np.cos(X) + np.exp(-Y**2) + np.sin(Z)

R = np.sqrt(X**2 + Y**2 + Z**2)
THETA = np.zeros_like(R)
THETA[R != 0] = np.arccos(Z[R != 0] / R[R != 0])
PHI = np.arctan2(Y, X)

def atualiza_espaco(n: int):
	global TAM_ESPACO, NUM_DIV, x, y, z, X, Y, Z, R, THETA, PHI

	if n < 4:
		pass
	else:
		NUM_DIV = 500 + (n - 3) * 100
	
	TAM_ESPACO = 5 + (n - 1) * 10
	
	x = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
	y = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
	z = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
	X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
	R = np.sqrt(X**2 + Y**2 + Z**2)
	THETA = np.zeros_like(R)
	THETA[R != 0] = np.arccos(Z[R != 0] / R[R != 0])
	PHI = np.arctan2(Y, X)

def plot_scalar_func(func: np.ndarray, mode: int = 1, mask: np.ndarray | None = None):
	global X, Y, Z, x, y, z
	if mode == 1:
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		ax.scatter(X, Y, Z, c=func)
		ax.set_xlabel("x")
		ax.set_ylabel("y")
		ax.set_zlabel("z")

	elif mode == 2:
		# Figura
		fig, ax = plt.subplots()
		plt.subplots_adjust(bottom=0.25)

		# Fatia inicial
		k0 = NUM_DIV // 2
		img = ax.imshow(func[:, :, k0], extent=[x.min(), x.max(), y.min(), y.max()])
		ax.set_title(f"z = {z[k0]:.2f}")
		plt.colorbar(img)

		# Slider
		ax_slider = plt.axes((0.4, 0.1, 0.2, 0.03))
		slider = Slider(ax_slider, "z index", 0, NUM_DIV - 1, valinit=k0, valstep=1)

		# Atualizador
		def update(val):
			k = int(slider.val)
			img.set_data(func[:, :, k])
			ax.set_title(f"z = {z[k]:.2f}")
			fig.canvas.draw_idle()
		slider.on_changed(update)

	elif mode == 3:
		x_plot, y_plot, z_plot = X[mask], Y[mask], Z[mask]
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		ax.scatter(x_plot, y_plot, z_plot)
		ax.set_xlabel("x")
		ax.set_ylabel("y")
		ax.set_zlabel("z")

	plt.show()

def sphere(R: int) -> np.ndarray:
	func = X ** 2 + Y ** 2 + Z ** 2 - R ** 2
	return func

def threshold_3d(func: np.ndarray, threshold: int = 0, tol: float = 1e-1) -> np.ndarray:
	mask = np.abs(func - threshold) < tol
	return mask

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

def hydrogen_wavefunction(n: int, l: int, m: int) -> np.ndarray:
	# Função de onda do átomo de hidrogênio
	radial = radial_part(n, l, R)
	angular = angular_part(l, m, THETA, PHI)
	wavefunction = radial * angular
	return wavefunction

def probability_density(wavefunction: np.ndarray, real: bool = False, m: int = 0) -> np.ndarray:
	# Densidade de probabilidade
	if real:
		if m > 0:
			wavefunction = np.real(wavefunction)
		elif m < 0:
			wavefunction = np.imag(wavefunction)
	density = np.abs(wavefunction) ** 2
	return density

def save_to_file(mask: np.ndarray, nome_arq: str):
	points = np.column_stack((X[mask], Y[mask], Z[mask]))
	file_path = io.get_data_path(f"{nome_arq}.npy")
	np.savetxt(file_path, points, delimiter=",")

def save_obj(func: np.ndarray, nome_arq: str, level: float = 0):
	dx = x[1] - x[0]
	dy = y[1] - y[0]
	dz = z[1] - z[0]

	verts, faces, _, _ = marching_cubes(func, level=level, spacing=(dx, dy, dz))
	
	verts[:, 0] += x.min()
	verts[:, 1] += y.min()
	verts[:, 2] += z.min()

	file_path = io.get_data_path(f"{nome_arq}.obj")
	with open(file_path, 'w') as f:
		for vert in verts:
			f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
		for face in faces:
			f.write(f"f {face[0]} {face[1]} {face[2]}\n")

def main():
	n, l, m = map(int, input("Digite os números quânticos n, l e m (separados por espaço): ").split())

	assert n > 0, "n deve ser um inteiro positivo"
	assert 0 <= l < n, "l deve ser um inteiro tal que 0 <= l < n"
	assert -l <= m <= l, "m deve ser um inteiro tal que -l <= m <= l"

	atualiza_espaco(n)

	wavefunction = hydrogen_wavefunction(n, l, m)
	density = probability_density(wavefunction, True, m)
	level = 0.01 * np.max(density)
	mask = density >= level

	print("Deseja plotar a função de onda? (s/n)")
	if input().lower() == 's':
		mode = int(input("\nEscolha o modo de plotagem\n1: Scatter 3D\n2: Fatias 2D\n3: Isosuperfície\nDigite o número do modo: "))
		plot_scalar_func(density, mode=mode, mask=mask)
	
	print("Deseja salvar os pontos da isosuperfície em um arquivo? (s/n)")
	if input().lower() == 's':
		save_obj(density, f"orbital_n{n}_l{l}_m{m}", level=level)

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
	auto_orbitals()