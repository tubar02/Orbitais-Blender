import numpy as np

import src.cli_save as sv
import src.grid.space as sp
import src.io.export as xp
import src.physics.atomic_orbitals as orb
import src.physics.density as den
import src.utils.plot as plt

def main():
	print("\nBem-vindo ao gerador de orbitais atômicos!\n")
	print("Selecione a opção desejada:")
	print("1: Gerar orbitais automaticamente")
	print("2: Gerar orbital personalizado")
	option = int(input("Digite o número da opção: "))
	print("\n")

	space = sp.Space()

	if option == 1:
		for n in range(1, 5):
			space.static_space_update(n)
			for l in range(0, n):
				for m in range(-l, l + 1):
					wavefunction = orb.hydrogen_wavefunction(n, l, m, space)
					density = den.probability_density(wavefunction, True, m=m)
					level = 0.01 * np.max(density)
					xp.save_obj(space, density, f"orbital_n{n}_l{l}_m{m}", level=level)
					print(f"Gerado orbital n={n}, l={l}, m={m}")

	elif option == 2:
		n, l, m = map(int, input("Digite os números quânticos n, l e m (separados por espaço): ").split())
		print("\n")

		assert n > 0, "n deve ser um inteiro positivo"
		assert 0 <= l < n, "l deve ser um inteiro tal que 0 <= l < n"
		assert -l <= m <= l, "m deve ser um inteiro tal que -l <= m <= l"

		space.static_space_update(n)
		wavefunction = orb.hydrogen_wavefunction(n, l, m, space)
		density = den.probability_density(wavefunction, real=True, m=m)

		print("Deseja plotar a função de onda? (s/n)")
		if input().lower() == 's':
			mode = int(input("\nEscolha o modo de plotagem\n1: Scatter 3D\n2: Fatias 2D\n3: Isosuperfície\nDigite o número do modo: "))
			if mode == 1:
				plt.scatter3D(space, density)
			elif mode == 2:
				plt.slice_view(space, density)
			elif mode == 3:
				mask = density >= 0.01 * np.max(density)
				plt.scatter_masked(space, mask)
		
		print("\nDeseja salvar a função de onda em um arquivo? (s/n)")
		if input().lower() == 's':
			mode = sv.ask_save_mode()
			kwargs = sv.ask_save_kwargs(mode, density)
			args = (space, f"orbital_n{n}_l{l}_m{m}")
			xp.save_options(mode, *args, **kwargs)

if __name__ == '__main__':
	main()