import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

import bpy

import src.blender as bl
import src.io.json_io as json_io
import src.services.run_service as runs


def execute_blender(run_dir: Path, save_blend: bool = False) -> Path:
	job = json_io.load_json(run_dir / "job.json")

	selection = job["selection"]
	bases = job["basis"]
	representations = job["representations"]

	if selection["type"] != "single":
		raise ValueError("Blender runner ainda não aceita range.")

	if len(bases) != 1 or list(representations) != ["single"]:
		raise ValueError(
			"Blender runner ainda aceita apenas uma base e o modo single."
		)

	n = selection["n"]
	l = selection["l"]
	m = selection["m"]
	basis = bases[0]

	orbital_name = f"orbital_n{n}_l{l}_m{m}_{basis}"

	input_dir = run_dir / "scientific" / "single"
	output_dir = run_dir / "blender"

	source_file = input_dir / f"{orbital_name}.obj"

	if not source_file.is_file():
		raise FileNotFoundError(f"OBJ não encontrado: {source_file}")

	# Começa com uma cena limpa, sem o cubo padrão.
	bpy.ops.object.select_all(action="SELECT")
	bpy.ops.object.delete(use_global=False)

	obj = bl.loader.load_single_orbital(orbital_name, mode="single", input_dir=input_dir)

	global_scale = job["blender"]["fbx"]["global_scale"]

	fbx_path = bl.exporter.export_fbx(obj, orbital_name, mode="single",	output_dir=output_dir / "single", global_scale=global_scale)

	if save_blend:
		blend_path = output_dir / f"{orbital_name}.blend"

		bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

		if not blend_path.is_file():
			raise RuntimeError(f"Arquivo .blend não encontrado: {blend_path}")

		print(f"Cena salva: {blend_path}")

	return fbx_path

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

		fbx_path = execute_blender(run_dir, args.save_blend)

		runs.complete_stage(run_dir, "blender")

		print(f"Etapa Blender concluída: {fbx_path}")

	except Exception as exc:
		try:
			runs.fail_run(run_dir, str(exc))
		except Exception:
			pass

		raise

if __name__ == "__main__":
	main()