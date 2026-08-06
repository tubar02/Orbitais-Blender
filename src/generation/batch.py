import numpy as np

import src.grid.space as sp
import src.physics as phy

import single as sg

def orbital_tasks(n_max: int):
	for n in range(1, n_max + 1):
		for l in range(0, n):
			for m in range(-l, l + 1):
				yield n, l, m

def generate_orbitals(space: sp.Space, n_max: int):
	current_n = None
	for n, l, m in orbital_tasks(n_max):
		if n != current_n:
			space.static_space_update(n)
			current_n = n

		yield sg.generate_orbital(space, n, l, m)