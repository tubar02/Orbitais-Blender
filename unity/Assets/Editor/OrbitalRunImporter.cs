using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
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

	public static (string basis, string[] modes) ImportRun(string runDir)
	{
		string runId = Path.GetFileName(Path.GetFullPath(runDir).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
		string blenderDir = Path.Combine(runDir, "blender");

		if (!Directory.Exists(blenderDir))
			throw new DirectoryNotFoundException($"Diretório 'blender' não encontrado na Run: {blenderDir}");

		string[] supportedModes = {"single", "signed", "multilayer", "point_cloud"};
		string [] modes = supportedModes.Where(mode =>
		{
			string folder = Path.Combine(blenderDir, mode);
			return Directory.Exists(folder) && Directory.GetFiles(folder, "*.fbx").Length > 0;
		}).ToArray();

		if (modes.Length == 0)
		{
			throw new Exception("Nenhuma representação suportada encontrada");
		}

		string[] files = modes.SelectMany(mode => Directory.GetFiles(Path.Combine(blenderDir, mode), "*.fbx")).ToArray();
		string basis = null;
		foreach (string file in files)
		{
			string name = Path.GetFileNameWithoutExtension(file);

			Match match = Regex.Match(name,	@"^orbital_n\d+_l\d+_m-?\d+_(real|complex)_(single|signed|multilayer|point_cloud)$", RegexOptions.IgnoreCase);

			if (!match.Success)
				throw new Exception($"Nome de FBX inválido: {name}");

			string fileBasis = match.Groups[1].Value.ToLowerInvariant();
			string fileMode = match.Groups[2].Value.ToLowerInvariant();
			string sourceMode = Path.GetFileName(Path.GetDirectoryName(file));

			if (fileMode != sourceMode)
				throw new Exception($"Modo inconsistente no FBX: {name}");

			if (basis == null)
				basis = fileBasis;
			else if (basis != fileBasis)
				throw new Exception("A Run contém múltiplas bases.");
		}

		if (modes.Contains("signed") && basis != "real") throw new Exception("signed exige base real.");
		if (files.Select(Path.GetFileName).Distinct(StringComparer.OrdinalIgnoreCase).Count() != files.Length)
		{
			throw new Exception("Nomes de FBX duplicados");
		}

		string assetFolder = $"Assets/Orbitals/{runId}";
		string targetDir = Path.Combine(Application.dataPath, "Orbitals", runId);

		Directory.CreateDirectory(targetDir);

		foreach (string file in files)
		{
			string destination = Path.Combine(targetDir, Path.GetFileName(file));

			if (File.Exists(destination))
			{
				// Garante que a cópia corresponde ao FBX original.
				using var sha = SHA256.Create();
				using var source = File.OpenRead(file);
				using var existing = File.OpenRead(destination);

				if (!sha.ComputeHash(source).SequenceEqual(sha.ComputeHash(existing)))
				{
					throw new IOException($"FBX importado diferente do original: {destination}");
				}

				continue;
			}

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
			$"Base: {basis}, Modos: {string.Join(",", modes)}"
		);

		return (basis, modes);
	}
}