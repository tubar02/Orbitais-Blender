import numpy as np
import matplotlib.pyplot as plt

# Parâmetros
TAM_ESPACO = 10
NUM_DIV = 100
ORIGEM = 0

# Gera eixo de coordenadas
x = np.linspace(ORIGEM, TAM_ESPACO, NUM_DIV)
y = np.linspace(ORIGEM, TAM_ESPACO, NUM_DIV)
z = np.linspace(ORIGEM, TAM_ESPACO, NUM_DIV)

X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

arbitrary_scalar = X - (2 * Y) + X * Z

def plot_scalar_func(arbitrary_scalar: np.ndarray):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(X, Y, Z, c=arbitrary_scalar)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    plt.show()

def sphere(R: int) -> int:
    pass

def main():
    plot_scalar_func(arbitrary_scalar)

if __name__ == '__main__':
    main()