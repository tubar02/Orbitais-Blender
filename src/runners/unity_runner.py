import argparse
import os
import subprocess
from pathlib import Path

import src.io.json_io as json_io
import src.io.paths as paths
import src.services.run_service as runs

def execute_unity(run_dir: Path) -> Path:
	unity_exe = os.environ.get("UNITY_EXE")

	if not unity_exe:
		raise EnvironmentError("Variável de ambiente UNITY_EXE não configurada.")

	unity_exe = Path(unity_exe)

	if not unity_exe.is_file():
		raise FileNotFoundError(f"Executável do Unity não encontrado: {unity_exe}")

	project_dir = paths.ROOT / "unity"

	if not (project_dir / "Assets").is_dir():
		raise FileNotFoundError(f"Projeto Unity inválido: {project_dir}")

	command = [
		str(unity_exe),
		"-projectPath", str(project_dir),
		"-executeMethod",
		"OrbitalRecordingRunner.StartRunFromCommandLine",
		"-orbitalsRun", str(run_dir),
	]

	print("Iniciando Unity...", flush=True)

	result = subprocess.run(command, timeout=900, check=False)

	if result.returncode != 0:
		raise RuntimeError(f"Unity encerrou com código {result.returncode}")

	# Primeira versão: um orbital, uma base, modo single.
	job = json_io.load_json(run_dir / "job.json")

	selection = job["selection"]
	basis = job["basis"][0]

	filename = (f"orbital_n{selection['n']}_l{selection['l']}_m{selection['m']}_{basis}_single.gif")

	gif = run_dir / "unity" / "single" / filename

	if not gif.is_file() or gif.stat().st_size <= 6:
		raise RuntimeError(f"GIF ausente ou vazio: {gif}")

	with gif.open("rb") as file:
		signature = file.read(6)

	if signature not in (b"GIF87a", b"GIF89a"):
		raise RuntimeError(f"Assinatura GIF inválida: {gif}")

	return gif

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--run", type=Path, required=True)
	args = parser.parse_args()

	run_dir = args.run.resolve()

	try:
		runs.start_stage(run_dir, "unity")
		gif = execute_unity(run_dir)
		runs.complete_stage(run_dir, "unity")

		print(f"Etapa Unity concluída: {gif}", flush=True)

	except Exception as exc:
		try:
			runs.fail_run(run_dir, str(exc))
		except Exception:
			pass

		raise

if __name__ == "__main__":
	main()