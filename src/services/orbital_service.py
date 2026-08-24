from tqdm import tqdm
from rich.console import Console
import time
from functools import wraps

import src.core.orbital as orb
import src.core.space as sp
import src.utils.plot as plt

def acompanha(desc: str | None= None):
	def deco(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			console = Console()
			t0 = time.perf_counter()
			with console.status(f"[bold green]{desc or func.__name__}..."):
				result = func(*args, **kwargs)
				console.log(f"{func.__name__} executado em {time.perf_counter() - t0:.2f} segundos")
			return result
		return wrapper
	return deco

@acompanha("Gerando orbital atômico")
def create_orbital(space: sp.Space, n: int, l: int, m: int, basis: orb.OrbitalBasis = orb.OrbitalBasis.REAL) -> orb.Orbital:
	space.static_space_update(n)
	return orb.Orbital(n, l, m, space, basis=basis)

def orbital_tasks(n_max: int):
	for n in range(1, n_max + 1):
		for l in range(0, n):
			for m in range(-l, l + 1):
				yield n, l, m

def generate_orbitals(space: sp.Space, n_max: int, basis: orb.OrbitalBasis = orb.OrbitalBasis.REAL):
	current_n = None
	for n, l, m in orbital_tasks(n_max):
		if n != current_n:
			space.static_space_update(n	)
			current_n = n

		yield orb.Orbital(n, l, m, space, basis=basis)

def generate_and_export_orbitals(space: sp.Space, n_max: int, basis: orb.OrbitalBasis):
	orbitals = generate_orbitals(space, n_max, basis)
	total = sum(n ** 2 for n in range(1, n_max + 1))  # Total de orbitais até n_max
	with tqdm(orbitals, "Gerando orbitais", total=total, colour="green") as pbar:
		it = iter(pbar)
		for n, l, m in orbital_tasks(n_max):
			pbar.set_postfix_str(f"n = {n}, l = {l}, m = {m}")
			orbital = next(it)
			# Aqui você pode adicionar a lógica para exportar o orbital, se necessário
			plt.slice_view(space, orbital.density)  # Exemplo de plotagem da densidade do orbital

def main():
	space = sp.Space()
	generate_and_export_orbitals(space, n_max=4, basis=orb.OrbitalBasis.REAL)
	
if __name__ == "__main__":
	main()