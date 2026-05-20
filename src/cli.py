import numpy as np

import src.grid.space as sp
import src.io.export as xp
import src.physics.atomic_orbitals as orb
import src.physics.density as den
import src.utils.plot as plt

def main():
	print("Bem-vindo ao gerador de orbitais atômicos!")
	print("Selecione a opção desejada:")
	print("1: Gerar orbitais automaticamente")
	print("2: Gerar orbital personalizado")
	option = int(input("Digite o número da opção: "))

	space = sp.Space()

	if option == 1:
		for n in range(1, 5):
			space.static_space_update(n)
			for l in range(0, n):
				for m in range(-l, l + 1):
					wavefunction = orb.hydrogen_wavefunction(n, l, m)
					density = den.probability_density(wavefunction, True, m=m)
					level = 0.01 * np.max(density)
					xp.save_obj(density, f"orbital_n{n}_l{l}_m{m}", level=level)
					print(f"Gerado orbital n={n}, l={l}, m={m}")

	elif option == 2:
		n, l, m = map(int, input("Digite os números quânticos n, l e m (separados por espaço): ").split())

		assert n > 0, "n deve ser um inteiro positivo"
		assert 0 <= l < n, "l deve ser um inteiro tal que 0 <= l < n"
		assert -l <= m <= l, "m deve ser um inteiro tal que -l <= m <= l"

		wavefunction = orb.hydrogen_wavefunction(n, l, m, space)
		density = den.probability_density(wavefunction, real=True, m=m)
		percent = 0.01 * np.max(density)
		mask = density >= percent

		print("Deseja plotar a função de onda? (s/n)")
		if input().lower() == 's':
			mode = int(input("\nEscolha o modo de plotagem\n1: Scatter 3D\n2: Fatias 2D\n3: Isosuperfície\nDigite o número do modo: "))
			if mode == 1:
				plt.scatter3D(space, density)
			elif mode == 2:
				plt.slice_view(space, density)
			elif mode == 3:
				plt.scatter_masked(space, mask)
		
		print("Deseja salvar a função de onda em um arquivo? (s/n)")
		if input().lower() == 's':
			mode = int(input("\nEscolha o modo\n1: Isossuperfície única\n2: Variação da porcentagem\nDigite o número do modo: "))
			if mode == 1:
				xp.save_obj(space, density, f"orbital_n{n}_l{l}_m{m}", level=percent)
			elif mode == 2:
				for i in range(10):
					xp.save_obj(space, density, f"orbital_n{n}_l{l}_m{m}", level=percent, mode=mode)
					percent += 0.1 * np.max(density)

if __name__ == '__main__':
	main()