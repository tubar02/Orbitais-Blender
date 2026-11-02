from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import src.io.paths as paths
from src.io.json_io import save_json


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

	save_json(run_dir / "job.json", resolved_job)
	save_json(run_dir / "run.json", run_data)

	for directory in ("scientific", "blender", "unity"):
		(run_dir / directory).mkdir()

	return run_dir