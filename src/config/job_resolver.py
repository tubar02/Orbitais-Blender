from copy import deepcopy

import src.config.job_validator as val

def deep_merge(base: dict, override: dict) -> dict:
	result = deepcopy(base)

	for key, value in override.items():
		if (key in result and isinstance(result[key], dict) and isinstance(value, dict)):
			result[key] = deep_merge(result[key], value)
		else:
			result[key] = deepcopy(value)

	return result

def resolve_job(defaults: dict, job: dict) -> dict:
	val.validate_job(job, defaults)

	config = deep_merge(defaults, job.get("overrides", {}))

	basis = job.get("basis", config["scientific"]["basis"])

	representations = job["representations"]

	scientific = config["scientific"]
	global_percent = scientific["percent"]
	representation_params = scientific["representation_params"]

	resolved_representations = {}

	for mode in representations:
		params = deepcopy(representation_params[mode])
		params.setdefault("percent", global_percent)

		resolved_representations[mode] = params

	resolved = {
		"name": job["name"],
		"selection": deepcopy(job["selection"]),
		"basis": deepcopy(basis),
		"representations": resolved_representations,
		"blender": deepcopy(config["blender"]),
		"unity": deepcopy(config["unity"])
	}
	val.validate_resolved_job(resolved)
	return resolved