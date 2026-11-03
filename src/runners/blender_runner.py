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

def execute_blender(run_dir: Path, save_blend: bool = False) -> list[Path]:
	job = json_io.load_json(run_dir / "job.json")

	selection = job["selection"]
	bases = job["basis"]
	representations = job["representations"]

	if len(bases) != 1 or list(representations) != ["single"]:
		raise ValueError("Blender runner ainda suporta somente uma base e a representação single.")

	basis = bases[0]
	input_dir = run_dir / "scientific" / "single"
	output_dir = run_dir / "blender"
	global_scale = job["blender"]["fbx"]["global_scale"]

	# Nomes esperados a partir do Job.
	orbital_names = [sel.orbital_stem(n, l, m, basis) for n, l, m in sel.iter_orbitals(selection)]

	if not orbital_names:
		raise RuntimeError("Nenhum orbital solicitado.")

	expected_files = {input_dir / f"{name}.obj"	for name in orbital_names}

	actual_files = set(input_dir.glob("*.obj"))

	if expected_files != actual_files:
		missing = expected_files - actual_files
		unexpected = actual_files - expected_files

		raise RuntimeError(
			f"Arquivos OBJ inconsistentes. "
			f"Ausentes: {[p.name for p in missing]}. "
			f"Inesperados: {[p.name for p in unexpected]}."
		)

	# Limpa a cena apenas uma vez.
	bpy.ops.object.select_all(action="SELECT")
	bpy.ops.object.delete(use_global=False)
	orbitals = bl.loader.load_all_orbitals(basis, mode="single", input_dir=input_dir)

	fbx_files = []
	for (n, l, m, orb_basis), obj in orbitals.items():
		orbital_name = sel.orbital_stem(n, l, m, orb_basis)
		print(f"Processando {orbital_name}", flush=True)
		fbx_path = bl.exporter.export_fbx(obj, orbital_name, mode="single", output_dir=output_dir / "single", global_scale=global_scale)
		fbx_files.append(fbx_path)
		print(f"FBX concluído: {fbx_path.name}", flush=True)

	if save_blend:
		rows = bl.layout.group_orbitals(orbitals)
		bl.layout.arrange_orbital_grid(rows)
		bl.scene.organize_collections(orbitals)

		blend_path = output_dir / f"{run_dir.name}.blend"

		bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

		if (not blend_path.is_file() or blend_path.stat().st_size == 0):
			raise RuntimeError(f"Arquivo .blend inválido: {blend_path}")

		print(f"Cena completa salva: {blend_path}", flush=True)

	if len(fbx_files) != len(orbital_names):
		raise RuntimeError("Quantidade de FBXs diferente da esperada.")

	return fbx_files

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument("--run", type=Path, required=True)
	parser.add_argument("--save-blend", action="store_true")

	# Argumentos depois de -- pertencem ao nosso script,
	# não à linha de comando do Blender.
	argv = sys.argv
	argv = argv[argv.index("--") + 1:] if "--" in argv else []

	args = parser.parse_args(argv)
	run_dir = args.run.resolve()

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