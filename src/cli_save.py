SAVE_MENU = {
	1: "point_cloud",
	2: "single_obj",
	3: "multilayer_obj",
	4: "signed_obj",
	5: "phase_obj",
}

def ask_save_mode(basis: str | None = None):
	available = {
		number: mode
		for number, mode in SAVE_MENU.items()
		if not (
			(mode == "phase_obj" and basis == "real")
			or
			(mode == "signed_obj" and basis == "complex")
		)
	}

	print("\nEscolha o modo de salvamento:")
	for number, mode in available.items():
		print(f"{number}: {mode}")
	option = int(input("\nDigite o número do modo: "))

	if option not in available:
		raise ValueError("Modo de salvamento inválido ou incompatível com a base.")

	return available[option]

def ask_point_cloud_args():
	percent = float(input("Porcentagem do máximo para a nuvem (0-100): ")) / 100

	decimals = int(input("Casas decimais de tolerância: "))
	tolerancia = 10 ** (-decimals)

	return {"percent": percent, "tolerancia": tolerancia}

def ask_single_obj_args():
	percent = float(input("Porcentagem do máximo para a isossuperfície (0-100): ")) / 100
	return {"percent": percent}

def ask_multilayer_obj_args():
	layers = int(input("Número de camadas: "))
	start_percent = float(input("Porcentagem inicial: ")) / 100

	return {"layers": layers, "start_percent": start_percent}

def ask_signed_obj_args():
	percent = float(input("Porcentagem do máximo para a isossuperfície (0-100): ")) / 100
	return {"percent": percent}

def ask_phase_obj_args():
	percent = float(input("Porcentagem da isosuperfície (0-100): ")) / 100
	bins = int(input("Número de faixas de fase (2-32): "))
	return {"percent": percent,	"bins": bins}

ASK_SAVE_ARGS = {
	"point_cloud": ask_point_cloud_args,
	"single_obj": ask_single_obj_args,
	"multilayer_obj": ask_multilayer_obj_args,
	"signed_obj": ask_signed_obj_args,
	"phase_obj": ask_phase_obj_args,

}

def ask_save_kwargs(mode: str):
	return ASK_SAVE_ARGS[mode]()