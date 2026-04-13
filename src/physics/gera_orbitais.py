import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Parâmetros
TAM_ESPACO = 10
NUM_DIV = 200
ORIGEM = 0

# Gera eixos de coordenadas
x = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
y = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)
z = np.linspace(ORIGEM - TAM_ESPACO, ORIGEM + TAM_ESPACO, NUM_DIV)

# Gera espaço euclidiano
X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

arbitrary_scalar = X - (2 * Y) + X * Z

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

def main():
    func = sphere(3)
    mascara = threshold_3d(func, tol=1e-1)
    plot_scalar_func(func, 3, mascara)

if __name__ == '__main__':
    main()