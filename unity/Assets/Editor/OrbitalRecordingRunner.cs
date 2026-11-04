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
		StartBatch(basis, new[] {mode});
	}

	public static void StartBatch(string basis, string[] modes)
	{
		if (running || SessionState.GetBool(PendingKey, false))
		{
			Debug.LogWarning("Já existe uma execução solicitada.");
			return;
		}

		if (modes == null || modes.Length == 0) throw new ArgumentException("Nenhuma representação solicitada.");

		// Salva os argumentos antes de mudar de modo.
		SessionState.SetString(BasisKey, basis);
		SessionState.SetString(ModeKey, string.Join(",", modes));
		SessionState.SetBool(PendingKey, true);
		bool shouldAutoExit = !EditorApplication.isPlaying;
		SessionState.SetBool(AutoExitKey, shouldAutoExit);

		if (EditorApplication.isPlaying) StartWhenReady();
		else EditorApplication.isPlaying = true;
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

		var settings = OrbitalRunSettings.Current?.presentation;
		if (settings != null)
		{
			presenter.ConfigurePresentation(settings.rotation_speed, settings.screen_fill, settings.revolutions);
		}

		string basis = SessionState.GetString(BasisKey, "real");
		string[] modes = SessionState.GetString(ModeKey, "").Split(new[] {","}, StringSplitOptions.RemoveEmptyEntries);

		SessionState.SetBool(PendingKey, false);

		running = true;

		OrbitalGifRecorder.RecordingFinished -= OnRecordingFinished;
		OrbitalGifRecorder.RecordingFinished += OnRecordingFinished;

		Debug.Log(
			$"Runner iniciou a gravação: " +
			$"{basis}/{string.Join(",", modes)}"
		);

		if (!OrbitalGifRecorder.RecordBatch(basis, modes))
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
			string[] modes = SessionState.GetString(ModeKey, "single").Split(new[] {","}, StringSplitOptions.RemoveEmptyEntries);
			bool valid = modes.Length > 0;

			foreach (string mode in modes)
			{
				string outputDir = Path.Combine(runDir, "unity", mode);
				string[] gifs = Directory.Exists(outputDir)	? Directory.GetFiles(outputDir, "*.gif") : Array.Empty<string>();

				if (gifs.Length == 0 || Array.Exists(gifs, gif => new FileInfo(gif).Length == 0))
				{
					Debug.LogError($"GIFs ausentes ou vazios: {mode}");
					valid = false;
					break;
				}
			}			

			if (!valid)	exitCode = 1;
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
		var (basis, modes) = OrbitalRunImporter.ImportRun(runDir);
		OrbitalRunSettings.Load(runDir);
		StartBatch(basis, modes);
	}
}