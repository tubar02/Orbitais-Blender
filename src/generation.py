import numpy as np
from tqdm import tqdm, trange
from rich.console import Console
import time
from functools import wraps

import src.grid.space as sp
import src.io.export as xp
import src.physics.atomic_orbitals as orb
import src.physics.density as den

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

@acompanha("Criando função de onda")
def create_wavefunction(space: sp.Space, n: int, l: int, m: int) -> np.ndarray:
	return orb.hydrogen_wavefunction(n, l, m, space)

@acompanha("Calculando densidade")
def calculate_density(wavefunction: np.ndarray, real: bool = False, m: int = 0) -> np.ndarray:
	return den.probability_density(wavefunction, real, m)

def generate_orbital(space: sp.Space, n: int, l: int, m: int, real: bool = True, verbose: bool = True) -> tuple[np.ndarray, np.ndarray]:
	if verbose:
		atualiza_space(space, n)
		wavefunction = create_wavefunction(space, n, l, m)
		density = calculate_density(wavefunction, real=real, m=m)
	else:
		space.static_space_update(n)
		wavefunction = orb.hydrogen_wavefunction(n, l, m, space)
		density = den.probability_density(wavefunction, real=real, m=m)
	return wavefunction, density

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

			wavefunction = orb.hydrogen_wavefunction(n, l, m, space)
			density = den.probability_density(wavefunction, real=True, m=m)
			level = percent * np.max(density)
			xp.save_obj	(space, density, f"orbital_n{n}_l{l}_m{m}", level, leave=False)

def main():
	auto_orbitals(n_max=4, percent=0.01, space=create_space())

if __name__ == "__main__":
	main()