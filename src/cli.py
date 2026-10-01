import numpy as np

import src.cli_save as sv
import src.core.space as sp
import src.core.orbital as orb
import src.io.export as xp
import src.services.orbital_service as osrv
import src.utils.plot as plt

def main():
	print("\nBem-vindo ao gerador de orbitais atômicos!\n")

	print("Escolha a base de funções de onda:")
	print("1: Base real")
	print("2: Base complexa\n")
	basis_option = input("Digite o número da base desejada (padrão: 1): ")
	if not basis_option:
		basis_option = 1
	else:
		basis_option = int(basis_option)
	basis = orb.OrbitalBasis.REAL if basis_option == 1 else orb.OrbitalBasis.COMPLEX

	print("Selecione a opção desejada:")
	print("1: Gerar orbitais automaticamente")
	print("2: Gerar orbital personalizado")
	print("0: Sair\n")
	option = int(input("Digite o número da opção: "))
	print("\n")

	space = sp.Space()

	if option == 1:
		n_max = input("\nDigite o valor máximo de n para gerar os orbitais (ex: 4): ")
		if not n_max:
			n_max = 4
		else:
			n_max = int(n_max)
			assert n_max > 0, "n_max deve ser um inteiro positivo"

		mode = sv.ask_save_mode()
		exporter = xp.SAVE_MODES[mode]
		print("\n")
		osrv.generate_and_export_orbitals(space, n_max=n_max, basis=basis, exporter=exporter)

	elif option == 2:
		n, l, m = map(int, input("\nDigite os números quânticos n, l e m (separados por espaço): ").split())

		assert n > 0, "n deve ser um inteiro positivo"
		assert 0 <= l < n, "l deve ser um inteiro tal que 0 <= l < n"
		assert -l <= m <= l, "m deve ser um inteiro tal que -l <= m <= l"

		orbital = osrv.create_orbital(space, n, l, m, basis=basis)

		print("\nDeseja plotar a função de onda? (s/n)")
		if input().lower() == 's':
			mode = int(input("\nEscolha o modo de plotagem\n1: Scatter 3D\n2: Fatias 2D\n3: Isosuperfície\nDigite o número do modo: "))
			if mode == 1:
				plt.scatter3D(space, orbital.density)
			elif mode == 2:
				plt.slice_view(space, orbital.density)
			elif mode == 3:
				mask = orbital.density >= 0.01 * np.max(orbital.density)
				plt.scatter_masked(space, mask)
		
		print("\nDeseja salvar a função de onda em um arquivo? (s/n)")
		if input().lower() == 's':
			mode = sv.ask_save_mode()
			kwargs = sv.ask_save_kwargs(mode)
			args = (space, orbital.name, orbital.density)
			xp.save_options(mode, *args, **kwargs)

	elif option == 0:
		print("Saindo do programa...")
		return

	else:
		raise ValueError("Opção inválida.")

if __name__ == '__main__':
	main()