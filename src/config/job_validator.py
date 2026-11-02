import math

VALID_BASES = {"real", "complex"}
VALID_MODES = {"point_cloud", "single", "multilayer", "signed"}

def _check_keys(data: dict, allowed: set, context: str) -> None:
	if not isinstance(data, dict):
		raise ValueError(f"{context} deve ser um objeto JSON.")

	unknown = set(data) - allowed
	if unknown:
		raise ValueError(f"Campos desconhecidos em {context}: {sorted(unknown)}")

def _positive_number(value, name: str) -> None:
	if (isinstance(value, bool)	or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0):
		raise ValueError(f"{name} deve ser positivo e finito.")

def _percent(value, name: str) -> None:
	_positive_number(value, name)
	if value >= 1:
		raise ValueError(f"{name} deve ser menor que 1.")

def _positive_int(value, name: str) -> None:
	if type(value) is not int or value < 1:
		raise ValueError(f"{name} deve ser um inteiro positivo.")

def _check_overrides(overrides: dict, defaults: dict) -> None:
	"""Impede campos desconhecidos e alterações na estrutura."""
	def check(data, reference, path="overrides"):
		_check_keys(data, set(reference), path)

		for key, value in data.items():
			expected = reference[key]

			if isinstance(expected, dict):
				if not isinstance(value, dict):
					raise ValueError(f"{path}.{key} deve ser um objeto.")
				check(value, expected, f"{path}.{key}")

	check(overrides, defaults)

def validate_job(job: dict, defaults: dict) -> None:
	"""Valida a estrutura do pedido antes da resolução."""
	_check_keys(job, {"name", "selection", "basis", "representations", "overrides"}, "job")

	if not isinstance(job.get("name"), str) or not job["name"].strip():
		raise ValueError("O Job precisa de um nome.")

	selection = job.get("selection")
	if not isinstance(selection, dict):
		raise ValueError("selection deve ser um objeto.")

	selection_type = selection.get("type")

	if selection_type == "single":
		_check_keys(selection, {"type", "n", "l", "m"}, "selection")
		if not all(k in selection for k in ("n", "l", "m")):
			raise ValueError("single exige n, l e m.")

		n, l, m = (selection[k] for k in ("n", "l", "m"))
		if not all(type(v) is int for v in (n, l, m)):
			raise ValueError("n, l e m devem ser inteiros.")
		if not (n > 0 and 0 <= l < n and -l <= m <= l):
			raise ValueError("Números quânticos inválidos.")

	elif selection_type == "range":
		_check_keys(selection, {"type", "n_min", "n_max"}, "selection")
		if not all(k in selection for k in ("n_min", "n_max")):
			raise ValueError("range exige n_min e n_max.")

		n_min, n_max = selection["n_min"], selection["n_max"]
		if (type(n_min) is not int or type(n_max) is not int or not 1 <= n_min <= n_max):
			raise ValueError("Intervalo de n inválido.")

	else:
		raise ValueError(f"Tipo de seleção inválido: {selection_type}")

	bases = job.get("basis", defaults["scientific"]["basis"])
	modes = job.get("representations")

	for name, values, allowed in (("basis", bases, VALID_BASES), ("representations", modes, VALID_MODES),):
		if not isinstance(values, list) or not values:
			raise ValueError(f"{name} deve ser uma lista não vazia.")
		if any(not isinstance(v, str) or v not in allowed for v in values):
			raise ValueError(f"Valores inválidos em {name}: {values}")
		if len(values) != len(set(values)):
			raise ValueError(f"Valores repetidos em {name}.")

	if "signed" in modes and "complex" in bases:
		raise ValueError("signed não é compatível com a base complexa.")

	_check_overrides(job.get("overrides", {}), defaults)

def validate_resolved_job(resolved: dict) -> None:
	"""Valida os parâmetros efetivos das etapas."""
	for mode, params in resolved["representations"].items():
		_percent(params["percent"], f"{mode}.percent")

		if mode == "point_cloud":
			_positive_number(params["tolerancia"], "point_cloud.tolerancia")

		elif mode == "multilayer":
			layers = params["layers"]
			_positive_int(layers, "multilayer.layers")

			# Os nomes atuais usam percentuais arredondados.
			percent = params["percent"]
			rounded = [round((percent + (1 - percent) * i / layers) * 100) for i in range(layers)]
			if len(set(rounded)) != layers:
				raise ValueError("multilayer produziria nomes repetidos.")

	fbx = resolved["blender"]["fbx"]
	_positive_number(fbx["global_scale"], "blender.fbx.global_scale")

	presentation = resolved["unity"]["presentation"]
	_positive_number(presentation["rotation_speed"], "rotation_speed")
	_positive_int(presentation["revolutions"], "revolutions")

	fill = presentation["screen_fill"]
	_positive_number(fill, "screen_fill")
	if fill > 0.95:
		raise ValueError("screen_fill deve ser <= 0.95.")

	recording = resolved["unity"]["recording"]
	_positive_int(recording["fps"], "fps")
	_positive_int(recording["resolution"], "resolution")

	quality = recording["quality"]
	if type(quality) is not int or not 0 <= quality <= 100:
		raise ValueError("quality deve estar entre 0 e 100.")

	if type(recording["loop"]) is not bool:
		raise ValueError("loop deve ser booleano.")