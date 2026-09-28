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

def ask_point_cloud_args():
	percent = float(input("Porcentagem do máximo para a nuvem (0-100): ")) / 100

	decimals = int(input("Casas decimais de tolerância: "))
	tolerancia = 10 ** (-decimals)

	return {"percent": percent, "tolerancia": tolerancia}

def ask_single_obj_args():
	percent = float(input("Porcentagem do máximo para a isossuperfície (0-100): ")) / 100
	return {"percent": percent}

def ask_batch_obj_args():
	layers = int(input("Número de camadas: "))
	start_percent = float(input("Porcentagem inicial: ")) / 100

	return {"layers": layers, "start_percent": start_percent}

ASK_SAVE_ARGS = {
	"point_cloud": ask_point_cloud_args,
	"single_obj": ask_single_obj_args,
	"batch_obj": ask_batch_obj_args,
}

AUTO_SAVE_ARGS = {
	"point_cloud": {"level": None, "tol": None},
	"single_obj": {"level": None},
	"batch_obj": {"layers": None, "start_percent": None},
}

def ask_save_kwargs(mode: str):
	return ASK_SAVE_ARGS[mode]()