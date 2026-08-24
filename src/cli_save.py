import numpy as np

SAVE_MENU = {
	1: "point_cloud",
	2: "single_obj",
	3: "batch_obj",
}

def ask_save_mode():
	print("\nEscolha o modo de salvamento:")
	for key, mode in SAVE_MENU.items():
		print(f"{key}: {mode}")
	option = int(input("\nDigite o número do modo: "))
	return SAVE_MENU[option]

def ask_point_cloud_args(scalar_field):
	percent = float(input("Porcentagem do máximo para a nuvem (0-100): "))
	level = percent / 100 * np.max(scalar_field)

	decimals = int(input("Casas decimais de tolerância: "))
	tol = 10 ** (-decimals) * np.max(scalar_field)

	return {"mask": np.abs(scalar_field - level) <= tol}

def ask_single_obj_args(scalar_field):
	percent = float(input("Porcentagem do máximo para a isossuperfície (0-100): "))
	level = percent / 100 * np.max(scalar_field)

	return {"scalar_field": scalar_field, "level": level}

def ask_batch_obj_args(scalar_field):
	layers = int(input("Número de camadas: "))
	start_percent = float(input("Porcentagem inicial: ")) / 100

	return {"scalar_field": scalar_field, "layers": layers, "start_percent": start_percent}

ASK_SAVE_ARGS = {
	"point_cloud": ask_point_cloud_args,
	"single_obj": ask_single_obj_args,
	"batch_obj": ask_batch_obj_args,
}

def ask_save_kwargs(mode: str, scalar_field):
	return ASK_SAVE_ARGS[mode](scalar_field)