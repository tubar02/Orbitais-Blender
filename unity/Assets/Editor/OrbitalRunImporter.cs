using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

public static class OrbitalRunImporter
{
	[MenuItem("Tools/Orbitais/Usar catálogo geral")]
	public static void UseGeneralCatalog()
	{
		SessionState.SetString(OrbitalPresenter.ActiveRunKey, "");
		OrbitalGifRecorder.UseDefaultOutputDirectory();
		Debug.Log("Catálogo geral ativado.");
	}

	[MenuItem("Tools/Orbitais/Importar FBX de uma Run")]
	public static void ImportFromMenu()
	{
		string runDir = EditorUtility.OpenFolderPanel(
			"Selecione a pasta da Run",
			"",
			""
		);

		if (string.IsNullOrEmpty(runDir))
			return;

		ImportRun(runDir);
	}

	public static (string basis, string mode) ImportRun(string runDir)
	{
		string runId = Path.GetFileName(Path.GetFullPath(runDir).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
		string blenderDir = Path.Combine(runDir, "blender");

		if (!Directory.Exists(blenderDir))
			throw new DirectoryNotFoundException($"Diretório 'blender' não encontrado na Run: {blenderDir}");

		string [] modes = {"single", "signed"};
		string [] availableModes = modes.Where(mode =>
		{
			string folder = Path.Combine(blenderDir, mode);
			return Directory.Exists(folder) && Directory.GetFiles(folder, "*.fbx").Length > 0;
		}).ToArray();

		if (availableModes.Length != 1)
			throw new Exception(
			"A Run deve conter exatamente uma " +
			"representação suportada: single ou signed."
		);

		string selectedMode = availableModes[0];
		string sourceDir = Path.Combine(blenderDir, selectedMode);
		string[] files = Directory.GetFiles(sourceDir, "*.fbx");

		// Descobre a base pelos nomes dos FBXs
		string basis = null;
		foreach (string file in files)
		{
			string name = Path.GetFileNameWithoutExtension(file);

			Match match = Regex.Match(name,	@"^orbital_n\d+_l\d+_m-?\d+_(real|complex)_(single|signed)$", RegexOptions.IgnoreCase);

			if (!match.Success)
				throw new Exception($"Nome de FBX inválido: {name}");

			string fileBasis = match.Groups[1].Value.ToLowerInvariant();
			string fileMode = match.Groups[2].Value.ToLowerInvariant();

			if (fileMode != selectedMode)
				throw new Exception($"Modo inconsistente: {name}");

			if (basis == null)
				basis = fileBasis;
			else if (basis != fileBasis)
				throw new Exception("A Run contém múltiplas bases.");
		}

		if (selectedMode == "signed" && basis != "real") throw new Exception("signed exige base real.");

		string assetFolder = $"Assets/Orbitals/{runId}";
		string targetDir = Path.Combine(Application.dataPath, "Orbitals", runId);

		if (Directory.Exists(targetDir))
			throw new IOException($"Esta Run já foi importada: {assetFolder}");

		Directory.CreateDirectory(targetDir);

		foreach (string file in files)
		{
			string destination = Path.Combine(targetDir, Path.GetFileName(file));
			File.Copy(file, destination);
		}

		AssetDatabase.Refresh();

		foreach (string file in files)
		{
			string assetPath = $"{assetFolder}/{Path.GetFileName(file)}";

			GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);

			if (model == null)
				throw new Exception($"Falha ao importar FBX: {assetPath}");
		}
		
		SessionState.SetString(OrbitalPresenter.ActiveRunKey, runId);
		OrbitalGifRecorder.SetOutputDirectory(Path.Combine(runDir, "unity"));
		Debug.Log(
			$"Run {runId}: {files.Length} FBX(s) importados. " +
			$"Base: {basis}, modo: {selectedMode}"
		);

		return (basis, selectedMode);
	}
}