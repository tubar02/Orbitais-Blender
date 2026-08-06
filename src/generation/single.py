from dataclasses import dataclass

import numpy as np

import src.grid.space as sp
import src.physics as phy

@dataclass
class Orbital:
	n: int
	m: int
	l: int
	wavefunction: np.ndarray
	density: np.ndarray

def generate_orbital(space: sp.Space, n: int, l: int, m: int, real: bool = True) -> Orbital:
	wavefunction = phy.atomic_orbitals.hydrogen_wavefunction(n, l, m, space)
	density = phy.density.probability_density(wavefunction, real=real, m=m)
	return Orbital(n=n, l=l, m=m, wavefunction=wavefunction, density=density)