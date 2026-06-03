import numpy as np
from tqdm import tqdm, trange
from time import sleep

import src.grid.space as sp
import src.io.export as xp
import src.physics.atomic_orbitals as orb
import src.physics.density as den
import src.utils.plot as plt

def generate_orbital():
	pass

def main():
	def usa_tqdm(leave = True):
		a = 0
		for tupla in tqdm(list(enumerate(range(1, 6))), desc="Inner loop 1", colour="cyan", leave=leave):
			sleep(0.5)
			a += tupla[0] + tupla[1]
		for i in trange(5, desc="Inner loop 2", colour="cyan", leave=leave):
			sleep(0.5)
		return a

	print("Fora do loop")
	print(usa_tqdm())

	print("Em loop")
	for i in trange(5, desc="Outter loop", colour="blue"):
		sleep(0.1)
		print(usa_tqdm(leave=False))

if __name__ == "__main__":
	main()