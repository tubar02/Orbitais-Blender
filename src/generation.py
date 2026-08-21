import numpy as np
from tqdm import tqdm, trange
from rich.console import Console
import time
from functools import wraps

import src.grid.space as sp
import src.io.export as xp
import src.core.orbital as orb

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

@acompanha("Gerando instância de Space")
def create_space() -> sp.Space:
	return sp.Space()

@acompanha("Atualizando espaço")
def atualiza_space(space: sp.Space, n: int):
	space.static_space_update(n)
	return

@acompanha("Criando orbital atômico")
def create_orbital(space: sp.Space, n: int, l: int, m: int, basis: orb.OrbitalBasis = orb.OrbitalBasis.REAL) -> orb.Orbital:
	return orb.Orbital(n, l, m, space, basis=basis)

def orbital_tasks(n_max: int):
	for n in range(1, n_max + 1):
		for l in range(0, n):
			for m in range(-l, l + 1):
				yield n, l, m

def auto_orbitals(n_max: int, percent: float, space: sp.Space):
	tasks = list(orbital_tasks(n_max))
	current_n = None

	with tqdm(tasks, "Gerando orbitais", colour="green") as pbar:
		for n, l, m in pbar:
			if n != current_n:
				space.static_space_update(n)
				current_n = n

			pbar.set_postfix_str(f"n = {n}, l = {l}, m = {m}")

			orbital = create_orbital(space, n, l, m)
			density = orbital.density
			level = percent * np.max(density)
			xp.save_obj	(space, f"orbital_n{n}_l{l}_m{m}", density, level, leave=False)

def main():
	space = create_space()

	n, l, m = 3, 2, 1

	atualiza_space(space, n)

	orbital = create_orbital(space, n, l, m, basis=orb.OrbitalBasis.REAL)
	xp.save_obj(space, f"testeReal_n{n}_l{l}_m{m}", orbital.density, 0.01 * np.max(orbital.density))

	orbital2 = create_orbital(space, n, l, m, basis=orb.OrbitalBasis.COMPLEX)
	xp.save_obj(space, f"testeComplex_n{n}_l{l}_m{m}", orbital2.density, 0.01 * np.max(orbital2.density))

if __name__ == "__main__":
	main()