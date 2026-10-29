
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Recorder;
using UnityEditor.Recorder.Encoder;
using UnityEditor.Recorder.Input;
using UnityEngine;

public static class OrbitalGifRecorder
{
	private static RecorderController controller;
	private const int FPS = 50;
	private const int Resolution = 1080;	
	private static float recordingStart;
	private static float recordingDuration;

	private static OrbitalPresenter presenter;
	private static List<OrbitalEntry> batchOrbitals;
	private static int batchIndex;
	private static bool batchActive;
	private static bool batchRecording;
	private static bool startNextOrbital;

	[MenuItem("Tools/Orbitais/Gravar GIF")]
	public static void RecordGif()
	{
		if (CheckRecordCond()) return;

		OrbitalEntry entry = presenter.CurrentEntry;

		if (entry == null)
		{
			Debug.LogError("Nenhum orbital carregado.");
			return;
		}

		StartSequence(new List<OrbitalEntry> { entry });
	}

	[MenuItem("Tools/Orbitais/Gravar GIF", true)]
	private static bool ValidateRecordGif()
	{
		return EditorApplication.isPlaying;
	}

	public static void RecordBatch(string basis, string mode)
	{
		if (CheckRecordCond()) return;

		List<OrbitalEntry> orbitals = presenter.GetOrbitals(basis, mode);
		if (orbitals.Count == 0)
		{
			Debug.LogWarning($"Nenhum orbital encontrado: {basis}/{mode}");
			return;
		}

		StartSequence(orbitals);
	}

	[MenuItem("Tools/Orbitais/Gravar lote de Gifs", true)]
	private static bool ValidateRecordBatch()
	{
		return EditorApplication.isPlaying && !batchActive && (controller == null || !controller.IsRecording());
	}

	private static bool CheckRecordCond()
	{
		if (!EditorApplication.isPlaying)
		{
			Debug.LogError("Entre no Play Mode antes de gravar.");
			return true;
		}

		if (batchActive || (controller != null && controller.IsRecording()))
		{
			Debug.LogWarning("Uma gravação já está em andamento.");
			return true;
		}

		presenter = UnityEngine.Object.FindAnyObjectByType<OrbitalPresenter>();
		if (presenter == null)
		{
			Debug.LogError("Nenhum OrbitalPresenter encontrado.");
			return true;
		}
		return false;
	}

	private static RecorderController CreateRecorder(string fileName, float duration, bool manual = false)
	{
		string outputDir = Path.Combine(Application.dataPath, "Recordings");
		Directory.CreateDirectory(outputDir);
		
		MovieRecorderSettings movieSettings = ScriptableObject.CreateInstance<MovieRecorderSettings>();
		movieSettings.name = "Orbital GIF";
		movieSettings.Enabled = true;
		movieSettings.EncoderSettings = new GifEncoderSettings{Quality = 90u, Loop = true};
		movieSettings.ImageInputSettings = new GameViewInputSettings{OutputWidth = Resolution,OutputHeight = Resolution};
		movieSettings.OutputFile = Path.Combine(outputDir, fileName);

		RecorderControllerSettings controllerSettings =	ScriptableObject.CreateInstance<RecorderControllerSettings>();
		controllerSettings.AddRecorderSettings(movieSettings);
		controllerSettings.FrameRate = FPS;
		controllerSettings.CapFrameRate = true;
		

		if (manual)
		{
			controllerSettings.SetRecordModeToManual();
		}
		else
		{
			controllerSettings.SetRecordModeToTimeInterval(0f, duration);
		}

		return new RecorderController(controllerSettings);
	}

	private static void StartSequence(List<OrbitalEntry> orbitals)
	{
		batchOrbitals = orbitals;
		batchIndex = 0;
		batchActive = true;
		batchRecording = false;
		startNextOrbital = true;

		// Inscreve o método no ciclo de atualização do Editor.
		EditorApplication.update -= UpdateBatch;
		EditorApplication.update += UpdateBatch;

		Debug.Log($"Iniciando gravação de {batchOrbitals.Count} orbital(is).");
	}

	private static void UpdateBatch()
	{
		// Interrompe se sair do Play Mode.
		if (!EditorApplication.isPlaying || presenter == null)
		{
			FinishBatch();
			return;
		}

		// Há outro orbital para começar?
		if (startNextOrbital)
		{
			startNextOrbital = false;
			StartNextOrbital();
			return;
		}

		// Se não estamos gravando, não há nada a acompanhar.
		if (!batchRecording)
			return;

		// Confirma que o Recorder continua ativo.
		if (controller == null || !controller.IsRecording())
		{
			Debug.LogError("A gravação foi interrompida.");
			FinishBatch();
			return;
		}

		// Mede quanto tempo simulado passou.
		float elapsed = Time.time - recordingStart;

		if (elapsed < recordingDuration)
			return;

		// Duração alcançada: encerra a gravação atual.
		controller.StopRecording();

		controller = null;
		batchRecording = false;

		Debug.Log($"GIF {batchIndex + 1} finalizado.");

		// Avança para o próximo orbital.
		batchIndex++;
		startNextOrbital = true;
	}
	
	private static void StartNextOrbital()
	{
		// Não há mais orbitais?
		if (batchIndex >= batchOrbitals.Count)
		{
			Debug.Log("Lote concluído!");
			FinishBatch();
			return;
		}

		OrbitalEntry entry = batchOrbitals[batchIndex];
		presenter.LoadOrbital(entry.n, entry.l, entry.m, entry.basis, entry.mode);
		Rotation rotation = presenter.CurrentRotation;
		if (rotation == null || rotation.rotationSpeed <= 0f)
		{
			Debug.LogError("Rotação inválida.");
			FinishBatch();
			return;
		}
		recordingDuration = 3f * 360f / rotation.rotationSpeed;
		string fileName = $"orbital_n{entry.n}_l{entry.l}_m{entry.m}_{entry.basis}_{entry.mode}";

		try
		{
			controller = CreateRecorder(fileName, recordingDuration, manual: true);
			controller.PrepareRecording();

			if (!controller.StartRecording())
			{
				Debug.LogError($"Falha ao gravar {fileName}");
				FinishBatch();
				return;
			}

			recordingStart = Time.time;
			batchRecording = true;
			Debug.Log($"Gravando {batchIndex + 1}/{batchOrbitals.Count}: {fileName}");
		}
		catch (System.Exception exception)
		{
			Debug.LogException(exception);
			FinishBatch();
		}
	}

	
	private static void FinishBatch()
	{
		// Para de receber chamadas do Editor.
		EditorApplication.update -= UpdateBatch;

		// Encerra a gravação, caso ainda esteja ativa.
		if (controller != null && controller.IsRecording())
		{
			controller.StopRecording();
		}

		controller = null;
		batchOrbitals = null;
		batchIndex = 0;
		batchActive = false;
		batchRecording = false;
		startNextOrbital = false;
	}
}