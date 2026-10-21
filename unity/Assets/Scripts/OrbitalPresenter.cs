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
	public GameObject orbitalPrefab;
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

		if (entry != null)
		{
			if (currentOrbital != null)
			{
				Destroy(currentOrbital);
			}

			currentOrbital = Instantiate(entry.orbitalPrefab, transform);
			currentOrbital.transform.localScale = Vector3.one * targetSize;

			Rotation rotationScript = currentOrbital.GetComponent<Rotation>();
			if (rotationScript != null)
			{
				rotationScript.rotationSpeed = rotationSpeed;
			}
		}
		else
		{
			Debug.LogWarning($"Orbital not found: n={n}, l={l}, m={m}, basis={basis}, mode={mode}");
		}
	}
}