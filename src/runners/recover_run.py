import argparse
import json
import sys
from pathlib import Path

import src.services.run_service as runs

def main():
	parser = argparse.ArgumentParser(description="Recupera o estado de uma Run interrompida.")
	parser.add_argument("--run", type=Path,	required=True)
	parser.add_argument("--confirm-stopped", action="store_true", help="Confirma que os processos anteriores já terminaram.")

	args = parser.parse_args()

	if not args.confirm_stopped:
		parser.error("Confirme que a execução anterior terminou usando --confirm-stopped.")

	try:
		run_dir = args.run.resolve()

		stage = runs.recover_interrupted_run(run_dir)

		print(json.dumps({"ok": True, "run_id": run_dir.name, "run_dir": str(run_dir), "failed_stage": stage}))

	except Exception as exc:
		print(
			json.dumps({
				"ok": False,
				"error": str(exc)
			}),
			file=sys.stderr
		)
		sys.exit(1)

if __name__ == "__main__":
	main()