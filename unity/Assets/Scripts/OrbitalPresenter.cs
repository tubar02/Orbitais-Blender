using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class OrbitalEntry
{
    public int n;
	public int l;
	public int m;
	public string basis;
	public string mode;
	public GameObject prefab;
}

public class OrbitalPresenter : MonoBehaviour
{
	[Header("Catálogo de orbitais")]
	[SerializeField] private List<OrbitalEntry> orbitalEntries = new();

	[Header("Orbital inicial")]
	[SerializeField] private int initialN = 3;
	[SerializeField] private int initialL = 2;
	[SerializeField] private int initialM = 1;
	[SerializeField] private string initialBasis = "real";
	[SerializeField] private string initialMode = "batch";

	[Header("Apresentação")]
	[SerializeField] private float targetSize = 2f;
	[SerializeField] private float rotationSpeed = 90f;

	private GameObject currentOrbital;

	public void LoadOrbital(int n, int l, int m, string basis, string mode)
	{
		OrbitalEntry entry = orbitalEntries.Find(
			e => e.n == n && e.l == l && e.m == m && 
			string.Equals(e.basis, basis, StringComparison.OrdinalIgnoreCase) && 
			string.Equals(e.mode, mode, StringComparison.OrdinalIgnoreCase)
		);

		if (entry == null || entry.prefab == null)
		{
			Debug.LogError($"Orbital não cadastrado: n={n}, l={l}, m={m}, basis={basis}, mode={mode}");
			return;
		}

		if (currentOrbital != null)
		{
			Destroy(currentOrbital);
		}

		
	}
}