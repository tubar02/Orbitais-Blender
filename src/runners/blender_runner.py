import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

import bpy

import src.core.orbital_selection as sel
import src.blender as bl
import src.io.json_io as json_io
import src.services.run_service as runs

def validate_scientific_inputs(input_dir: Path, orbital_names: list[str], mode: str, layers: int | None = None) -> None:
	if not input_dir.is_dir():
		raise FileNotFoundError(input_dir)

	if mode == "single":
		expected = {input_dir / f"{name}.obj" for name in orbital_names}
	elif mode in {"signed", "multilayer"}:
		expected = {input_dir / name for name in orbital_names}
	else:
		raise ValueError(f"Modo inválido: {mode}")

	actual = set(input_dir.iterdir())

	if actual != expected:
		raise RuntimeError(
			f"Entradas {mode} inconsistentes. "
			f"Ausentes: {sorted(p.name for p in expected - actual)}. "
			f"Inesperadas: {sorted(p.name for p in actual - expected)}."
		)

	for entry in expected:
		if mode == "single":
			if not entry.is_file() or entry.stat().st_size == 0:
				raise RuntimeError(f"OBJ inválido: {entry}")
		else:
			if not entry.is_dir():
				raise RuntimeError(f"Pasta inválida: {entry}")

			parts = list(entry.iterdir())
			names = {p.name for p in parts}

			if mode == "signed":
				valid = (bool(parts) and names <= {"pos.obj", "neg.obj"})
			else:
				valid = (
					layers is not None
					and len(parts) == layers
					and all(
						p.suffix == ".obj"
						and p.stem.startswith("lvl")
						and p.stem[3:].isdigit()
						for p in parts
					)
				)

			if not valid:
				raise RuntimeError(f"Partes {mode} inválidas: {entry}")

def execute_blender(run_dir: Path, save_blend: bool = False) -> list[Path]:
	job = json_io.load_json(run_dir / "job.json")

	bases = job["basis"]
	modes = list(job["representations"])

	if len(bases) != 1:
		raise ValueError("Blender ainda aceita apenas uma base.")

	if not modes or set(modes) - {"single", "signed", "multilayer"}:
		raise ValueError(f"Representações inválida: {modes}")

	basis = bases[0]

	if "signed" in modes and basis != "real":
		raise ValueError("signed exige base real.")

	orbital_keys = list(sel.iter_orbitals(job["selection"]))
	if not orbital_keys:
		raise RuntimeError("Nenhum orbital solicitado")
	orbital_names = [sel.orbital_stem(n, l, m, basis) for n, l, m in orbital_keys]
	global_scale = job["blender"]["fbx"]["global_scale"]
	output_dir = run_dir / "blender"

	for mode in modes:
		validate_scientific_inputs(run_dir / "scientific" / mode, orbital_names, mode, layers=job["representations"][mode].get("layers"))
			
	# Cena limpa
	bpy.ops.object.select_all(action="SELECT")
	bpy.ops.object.delete(use_global=False)

	orbitals_by_mode = {}
	fbx_files = []
	expected_keys = {(n, l, m, basis) for n, l, m in orbital_keys}

	for mode in modes:
		input_dir = run_dir / "scientific" / mode
		orbitals = bl.loader.load_all_orbitals(basis, mode=mode, input_dir=input_dir)

		if set(orbitals) != expected_keys:
			raise RuntimeError(f"Orbitais carregados inconsistentes: {mode}")

		orbitals_by_mode[mode] = orbitals
		for (n, l, m, orb_basis), obj in orbitals.items():
			orbital_name = sel.orbital_stem(n, l, m, orb_basis)
			obj.name = sel.orbital_stem(n, l, m, orb_basis, mode=mode)
			fbx_path = bl.exporter.export_fbx(obj, orbital_name, mode=mode, output_dir=output_dir / mode, global_scale=global_scale)
			fbx_files.append(fbx_path)
			print(f"FBX concluído: {fbx_path.name}", flush=True)

	if len(fbx_files) != len(orbital_names) * len(modes):
		raise RuntimeError("Quantidade incorreta de FBXs.")

	# Um blend com todos os orbitais da run
	if save_blend:
		x_offset = 0.0

		for mode, orbitals in orbitals_by_mode.items():
			rows = bl.layout.group_orbitals(orbitals)
			x_offset = bl.layout.arrange_orbital_grid(rows, x_offset=x_offset) + 20.0
			bl.scene.organize_collections(orbitals, mode=mode)
			
		blend_path = output_dir / f"{run_dir.name}.blend"
		bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
		if (not blend_path.is_file() or blend_path.stat().st_size == 0):
			raise RuntimeError(f"Arquivo .blend inválido: {blend_path}")
		print(f"Cena salva: {blend_path}", flush=True)

	return fbx_files

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--run", type=Path, required=True)
	parser.add_argument("--save-blend", action="store_true")
	parser.add_argument("--resume", action="store_true")

	# Argumentos depois de -- pertencem ao nosso script,
	# não à linha de comando do Blender.
	argv = sys.argv
	argv = argv[argv.index("--") + 1:] if "--" in argv else []
	
	args = parser.parse_args(argv)
	run_dir = args.run.resolve()

	if args.resume:
		runs.retry_failed_stage(run_dir, "blender")

	try:
		runs.start_stage(run_dir, "blender")

		fbx_files = execute_blender(run_dir, args.save_blend)

		runs.complete_stage(run_dir, "blender")

		print(
			f"Etapa Blender concluída: "
			f"{len(fbx_files)} FBXs gerados.",
			flush=True
		)

	except Exception as exc:
		try:
			runs.fail_run(run_dir, str(exc))
		except Exception:
			pass

		raise

if __name__ == "__main__":
	main()