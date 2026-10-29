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

		OrbitalPresenter presenter = Object.FindAnyObjectByType<OrbitalPresenter>();

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
}