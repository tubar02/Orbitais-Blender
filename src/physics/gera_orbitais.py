import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import src.utils.io_utils as io

# Parâmetros
TAM_ESPACO = 10
NUM_DIV = 250
ORIGEM = 0

# Gera eixos de coordenadas
x = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
y = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
z = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)

# Gera espaço euclidiano
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

arbitrary_scalar = np.cos(X) + np.exp(-Y**2) + np.sin(Z)

def plot_scalar_func(func: np.ndarray, mode: int = 1, mask: np.ndarray = None):
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

def save_to_file(mask: np.ndarray, nome_arq: str):
	points = np.column_stack((X[mask], Y[mask], Z[mask]))
	file_path = io.get_data_path(f"{nome_arq}.npy")
	np.savetxt(file_path, points, delimiter=",")

def main():
	'''
	r = float(input("Digite o raio da esfera: "))
	func = sphere(r)
	mascara = threshold_3d(func, tol=5e-2)
	mode = int(input("Escolha o modo de visualização (1: scatter, 2: slice, 3: masked scatter): "))
	plot_scalar_func(func, mode, mascara)
	# Salvar pontos em arquivo
	option = input("Deseja salvar os pontos em um arquivo? (s/n): ")
	if option.lower() == 's':
		nome_arq = input("Digite o nome do arquivo (sem extensão): ")
		save_to_file(mascara, nome_arq)
	print("Programa finalizado.")

	'''
	mascara = threshold_3d(arbitrary_scalar, tol=1e-2)
	#plot_scalar_func(arbitrary_scalar, mode=3, mask=mascara)
	save_to_file(mascara, "arbitrary_points2")
	

if __name__ == '__main__':
	main()