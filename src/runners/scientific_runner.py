import argparse
from pathlib import Path

import src.core.orbital as orb
import src.core.space as sp
import src.io.export as xp
import src.io.json_io as json_io
import src.services.orbital_service as orbital_service
import src.services.run_service as run_service

def execute_scientific(run_dir: Path) -> None:
	job = json_io.load_json(run_dir / "job.json")

	selection = job["selection"]
	bases = job["basis"]
	representations = job["representations"]

	# Por enquanto, uma base e o modo single.
	if len(bases) != 1 or list(representations) != ["single"]:
		raise ValueError("O runner ainda aceita apenas uma base e a representação single.")

	basis = orb.OrbitalBasis(bases[0])
	params = representations["single"]
	num_div = job["space"]["num_div"]

	# Transforma a seleção em uma sequência de orbitais.
	if selection["type"] == "single":
		tasks = [(selection["n"], selection["l"], selection["m"])]

	elif selection["type"] == "range":
		tasks = orbital_service.orbital_tasks(n_max=selection["n_max"],	n_min=selection["n_min"])

	else:
		raise ValueError("Tipo de seleção desconhecido.")

	output_dir = run_dir / "scientific" / "single"
	output_dir.mkdir(parents=True, exist_ok=True)

	count = 0

	for n, l, m in tasks:
		print(f"Gerando orbital n={n}, l={l}, m={m}", flush=True)

		space = sp.Space()

		orbital = orbital_service.create_orbital(space,	n=n, l=l, m=m, basis=basis,	num_div=num_div)

		xp.save_obj(orbital, percent=params["percent"],	output_dir=output_dir)

		output_file = output_dir / f"{orbital.name}.obj"

		if (not output_file.is_file() or output_file.stat().st_size == 0):
			raise RuntimeError(f"OBJ inválido: {output_file}")

		count += 1
		print(f"Orbital {orbital.name} concluído.", flush=True)

		# Libera as referências ao orbital e à grade.
		del orbital, space

	if count == 0:
		raise RuntimeError("Nenhum orbital foi gerado.")

	print(f"Total gerado: {count} orbitais.", flush=True)

def main() -> None:
	parser = argparse.ArgumentParser(description="Executa a etapa científica de uma Run.")

	parser.add_argument("--run", type=Path,	required=True, help="Diretório da Run.")

	args = parser.parse_args()
	run_dir = args.run.resolve()

	try:
		run_service.start_stage(run_dir, "scientific")
		execute_scientific(run_dir)
		run_service.complete_stage(run_dir, "scientific")

		print("Etapa científica concluída.")

	except Exception as exc:
		try:
			run_service.fail_run(run_dir, str(exc))
		except Exception:
			pass

		raise

if __name__ == "__main__":
	main()