
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
#endif

// Representa um orbital disponível no catálogo.
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
	[SerializeField] private int initialM = 0;
	[SerializeField] private string initialBasis = "real";
	[SerializeField] private string initialMode = "signed";

	[Header("Apresentação")]
	[SerializeField] private float scaleMultiplier = 1f;
	[SerializeField] private float rotationSpeed = 90f;

	private GameObject currentOrbital;
	private int currentIndex = -1;

	private void Start()
	{
#if UNITY_EDITOR
		UpdateCatalog();
#endif 
		LoadOrbital(initialN, initialL, initialM, initialBasis, initialMode);
	}

	public void LoadOrbital(int n, int l, int m, string basis, string mode)
	{
		OrbitalEntry entry = orbitalEntries.Find(
			e => e.n == n && e.l == l && e.m == m && 
			string.Equals(e.basis, basis, StringComparison.OrdinalIgnoreCase) && 
			string.Equals(e.mode, mode, StringComparison.OrdinalIgnoreCase)
		);

		if (entry == null || entry.prefab == null)
		{
			Debug.LogError($"Orbital não encontrado: n={n}, l={l}, m={m}, basis={basis}, mode={mode}");
			return;
		}

		if (currentOrbital != null)
		{
			Destroy(currentOrbital);
		}

		GameObject nextOrbital = Instantiate(entry.prefab, transform);
		nextOrbital.transform.localPosition = Vector3.zero;
		nextOrbital.transform.localScale = entry.prefab.transform.localScale * scaleMultiplier;
		
	}

#if UNITY_EDITOR
	[ContextMenu("Atualizar catálogo")]
	private void UpdateCatalog()
	{
		return;
	}
#endif
}