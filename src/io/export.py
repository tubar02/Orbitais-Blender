from pathlib import Path
import numpy as np
from tqdm import tqdm

import src.core.orbital as orb
import src.io.paths as io

def fake_exporter(orbital: orb.Orbital):
	print(f"\nExportando {orbital.name}")

def _validate_percent(percent: float) -> None:
	if not np.isfinite(percent) or not (0 < percent < 1):
		raise ValueError("O valor de percent deve estar entre 0 e 1.")

def _validate_point_cloud(percent: float, tolerancia: float) -> None:
	_validate_percent(percent)
	if not np.isfinite(tolerancia) or tolerancia <= 0:
		raise ValueError("O valor de tolerancia deve ser um número positivo finito.")

def _validate_multilayer(layers: int, start_percent:float) -> np.ndarray:
	if not isinstance(layers, int) or layers < 1:
		raise ValueError("O número de camadas deve ser um inteiro positivo.")
	_validate_percent(start_percent)

	percents = np.round(np.linspace(start_percent, 1.0, layers, endpoint=False) * 100).astype(int)
	if len(np.unique(percents)) != layers:
		raise ValueError("A quantidade de camadas produz nomes repetidos.")

	return percents

def save_point_cloud(orbital: orb.Orbital, percent: float, tolerancia: float, output_dir: Path | None = None):
	scalar_field = orbital.density
	space = orbital.space
	nome_arq = orbital.name

	_validate_point_cloud(percent, tolerancia)
	level = percent * np.max(scalar_field)
	tol = tolerancia * np.max(scalar_field)
	mask = np.abs(scalar_field - level) < tol
	if not np.any(mask):
		raise ValueError(f"Nenhum ponto encontrado dentro da tolerância especificada: {tol}")

	points = np.column_stack((space.X[mask], space.Y[mask], space.Z[mask]))
	target_dir = output_dir if output_dir is not None else io.POINT_CLOUD_DIR
	file_path = io.get_path(f"{nome_arq}.npy", target_dir)
	np.savetxt(file_path, points, delimiter=",")
	return file_path

def write_obj(file_path: Path, vertices: np.ndarray, faces: np.ndarray, leave: bool = True):
	with open(file_path, 'w') as f:
		for vert in tqdm(vertices, desc=f"Salvando vértices em {file_path.name}", colour="green", leave=leave):  # Barra de progresso
			f.write(f"v {vert[0]} {vert[1]} {vert[2]}\n")
		for face in tqdm(faces, desc=f"Salvando faces em {file_path.name}", colour="green", leave=leave):
			f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def save_obj(orbital: orb.Orbital, percent: float, leave: bool = False, output_dir: Path | None = None):
	_validate_percent(percent)

	scalar_field = orbital.density
	space = orbital.space
	nome_arq = orbital.name

	level = percent * np.max(scalar_field)
	verts, faces = space.apply_marching_cubes(scalar_field, level)

	target_dir = output_dir if output_dir is not None else io.SINGLE_OBJ_DIR
	file_path = io.get_path(f"{nome_arq}.obj", target_dir)
	write_obj(file_path, verts, faces, leave=leave)

def save_multilayer_obj(orbital: orb.Orbital, layers: int = 10, start_percent: float = 0.01, leave: bool = False, output_dir: Path | None = None):
	scalar_field = orbital.density
	space = orbital.space
	nome_dir = orbital.name

	percents = _validate_multilayer(layers, start_percent)
	levels = np.linspace(start_percent * np.max(scalar_field), np.max(scalar_field), layers, endpoint=False)

	target_dir = output_dir if output_dir is not None else io.MULTILAYER_OBJ_DIR
	dir_path = io.get_path(f"{nome_dir}", target_dir)
	io.ensure_dir(dir_path)

	for level, percent in tqdm(list(zip(levels, percents)), desc=f"Salvando camadas em {nome_dir}", colour="cyan", leave=leave):
		verts, faces = space.apply_marching_cubes(scalar_field, level)
		file_path = dir_path / f"lvl{percent}.obj"
		write_obj(file_path, verts, faces, leave=False)

def save_signed_obj(orbital: orb.Orbital, percent: float, leave: bool = False, output_dir: Path | None = None):
	_validate_percent(percent)

	if orbital.basis != orb.OrbitalBasis.REAL:
		raise ValueError("O modo 'signed_obj' só é aplicável a orbitais com base REAL.")

	wavefunction, density, space = orbital.wavefunction, orbital.density, orbital.space

	density_level = percent * np.max(density)
	amplitude = np.sqrt(density_level)

	target_dir = output_dir if output_dir is not None else io.SIGNED_OBJ_DIR
	dir_path = io.get_path(f"{orbital.name}", target_dir)
	io.ensure_dir(dir_path)
	for sign, level in [("pos", amplitude), ("neg", -amplitude)]:
		if not (wavefunction.min() <= level <= wavefunction.max()):
			continue  # Pula se o nível não estiver dentro do intervalo da função de onda
		direction = "ascent" if sign == "pos" else "descent"
		verts, faces = space.apply_marching_cubes(wavefunction, level, direction)
		file_path = dir_path / f"{sign}.obj"
		write_obj(file_path, verts, faces, leave=leave)

SAVE_MODES = {
	"point_cloud": lambda *args, **ctx: save_point_cloud(
		*args,
		percent=ctx.get("percent", 0.01),
		tolerancia=ctx.get("tolerancia", 1e-4)
	),
	"single_obj": lambda *args, **ctx: save_obj(
		*args,
		percent=ctx.get("percent", 0.01)
	),
	"multilayer_obj": lambda *args, **ctx: save_multilayer_obj(
		*args,
		layers=ctx.get("layers", 10),
		start_percent=ctx.get("start_percent", 0.01)
	),
	"signed_obj": lambda *args, **ctx: save_signed_obj(
		*args,
		percent=ctx.get("percent", 0.01)
	),
}

def save_options(mode: str, *args, **kwargs):
	try:
		SAVE_MODES[mode](*args, **kwargs)
	except KeyError:
		raise ValueError(f"Modo {mode} inexistente.")

def main():
	percents = np.round(np.linspace(0.01, 1.0, 10, endpoint=False) * 100).astype(int)

	print(percents)
	
if __name__ == "__main__":
	main()