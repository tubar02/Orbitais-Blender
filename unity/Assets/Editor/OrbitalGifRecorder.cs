
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Recorder;
using UnityEditor.Recorder.Encoder;
using UnityEditor.Recorder.Input;
using UnityEngine;

public static class OrbitalGifRecorder
{
	private const int FPS = 50;
	private const int Resolution = 1080;
	private static OrbitalPresenter presenter = UnityEngine.Object.FindAnyObjectByType<OrbitalPresenter>();
	private static RecorderController controller;

	private const string BatchBasis = "real";
	private const string BatchMode = "signed";
	private static List<OrbitalEntry> batchOrbitals;
	private static int batchIndex;

	private static float recordingStart;
	private static float recordingDuration;

	private static bool batchActive;
	private static bool batchRecording;
	private static bool startNextOrbital;

	[MenuItem("Tools/Orbitais/Gravar GIF")]
	public static void RecordGif()
	{
		if (CheckRecordCond()) return;

		Rotation rotation = presenter.CurrentRotation;
		if (rotation == null || rotation.rotationSpeed <= 0f)
		{
			Debug.LogError("Nenhuma rotação válida encontrada.");
			return;
		}
		
		// Inicia a gravação
		float duration = 3f * 360f / rotation.rotationSpeed;
		controller = CreateRecorder("orbital_teste", duration);
		controller.PrepareRecording();
		if (controller.StartRecording())
		{
			Debug.Log($"Iniciando gravação GIF: {duration} segundos");
		}
		else
		{
			Debug.LogError("Não foi possível iniciar a gravação.");
		}
	}

	[MenuItem("Tools/Orbitais/Gravar GIF", true)]
	private static bool ValidateRecordGif()
	{
		return EditorApplication.isPlaying;
	}

	[MenuItem("Tools/Orbitais/Gravar lote de Gifs")]
	public static bool RecordBatch()
	{
		if (CheckRecordCond()) return;

		batchOrbitals = presenter.GetOrbitals(BatchBasis, BatchMode);
		if (batchOrbitals.count == 0)
		{
			Debug.LogWarning($"Nenhum orbital encontrado: {BatchBasis}/{Batch_Mode}");
			return;
		}

		batchIndex = 0;
		batchActive = true;
		batchRecording = false;
		startNextOrbital = true;

		// Inscreve o método no ciclo de atualização do Editor.
		EditorApplication.update -= UpdateBatch;
		EditorApplication.update += UpdateBatch;

		Debug.Log($"Iniciando lote: {batchOrbitals.Count} orbitais ({BatchBasis}/{BatchMode})");
	}

	private static bool CheckRecordCond(bool? batch = null)
	{
		if (!EditorApplication.isPlaying)
		{
			Debug.LogError("Entre no Play Mode antes de gravar.");
			return true;
		}

		if (batch || (controller != null && controller.IsRecording()))
		{
			Debug.LogWarning("Uma gravação já está em andamento.");
			return true;
		}
	
		if (presenter == null)
		{
			Debug.LogError("Nenhum OrbitalPresenter encontrado.");
			return true;
		}
		return false;
	}
	
	private static void UpdateBatch()
	{
		
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
}