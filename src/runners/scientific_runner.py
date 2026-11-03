import argparse
from pathlib import Path

import src.core.orbital as orb
import src.core.space as sp
import src.core.orbital_selection as sel
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
	if len(bases) != 1:
		raise ValueError("O runner ainda aceita apenas uma base.")

	supported_modes = {"single", "signed"}
	if not representations or set(representations) - supported_modes:
		raise ValueError(f"Representações inválidas: {representations}. Suportadas: {supported_modes}")

	basis = orb.OrbitalBasis(bases[0])
	if ("signed" in representations and basis != orb.OrbitalBasis.REAL):
		raise ValueError("signed exige base real.")
	
	num_div = job["space"]["num_div"]
	count = 0

	for n, l, m in sel.iter_orbitals(selection):
		print(f"Gerando orbital n={n}, l={l}, m={m}", flush=True)

		space = sp.Space()

		orbital = orbital_service.create_orbital(space,	n=n, l=l, m=m, basis=basis,	num_div=num_div)

		for mode, params in representations.items():
			output_dir = run_dir / "scientific" / mode

			if mode == "single":
				xp.save_obj(orbital, percent=params["percent"], output_dir=output_dir)
				files = [output_dir / f"{orbital.name}.obj"]
			elif mode == "signed":
				xp.save_signed_obj(orbital, percent=params["percent"], output_dir=output_dir)
				parts_dir = output_dir / orbital.name
				files = sorted(parts_dir.glob("*.obj"))

				if (not files or any(file.stem not in {"pos", "neg"} for file in files)):
					raise RuntimeError(f"Superfícies signed inválidas: {parts_dir}")

			for file in files:
				if (not file.is_file() or file.stat().st_size == 0):
					raise RuntimeError(f"OBJ inválido: {file}")
				
			print(f"{orbital.name} modo {mode} concluído.", flush=True)

		count += 1
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