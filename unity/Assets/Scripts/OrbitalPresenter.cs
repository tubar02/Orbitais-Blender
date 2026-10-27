
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
	[SerializeField] private int selectedN = 3;
	[SerializeField] private int selectedL = 2;
	[SerializeField] private int selectedM = 0;
	[SerializeField] private string selectedBasis = "real";
	[SerializeField] private string selectedMode = "signed";

	[Header("Apresentação")]
	[SerializeField] private float scaleMultiplier = 1f;
	[SerializeField] private float rotationSpeed = 90f;

	private GameObject currentOrbital;

	private void Start()
	{
#if UNITY_EDITOR
		UpdateCatalog();
#endif 
		LoadOrbital(selectedN, selectedL, selectedM, selectedBasis, selectedMode);
	}

	[ContextMenu("Carregar orbital selecionado")]
	public void LoadSelectedOrbital()
	{
		if (!Application.isPlaying)
		{
			Debug.LogWarning("Entre no Play Mode para carregar um orbital.");
			return;
		}
		LoadOrbital(selectedN, selectedL, selectedM, selectedBasis, selectedMode);
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

		GameObject nextOrbital = Instantiate(entry.prefab, transform);
		nextOrbital.transform.localPosition = Vector3.zero;
		nextOrbital.transform.localScale = entry.prefab.transform.localScale * scaleMultiplier;

		Rotation rotation = nextOrbital.GetComponent<Rotation>();
		if (rotation == null)
		{
			rotation = nextOrbital.AddComponent<Rotation>();
		}
		rotation.rotationSpeed = rotationSpeed;

		if (currentOrbital != null)
		{
			currentOrbital.SetActive(false);
			Destroy(currentOrbital);
		}	
		currentOrbital = nextOrbital;

		Debug.Log($"Orbital carregado: {entry.prefab.name}");
	}

#if UNITY_EDITOR
	[ContextMenu("Atualizar catálogo")]
	private void UpdateCatalog()
	{
		const string folder = "Assets/Orbitals";

		Regex pattern = new Regex(@"^orbital_n(\d+)_l(\d+)_m(-?\d+)_" +
			@"(real|complex)_(single|batch|signed)$", RegexOptions.IgnoreCase);

		string[] guids = AssetDatabase.FindAssets("", new[] { folder });
		List<OrbitalEntry> entries = new();
		foreach (string guid in guids)
		{
			string path = AssetDatabase.GUIDToAssetPath(guid);
			string name = Path.GetFileNameWithoutExtension(path);
			Match match = pattern.Match(name);
			if (!match.Success)
			{
				Debug.LogWarning($"Nome de orbital não padronizado: {name}");
				continue;
			}

			GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
			OrbitalEntry entry = new OrbitalEntry
			{
				n = int.Parse(match.Groups[1].Value),
				l = int.Parse(match.Groups[2].Value),
				m = int.Parse(match.Groups[3].Value),
				basis = match.Groups[4].Value.ToLowerInvariant(),
				mode = match.Groups[5].Value.ToLowerInvariant(),
				prefab = model
			};
			entries.Add(entry);
		}

		// Mantém uma ordem previsível.
		entries.Sort((a, b) =>
		{
			int result = a.n.CompareTo(b.n);
			if (result != 0) return result;

			result = a.l.CompareTo(b.l);
			if (result != 0) return result;

			result = a.m.CompareTo(b.m);
			if (result != 0) return result;

			result = string.CompareOrdinal(
				a.basis, b.basis
			);
			if (result != 0) return result;

			return string.CompareOrdinal(
				a.mode, b.mode
			);
		});
		orbitalEntries = entries;

		if (!Application.isPlaying)
		{
			EditorUtility.SetDirty(this);
			if (gameObject.scene.IsValid())
			{
				EditorSceneManager.MarkSceneDirty(gameObject.scene);
			}
		}
		Debug.Log($"Catálogo atualizado: {entries.Count} orbitais.");
	}
#endif
}