
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

public static class OrbitalRunImporter
{
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

	public static void ImportRun(string runDir)
	{
		string runId = Path.GetFileName(Path.GetFullPath(runDir).TrimEnd(Path.DirectorySeparatorChar));
		string sourceDir = Path.Combine(runDir, "blender", "single");

		if (!Directory.Exists(sourceDir))
			throw new DirectoryNotFoundException(sourceDir);

		string[] files = Directory.GetFiles(sourceDir, "*.fbx");

		if (files.Length == 0)
			throw new Exception("Nenhum FBX encontrado na Run.");

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

		Debug.Log($"Run {runId}: {files.Length} FBX importado(s).");
	}
}