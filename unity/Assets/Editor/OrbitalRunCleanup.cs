using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

public static class OrbitalRunCleanup
{
	private const string Root = "Assets/Orbitals";

	private static bool IsRunFolder(string path)
	{
		if (!path.StartsWith(Root + "/", StringComparison.Ordinal))
			return false;

		string name = Path.GetFileName(path);

		return Regex.IsMatch(name, @"^run_\d{8}_\d{6}_[0-9a-fA-F]{8}$");
	}

	[MenuItem("Tools/Orbitais/Limpar Run ativa...")]
	public static void CleanActiveRun()
	{
		if (!CanClean()) return;

		string runId = OrbitalPresenter.ActiveRunId;
		string folder = $"{Root}/{runId}";

		if (!IsRunFolder(folder) || !AssetDatabase.IsValidFolder(folder))
		{
			EditorUtility.DisplayDialog(
				"Limpeza",
				"Nenhuma Run importada está ativa.",
				"OK"
			);
			return;
		}

		CleanFolders(new[] { folder });
	}

	[MenuItem("Tools/Orbitais/Limpar todas as Runs importadas...")]
	public static void CleanAllRuns()
	{
		if (!CanClean()) return;

		if (!AssetDatabase.IsValidFolder(Root))
			return;

		string[] folders = AssetDatabase
			.GetSubFolders(Root)
			.Where(IsRunFolder)
			.ToArray();

		CleanFolders(folders);
	}

	private static bool CanClean()
	{
		if (EditorApplication.isPlayingOrWillChangePlaymode)
		{
			EditorUtility.DisplayDialog(
				"Limpeza indisponível",
				"Saia do Play Mode antes de limpar as Runs.",
				"OK"
			);
			return false;
		}

		return true;
	}

	private static void CleanFolders(string[] folders)
	{
		if (folders.Length == 0)
		{
			EditorUtility.DisplayDialog(
				"Limpeza",
				"Nenhuma Run importada encontrada.",
				"OK"
			);
			return;
		}

		bool confirmed = EditorUtility.DisplayDialog(
			"Confirmar limpeza",
			$"Apagar {folders.Length} pasta(s) importada(s)?\n\n" +
			"Isso removerá os assets dentro dessas pastas.\n" +
			"As Runs originais na pasta runs/ serão preservadas.",
			"Apagar cópias",
			"Cancelar"
		);

		if (!confirmed) return;

		int deleted = 0;

		foreach (string folder in folders)
		{
			if (AssetDatabase.DeleteAsset(folder))
			{
				deleted++;
			}
			else
			{
				Debug.LogError($"Falha ao remover: {folder}");
			}
		}

		string activeRun = OrbitalPresenter.ActiveRunId;

		if (!string.IsNullOrEmpty(activeRun) && !AssetDatabase.IsValidFolder($"{Root}/{activeRun}"))
		{
			OrbitalRunImporter.UseGeneralCatalog();
		}

		Debug.Log($"Limpeza concluída: {deleted}/{folders.Length} pastas removidas.");
	}
}