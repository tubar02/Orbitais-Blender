import argparse
import os
import subprocess
from pathlib import Path

import src.core.orbital_selection as sel
import src.io.json_io as json_io
import src.io.paths as paths
import src.services.run_service as runs

def expected_orbitals(job: dict) -> dict[str, list[str]]:
	bases = job["basis"]
	modes = list(job["representations"])

	if len(bases) != 1:
		raise ValueError("Unity runner aceita só uma base")

	if not modes or set(modes) - {"single", "signed"}:
		raise ValueError(f"Representações inválidas: {modes}")

	basis = bases[0]
	if "signed" in modes and basis != "real":
		raise ValueError("signed exige base real.")

	tasks = list(sel.iter_orbitals(job["selection"]))
	if not tasks:
		raise RuntimeError("Nenhum orbital solicitado")

	orbitals_by_mode = {}
	for mode in modes:
		orbital_names = [sel.orbital_stem(n, l, m, basis, mode=mode) for n, l, m in tasks]
		orbitals_by_mode[mode] = orbital_names
	return orbitals_by_mode 

def execute_unity(run_dir: Path) -> list[Path]:
	job = json_io.load_json(run_dir / "job.json")
	orbitals_by_mode = expected_orbitals(job)

	# Verifica todos os FBXs antes de abrir o Unity.
	for mode, names in orbitals_by_mode.items():
		input_dir = run_dir / "blender" / mode
		expected_fbx = {input_dir / f"{name}.fbx" for name in names}
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

	unity_log = run_dir / "unity" / "Editor.log"
	command.extend(["-logFile", str(unity_log)])

	count = sum(len(names) for names in orbitals_by_mode.values())
	print(f"Iniciando Unity para {count} modelos...",	flush=True)

	result = subprocess.run(command, timeout=3600, check=False)

	if result.returncode != 0:
		raise RuntimeError(f"Unity encerrou com código {result.returncode}")

	# Verifica todos os GIFs produzidos.
	gif_files = []

	for mode, names in orbitals_by_mode.items():
		output_dir = run_dir / "unity" / mode
		expected_gif = {output_dir / f"{name}.gif" for name in names}
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
		gif_files.extend(expected_gif)

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