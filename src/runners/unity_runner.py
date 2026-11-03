import argparse
import os
import subprocess
from pathlib import Path

import src.io.json_io as json_io
import src.io.paths as paths
import src.services.run_service as runs

def expected_orbitals(job: dict) -> list[str]:
	selection = job["selection"]

	if len(job["basis"]) != 1 or list(job["representations"]) != ["single"]:
		raise ValueError("Unity runner ainda aceita uma base e o modo single.")

	basis = job["basis"][0]

	if selection["type"] == "single":
		tasks = [(selection["n"], selection["l"], selection["m"])]

	elif selection["type"] == "range":
		tasks = (
			(n, l, m)
			for n in range(selection["n_min"], selection["n_max"] + 1)
			for l in range(n)
			for m in range(-l, l + 1)
		)

	else:
		raise ValueError("Tipo de seleção desconhecido.")

	return [f"orbital_n{n}_l{l}_m{m}_{basis}_single" for n, l, m in tasks]

def execute_unity(run_dir: Path) -> list[Path]:
	job = json_io.load_json(run_dir / "job.json")
	orbital_names = expected_orbitals(job)

	if not orbital_names:
		raise RuntimeError("Nenhum orbital solicitado.")

	# Verifica todos os FBXs antes de abrir o Unity.
	input_dir = run_dir / "blender" / "single"

	expected_fbx = {input_dir / f"{name}.fbx" for name in orbital_names}
	actual_fbx = set(input_dir.glob("*.fbx"))

	if actual_fbx != expected_fbx:
		raise RuntimeError(
			"FBXs inconsistentes. "
			f"Ausentes: {sorted(p.name for p in expected_fbx - actual_fbx)}. "
			f"Inesperados: {sorted(p.name for p in actual_fbx - expected_fbx)}."
		)

	if any(p.stat().st_size == 0 for p in expected_fbx):
		raise RuntimeError("Há arquivos FBX vazios.")

	unity_exe = os.environ.get("UNITY_EXE")

	if not unity_exe:
		raise EnvironmentError("Variável UNITY_EXE não configurada.")

	unity_exe = Path(unity_exe)

	if not unity_exe.is_file():
		raise FileNotFoundError(unity_exe)

	project_dir = paths.ROOT / "unity"

	if not (project_dir / "Assets").is_dir():
		raise FileNotFoundError(project_dir)

	command = [
		str(unity_exe),
		"-projectPath", str(project_dir),
		"-executeMethod",
		"OrbitalRecordingRunner.StartRunFromCommandLine",
		"-orbitalsRun", str(run_dir),
	]

	print(f"Iniciando Unity para {len(orbital_names)} orbitais...",	flush=True)

	result = subprocess.run(command, timeout=900, check=False)

	if result.returncode != 0:
		raise RuntimeError(f"Unity encerrou com código {result.returncode}")

	# Verifica todos os GIFs produzidos.
	output_dir = run_dir / "unity" / "single"

	expected_gif = {output_dir / f"{name}.gif" for name in orbital_names}
	actual_gif = set(output_dir.glob("*.gif"))

	if actual_gif != expected_gif:
		raise RuntimeError(
			"GIFs inconsistentes. "
			f"Ausentes: {sorted(p.name for p in expected_gif - actual_gif)}. "
			f"Inesperados: {sorted(p.name for p in actual_gif - expected_gif)}."
		)

	for gif in expected_gif:
		if gif.stat().st_size <= 6:
			raise RuntimeError(f"GIF vazio: {gif}")

		with gif.open("rb") as file:
			signature = file.read(6)

		if signature not in (b"GIF87a", b"GIF89a"):
			raise RuntimeError(f"Assinatura GIF inválida: {gif}")

	return sorted(expected_gif)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--run", type=Path, required=True)
	args = parser.parse_args()

	run_dir = args.run.resolve()

	try:
		runs.start_stage(run_dir, "unity")
		gifs = execute_unity(run_dir)
		runs.complete_stage(run_dir, "unity")

		print(f"Etapa Unity concluída: {len(gifs)} GIFs produzidos", flush=True)

	except Exception as exc:
		try:
			runs.fail_run(run_dir, str(exc))
		except Exception:
			pass

		raise

if __name__ == "__main__":
	main()