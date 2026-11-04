from collections.abc import Iterator

def bases_for_mode(mode: str, bases: list[str]) -> list[str]:
	"""Seleciona as bases compatíveis com o modo solicitado."""
	required_basis = {"signed": "real", "phase": "complex"}.get(mode)

	if required_basis is None:
		return bases.copy()

	if required_basis not in bases:
		label = "complexa" if required_basis == "complex" else "real"
		raise ValueError(f"{mode} exige base {label}.")

	return [required_basis]

def iter_orbitals(selection: dict) -> Iterator[tuple[int, int, int]]:
	"""
	Enumera os números quânticos de uma seleção.

	A seleção deve ter sido validada previamente.
	"""
	selection_type = selection["type"]

	if selection_type == "single":
		yield (selection["n"], selection["l"], selection["m"])

	elif selection_type == "range":
		for n in range(
			selection["n_min"],
			selection["n_max"] + 1
		):
			for l in range(n):
				for m in range(-l, l + 1):
					yield n, l, m

	else:
		raise ValueError(f"Tipo de seleção desconhecido: {selection_type}")

def orbital_stem(n: int, l: int, m: int, basis: str, mode: str | None = None) -> str:
	"""Monta o nome de um orbital, sem extensão."""
	name = f"orbital_n{n}_l{l}_m{m}_{basis}"

	if mode is not None:
		name += f"_{mode}"

	return name