from tqdm import tqdm
from rich.console import Console
import time
from functools import wraps
from typing import Callable

import src.core.orbital as orb
import src.core.space as sp
import src.core.orbital_selection as sel
import src.io.export as xp

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
def create_orbital(space: sp.Space, n: int, l: int, m: int, basis: orb.OrbitalBasis = orb.OrbitalBasis.REAL, num_div: int | None = None) -> orb.Orbital:
	space.static_space_update(n, num_div)
	orbital = orb.Orbital(n, l, m, space, basis=basis)
	return orbital

def validate_interval(n_min: int, n_max: int):
	try:
		n_min = int(n_min)
		n_max = int(n_max)
	except (ValueError, TypeError) as exc:
		raise ValueError("Os limites devem ser inteiros.") from exc
	if not (1 <= n_min <= n_max):
			raise ValueError("O intervalo deve satisfazer 1 <= n_min <= n_max.")
	return n_min, n_max

def orbital_tasks(n_max: int, n_min: int = 1):
	selection = {"type": "range", "n_min": n_min, "n_max": n_max}
	yield from sel.iter_orbitals(selection)

def generate_orbitals(space: sp.Space, n_max: int, basis: orb.OrbitalBasis = orb.OrbitalBasis.REAL, n_min: int = 1):
	current_n = None
	for n, l, m in orbital_tasks(n_max, n_min):
		if n != current_n:
			space.static_space_update(n	)
			current_n = n

		yield orb.Orbital(n, l, m, space, basis=basis)

def generate_and_export_orbitals(space: sp.Space, n_max: int, basis: orb.OrbitalBasis, n_min: int = 1, exporter: Callable[[orb.Orbital], None] = xp.fake_exporter):
	n_min, n_max = validate_interval(n_min, n_max)
	orbitals = generate_orbitals(space, n_max, basis, n_min)
	total = sum(n ** 2 for n in range(n_min, n_max + 1))  # Total de orbitais até n_max
	with tqdm(orbitals, "Gerando orbitais", total=total, colour="green") as pbar:
		it = iter(pbar)
		for n, l, m in orbital_tasks(n_max, n_min):
			pbar.set_postfix_str(f"n = {n}, l = {l}, m = {m}")
			orbital = next(it)
			exporter(orbital)

def main():
	space = sp.Space()
	mode = "single_obj"
	#kwargs = sv.ask_save_kwargs(mode)
	base_exporter = xp.SAVE_MODES[mode]
	#exporter = partial(base_exporter)
	generate_and_export_orbitals(space, n_max=4, basis=orb.OrbitalBasis.REAL, exporter=base_exporter)
	
if __name__ == "__main__":
	main()