import numpy as np

def thresholding(func: np.ndarray, threshold: int = 0, tol: float = 1e-1) -> np.ndarray:
	mask = np.abs(func - threshold) < tol
	return mask