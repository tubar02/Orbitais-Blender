using System;
using System.IO;
using UnityEditor;
using UnityEngine;

[InitializeOnLoad]
public static class OrbitalRecordingRunner
{
	// Chaves usadas para preservar a solicitação
	// durante a entrada em Play Mode.
	private const string AutoExitKey = "Orbitals.AutoExit";
	private const string PendingKey = "Orbitals.Pending";
	private const string BasisKey = "Orbitals.Basis";
	private const string ModeKey = "Orbitals.Mode";
	private const string CommandLineKey = "Orbitals.CommandLine";
	private const string RunDirectoryKey = "Orbitals.RunDirectory";
	private const string ExitCodeKey = "Orbitals.ExitCode";

	private static bool running;

	private static double waitStart;

	// Executado quando o Unity carrega esta classe.
	static OrbitalRecordingRunner()
	{
		EditorApplication.playModeStateChanged += OnPlayModeChanged;
	}

	public static void StartBatch(string basis, string mode)
	{
		if (running || SessionState.GetBool(PendingKey, false))
		{
			Debug.LogWarning("Já existe uma execução solicitada.");
			return;
		}

		// Salva os argumentos antes de mudar de modo.
		SessionState.SetString(BasisKey, basis);
		SessionState.SetString(ModeKey, mode);
		SessionState.SetBool(PendingKey, true);
		bool shouldAutoExit = !EditorApplication.isPlaying;
		SessionState.SetBool(AutoExitKey, shouldAutoExit);

		if (EditorApplication.isPlaying)
		{
			StartWhenReady();
		}
		else
		{
			EditorApplication.isPlaying = true;
		}
	}

	private static void OnPlayModeChanged(PlayModeStateChange state)
	{
		if (state == PlayModeStateChange.EnteredPlayMode &&	SessionState.GetBool(PendingKey, false))
		{
			StartWhenReady();
		}

		if (state == PlayModeStateChange.ExitingPlayMode)
		{
			if (SessionState.GetBool(CommandLineKey, false) && SessionState.GetInt(ExitCodeKey, -1) == -1)
			{
				SessionState.SetInt(ExitCodeKey, 1);
			}

			EditorApplication.update -= WaitForPresenter;
			OrbitalGifRecorder.RecordingFinished -= OnRecordingFinished;
			OrbitalGifRecorder.CancelRecording();

			SessionState.SetBool(PendingKey, false);
			SessionState.SetBool(AutoExitKey, false);
			running = false;
		}

		if (state == PlayModeStateChange.EnteredEditMode && SessionState.GetBool(CommandLineKey, false))
		{
			EditorApplication.delayCall += FinishCommandLineRun;
		}
	}

	private static void StartWhenReady()
	{
		waitStart = EditorApplication.timeSinceStartup;
		EditorApplication.update -= WaitForPresenter;
		EditorApplication.update += WaitForPresenter;
	}

	private static void WaitForPresenter()
	{
		if (!EditorApplication.isPlaying) return;

		OrbitalPresenter presenter = UnityEngine.Object.FindAnyObjectByType<OrbitalPresenter>();

		// Espera a inicialização do Presenter.
		if (presenter == null || presenter.CurrentEntry == null)
		{
			if (EditorApplication.timeSinceStartup - waitStart > 30.0)
			{
				Debug.LogError("O OrbitalPresenter não ficou pronto para gravar.");
				CancelRun();
			}
			return;
		}

		EditorApplication.update -= WaitForPresenter;

		string basis = SessionState.GetString(BasisKey, "real");
		string mode = SessionState.GetString(ModeKey, "signed");

		SessionState.SetBool(PendingKey, false);

		running = true;

		OrbitalGifRecorder.RecordingFinished -= OnRecordingFinished;
		OrbitalGifRecorder.RecordingFinished += OnRecordingFinished;

		Debug.Log($"Runner iniciou a gravação: {basis}/{mode}");

		if (!OrbitalGifRecorder.RecordBatch(basis, mode))
		{
			Debug.LogError("Não foi possível iniciar o lote.");
			CancelRun();
		}
	}

	private static void OnRecordingFinished(bool success)
	{
		OrbitalGifRecorder.RecordingFinished -= OnRecordingFinished;

		running = false;

		if (SessionState.GetBool(CommandLineKey, false))
		{
			SessionState.SetInt(ExitCodeKey, success ? 0 : 1);
		}

		if (success)
			Debug.Log("Runner: gravação concluída com sucesso.");
		else
			Debug.LogError("Runner: gravação interrompida.");

		bool autoExit = SessionState.GetBool(AutoExitKey, false);
		if (autoExit && EditorApplication.isPlaying)
		{
			EditorApplication.isPlaying = false;
		}
		SessionState.SetBool(AutoExitKey, false);
	}

	private static void CancelRun()
	{
		EditorApplication.update -= WaitForPresenter;
		OrbitalGifRecorder.RecordingFinished -= OnRecordingFinished;

		SessionState.SetBool(PendingKey, false);
		running = false;

		bool autoExit = SessionState.GetBool(AutoExitKey, false);
		if (autoExit && EditorApplication.isPlaying) EditorApplication.isPlaying = false;
		SessionState.SetBool(AutoExitKey, false);
	}
	
	[MenuItem("Tools/Orbitais/Importar e gravar Run")]
	public static void StartRunFromMenu()
	{
		string runDir = EditorUtility.OpenFolderPanel(
			"Selecione a Run para gravar",
			"",
			""
		);

		if (string.IsNullOrEmpty(runDir))
			return;

		try
		{
			StartRun(runDir);
		}
		catch (Exception exception)
		{
			Debug.LogException(exception);
		}
	}

	public static void StartRunFromCommandLine()
	{
		string[] args = Environment.GetCommandLineArgs();
		string runDir = null;

		for (int i = 0; i < args.Length - 1; i++)
		{
			if (args[i] == "-orbitalsRun")
			{
				runDir = args[i + 1];
				break;
			}
		}

		if (string.IsNullOrWhiteSpace(runDir))
			throw new ArgumentException("Informe o caminho usando -orbitalsRun.");

		SessionState.SetBool(CommandLineKey, true);
		SessionState.SetString(RunDirectoryKey,	Path.GetFullPath(runDir));
		SessionState.SetInt(ExitCodeKey, -1);

		try
		{
			StartRun(runDir);
		}
		catch (Exception exception)
		{
			Debug.LogException(exception);
			EditorApplication.Exit(1);
		}
	}

	private static void FinishCommandLineRun()
	{
		if (!SessionState.GetBool(CommandLineKey, false))
			return;

		int exitCode = SessionState.GetInt(ExitCodeKey, 1);
		string runDir = SessionState.GetString(RunDirectoryKey, "");

		if (exitCode == 0)
		{
			string mode = SessionState.GetString(ModeKey, "single");
			string outputDir = Path.Combine(runDir, "unity", mode);

			string[] gifs = Directory.Exists(outputDir)	? Directory.GetFiles(outputDir, "*.gif") : Array.Empty<string>();

			bool valid = gifs.Length > 0;

			foreach (string gif in gifs)
			{
				if (new FileInfo(gif).Length == 0)
				{
					valid = false;
					break;
				}
			}

			if (!valid)
			{
				Debug.LogError("Gravação finalizada, mas nenhum GIF válido foi encontrado.");
				exitCode = 1;
			}
		}

		Debug.Log($"Unity finalizado. Código: {exitCode}");

		SessionState.SetBool(CommandLineKey, false);
		SessionState.EraseString(RunDirectoryKey);
		SessionState.EraseInt(ExitCodeKey);

		EditorApplication.Exit(exitCode);
	}

	public static void StartRun(string runDir)
	{
		if (running || SessionState.GetBool(PendingKey, false))
			throw new InvalidOperationException("Já existe uma gravação solicitada.");

		if (!Directory.Exists(runDir))
			throw new DirectoryNotFoundException(runDir);

		// Importa os FBX e configura a Run ativa.
		var (basis, mode) = OrbitalRunImporter.ImportRun(runDir);
		StartBatch(basis, mode);
	}
}