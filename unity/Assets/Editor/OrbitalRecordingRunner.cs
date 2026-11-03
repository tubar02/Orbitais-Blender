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
			EditorApplication.update -= WaitForPresenter;
			OrbitalGifRecorder.RecordingFinished -= OnRecordingFinished;
			OrbitalGifRecorder.CancelRecording();

			SessionState.SetBool(PendingKey, false);
			SessionState.SetBool(AutoExitKey, false);
			running = false;
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

		Debug.Log($"Iniciando Run pelo terminal: {runDir}");

		StartRun(runDir);
	}

	public static void StartRun(string runDir)
	{
		if (running || SessionState.GetBool(PendingKey, false))
			throw new InvalidOperationException("Já existe uma gravação solicitada.");

		if (!Directory.Exists(runDir))
			throw new DirectoryNotFoundException(runDir);

		// Importa os FBX e configura a Run ativa.
		OrbitalRunImporter.ImportRun(runDir);

		// Primeira versão: um orbital real, modo single.
		StartBatch("real", "single");
	}
}