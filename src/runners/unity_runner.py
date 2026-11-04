import argparse
import os
import subprocess
import time
from pathlib import Path

import src.core.orbital_selection as sel
import src.io.json_io as json_io
import src.io.paths as paths
import src.services.run_service as runs

def expected_orbitals(job: dict) -> dict[str, list[str]]:
	bases = job["basis"]
	modes = list(job["representations"])

	supported = {"single", "signed", "multilayer", "point_cloud", "phase"}

	if not bases:
		raise ValueError("Nenhuma base solicitada")

	if not modes or set(modes) - supported:
		raise ValueError(f"Representações inválidas: {modes}")

	if "signed" in modes and "real" not in bases:
		raise ValueError("signed exige base real.")

	if "phase" in modes and "complex" not in bases:
		raise ValueError("phase exige base complexa.")

	tasks = list(sel.iter_orbitals(job["selection"]))
	if not tasks:
		raise RuntimeError("Nenhum orbital solicitado")

	orbitals_by_mode = {}
	for mode in modes:
		orbital_names = [sel.orbital_stem(n, l, m, basis, mode=mode)
		                for basis in bases if (
							(mode != "signed" or basis == "real") and
							(mode != "phase" or basis == "complex"))
		                for n, l, m in tasks]
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

	# 0 = sem timeout; qualquer valor positivo = limite em segundos.
	try:
		timeout_seconds = int(os.environ.get("UNITY_TIMEOUT_SECONDS", "0"))
	except ValueError as exc:
		raise ValueError("UNITY_TIMEOUT_SECONDS deve ser um inteiro.") from exc

	if timeout_seconds < 0:
		raise ValueError("UNITY_TIMEOUT_SECONDS não pode ser negativo.")

	start_time = time.perf_counter()

	try:
		result = subprocess.run(command, timeout=timeout_seconds or None, check=False)
	finally:
		elapsed = time.perf_counter() - start_time

		print(f"Tempo de execução do Unity: {elapsed / 60:.1f} minutos.", flush=True)

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

	return sorted(gif_files)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--run", type=Path, required=True)
	parser.add_argument("--resume", action="store_true", help="Retoma a etapa Unity de uma Run con falha.")

	args = parser.parse_args()
	run_dir = args.run.resolve()

	if args.resume:
		runs.retry_failed_stage(run_dir, "unity")

	runs.start_stage(run_dir, "unity")
	try:
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