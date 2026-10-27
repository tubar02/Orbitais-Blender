
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
	[SerializeField, Range(0.1f, 0.95f)] private float screenFill = 0.95f;
	[SerializeField] private Camera targetCamera;

	private GameObject currentOrbital;

	private void Start()
	{
#if UNITY_EDITOR
		UpdateCatalog();
#endif 
		LoadSelectedOrbital();
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

		GameObject pivot = new GameObject("OrbitalPivot");
		pivot.transform.SetParent(transform, false);

		GameObject nextOrbital = Instantiate(entry.prefab, pivot.transform);
		FitOrbitalToCamera(pivot, nextOrbital);

		Rotation rotation = pivot.AddComponent<Rotation>();
		rotation.rotationSpeed = 90f;

		if (currentOrbital != null)
		{
			currentOrbital.SetActive(false);
			Destroy(currentOrbital);
		}	
		currentOrbital = pivot;

		Debug.Log($"Orbital carregado: {entry.prefab.name}");
	}

	private void FitOrbitalToCamera(GameObject pivot, GameObject model)
	{
		Camera cam = targetCamera != null ? targetCamera : Camera.main;
		if (cam == null)
		{
			Debug.LogError("Nenhuma câmera encontrada.");
			return;
		}

		Renderer[] renderers = model.GetComponentsInChildren<Renderer>();
		if (renderers.Length == 0)
		{
			Debug.LogWarning("Orbital sem Renderer.");
			return;
		}

		// Bounding box que engloba todas as malhas.
		Bounds bounds = renderers[0].bounds;
		foreach (Renderer renderer in renderers)
		{
			bounds.Encapsulate(renderer.bounds);
		}

		// Move a geometria para o centro do pivô.
		model.transform.position += pivot.transform.position - bounds.center;

		// Raio de uma esfera que envolve a bounding box.
		float radius = bounds.extents.magnitude;

		if (radius <= 0f)
			return;

		// Distância do pivô à câmera.
		Vector3 cameraToPivot = pivot.transform.position - cam.transform.position;
		float distance = Vector3.Dot(cameraToPivot,	cam.transform.forward);

		// Menor campo de visão, vertical ou horizontal.
		float verticalHalfFov = cam.fieldOfView * Mathf.Deg2Rad / 2f;
		float horizontalHalfFov = Mathf.Atan(Mathf.Tan(verticalHalfFov) * cam.aspect);
		float halfFov = Mathf.Min(verticalHalfFov, horizontalHalfFov);

		// Escala segura para a rotação.
		float targetRadius = distance * Mathf.Sin(halfFov) * screenFill;
		float scaleFactor = targetRadius / radius;
		pivot.transform.localScale *= scaleFactor;
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