import numpy as np

import src.cli_save as sv
import src.grid.space as sp
import src.io.export as xp
import src.utils.plot as plt
import src.generation as gen

def main():
	print("\nBem-vindo ao gerador de orbitais atômicos!\n")
	print("Selecione a opção desejada:")
	print("1: Gerar orbitais automaticamente")
	print("2: Gerar orbital personalizado")
	option = int(input("Digite o número da opção: "))
	print("\n")

	space = gen.create_space()

	if option == 1:
		n_max = input("\nDigite o valor máximo de n para gerar os orbitais (ex: 4): ")
		if not n_max:
			n_max = 4
		else:
			n_max = int(n_max)
			assert n_max > 0, "n_max deve ser um inteiro positivo"

		percent = input("Digite a porcentagem do valor máximo para a isossuperfície (0-100) (padrão: 1): ")
		if not percent:
			percent = 0.01
		else:
			percent = float(percent) / 100
			assert 0 < percent < 1, "percent deve ser um número entre 0 e 100"

		print("\n")
		gen.auto_orbitals(n_max=n_max, percent=percent, space=space)

	elif option == 2:
		n, l, m = map(int, input("\nDigite os números quânticos n, l e m (separados por espaço): ").split())
		print("\n")

		assert n > 0, "n deve ser um inteiro positivo"
		assert 0 <= l < n, "l deve ser um inteiro tal que 0 <= l < n"
		assert -l <= m <= l, "m deve ser um inteiro tal que -l <= m <= l"

		wavefunction, density = gen.generate_orbital(space, n, l, m)

		print("\nDeseja plotar a função de onda? (s/n)")
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