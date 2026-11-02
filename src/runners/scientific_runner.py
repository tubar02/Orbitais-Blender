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

	# Primeira versão: um orbital e uma representação.
	if selection["type"] != "single":
		raise ValueError("O runner ainda não aceita intervalos.")

	if len(bases) != 1 or len(representations) != 1:
		raise ValueError("O runner ainda aceita apenas uma base e uma representação.")

	mode, params = next(iter(representations.items()))

	if mode != "single":
		raise ValueError("O runner ainda suporta somente a representação single.")

	basis = orb.OrbitalBasis(bases[0])

	space = sp.Space()

	orbital = orbital_service.create_orbital(
		space,
		n=selection["n"],
		l=selection["l"],
		m=selection["m"],
		basis=basis
	)

	output_dir = run_dir / "scientific" / "single"

	xp.save_obj(orbital, percent=params["percent"],	output_dir=output_dir)

	output_file = output_dir / f"{orbital.name}.obj"

	if not output_file.is_file() or output_file.stat().st_size == 0:
		raise RuntimeError(f"O arquivo OBJ não foi gerado corretamente: {output_file}")

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