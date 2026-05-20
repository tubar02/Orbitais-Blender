import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

from src.grid.space import Space

def scatter3D(space: Space, func: np.ndarray):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(space.X, space.Y, space.Z, c=func)
	ax.set_xlabel("x")
	ax.set_ylabel("y")
	ax.set_zlabel("z")
	plt.show()

def slice_view(space: Space, func: np.ndarray):# Figura
	fig, ax = plt.subplots()
	plt.subplots_adjust(bottom=0.25)

	# Fatia inicial
	k0 = space.num_div // 2
	img = ax.imshow(func[:, :, k0], extent=(space.x.min(), space.x.max(), space.y.min(), space.y.max()))
	ax.set_title(f"z = {space.z[k0]:.2f}")
	plt.colorbar(img)

	# Slider
	ax_slider = plt.axes((0.4, 0.1, 0.2, 0.03))
	slider = Slider(ax_slider, "z index", 0, space.num_div - 1, valinit=k0, valstep=1)

	# Atualizador
	def update(val):
		k = int(slider.val)
		img.set_data(func[:, :, k])
		ax.set_title(f"z = {space.z[k]:.2f}")
		fig.canvas.draw_idle()
	slider.on_changed(update)
	plt.show()

def scatter_masked(space: Space, mask: np.ndarray):
	x_plot, y_plot, z_plot = space.X[mask], space.Y[mask], space.Z[mask]
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(x_plot, y_plot, z_plot)
	ax.set_xlabel("x")
	ax.set_ylabel("y")
	ax.set_zlabel("z")
	plt.show()