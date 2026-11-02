import argparse
import json
import sys

import src.io.paths as paths
import src.io.json_io as json_io
import src.config.job_resolver as resolver
import src.services.run_service as runs

def prepare_run(preset_name: str):
	if not preset_name or not all(char.isalnum() or char in "_-" for char in preset_name):
		raise ValueError("Nome de preset inválido.")

	defaults = json_io.load_json(paths.DEFAULTS_PATH)

	preset_path = paths.JOBS_DIR / f"{preset_name}.json"
	job = json_io.load_json(preset_path)

	resolved = resolver.resolve_job(defaults, job)

	return runs.create_run(resolved)

def main():
	parser = argparse.ArgumentParser(description="Prepara uma Run a partir de um preset.")

	parser.add_argument("preset", help="Nome do preset, sem a extensão .json.")

	args = parser.parse_args()

	try:
		run_dir = prepare_run(args.preset)

		print(json.dumps({"ok": True, "run_id": run_dir.name, "run_dir": str(run_dir.resolve())}))

	except Exception as exc:
		print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)

		sys.exit(1)

if __name__ == "__main__":
	main()