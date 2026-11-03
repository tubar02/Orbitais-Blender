from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import src.io.paths as paths
import src.io.json_io as json_io


def create_run(resolved_job: dict) -> Path:
	now = datetime.now(timezone.utc)

	run_id = (
		f"run_{now.strftime('%Y%m%d_%H%M%S')}_"
		f"{uuid4().hex[:8]}"
	)

	run_dir = paths.RUNS_DIR / run_id
	run_dir.mkdir(parents=True, exist_ok=False)

	run_data = {
		"run_id": run_id,
		"status": "pending",
		"current_stage": None,
		"created_at": now.isoformat(),
		"started_at": None,
		"finished_at": None,
		"stages": {
			"scientific": "pending",
			"blender": "pending",
			"unity": "pending"
		},
		"error": None
	}

	json_io.save_json(run_dir / "job.json", resolved_job)
	json_io.save_json(run_dir / "run.json", run_data)

	for directory in ("scientific", "blender", "unity"):
		(run_dir / directory).mkdir()

	return run_dir

STAGE_ORDER = ("scientific", "blender", "unity")
FINAL_STATES = {"completed", "failed", "cancelled"}

def _now() -> str:
	return datetime.now(timezone.utc).isoformat()

def _load_run(run_dir: Path) -> dict:
	return json_io.load_json(Path(run_dir) / "run.json")

def _save_run(run_dir: Path, data: dict) -> None:
	json_io.save_json(Path(run_dir) / "run.json", data)

def start_stage(run_dir: Path, stage: str) -> None:
	data = _load_run(run_dir)

	if stage not in STAGE_ORDER:
		raise ValueError(f"Etapa desconhecida: {stage}")

	if data["status"] in FINAL_STATES:
		raise ValueError("A Run já foi encerrada.")

	if data["current_stage"] is not None:
		raise ValueError("Já existe uma etapa em execução.")

	index = STAGE_ORDER.index(stage)

	for previous in STAGE_ORDER[:index]:
		if data["stages"][previous] != "completed":
			raise ValueError(f"A etapa {previous} ainda não foi concluída.")

	if data["stages"][stage] != "pending":
		raise ValueError(f"A etapa {stage} não está pendente.")

	if data["started_at"] is None:
		data["started_at"] = _now()

	data["status"] = "running"
	data["current_stage"] = stage
	data["stages"][stage] = "running"

	_save_run(run_dir, data)

def complete_stage(run_dir: Path, stage: str) -> None:
	data = _load_run(run_dir)

	if (data["status"] != "running" or data["current_stage"] != stage or data["stages"].get(stage) != "running"):
		raise ValueError(f"A etapa {stage} não está em execução.")

	data["stages"][stage] = "completed"
	data["current_stage"] = None

	if all(status == "completed" for status in data["stages"].values()):
		data["status"] = "completed"
		data["finished_at"] = _now()

	_save_run(run_dir, data)

def fail_run(run_dir: Path, message: str) -> None:
	data = _load_run(run_dir)

	if data["status"] in FINAL_STATES:
		raise ValueError("A Run já foi encerrada.")

	stage = data["current_stage"]

	if stage is not None:
		data["stages"][stage] = "failed"

	data["status"] = "failed"
	data["current_stage"] = None
	data["finished_at"] = _now()
	data["error"] = str(message)

	_save_run(run_dir, data)

def cancel_run(run_dir: Path) -> None:
	data = _load_run(run_dir)

	if data["status"] in FINAL_STATES:
		raise ValueError("A Run já foi encerrada.")

	stage = data["current_stage"]

	if stage is not None:
		data["stages"][stage] = "cancelled"

	data["status"] = "cancelled"
	data["current_stage"] = None
	data["finished_at"] = _now()

	_save_run(run_dir, data)

def retry_failed_unity(run_dir: Path) -> None:
	data = _load_run(run_dir)

	if (data["status"] != "failed" or data["stages"]["unity"] != "failed" or data["current_stage"] is not None):
		raise ValueError("Somente Runs que falharam na etapa Unity podem ser retomadas por este comando.")

	if any(data["stages"][stage] != "completed"	for stage in ("scientific", "blender")):
		raise ValueError("Scientific e Blender precisam estar concluídos.")

	data["status"] = "pending"
	data["stages"]["unity"] = "pending"
	data["finished_at"] = None
	data["error"] = None

	_save_run(run_dir, data)