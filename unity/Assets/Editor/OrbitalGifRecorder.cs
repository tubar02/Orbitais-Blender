
using System.IO;
using UnityEditor;
using UnityEditor.Recorder;
using UnityEditor.Recorder.Encoder;
using UnityEditor.Recorder.Input;
using UnityEngine;

public static class OrbitalGifRecorder
{
	private const int FPS = 60;
	private const int Duration = 12;
	private const int Resolution = 1024;

	private static RecorderController controller;

	[MenuItem("Tools/Orbitais/Gravar GIF")]
	public static void RecordGif()
	{
		if (!EditorApplication.isPlaying)
		{
			Debug.LogError("Entre no Play Mode antes de gravar.");
			return;
		}

		if (controller != null && controller.IsRecording())
		{
			Debug.LogWarning("Uma gravação já está em andamento.");
			return;
		}

		string outputDir = Path.Combine(Application.dataPath, "Recordings");

		// Configura o Movie Recorder
		MovieRecorderSettings movieSettings = ScriptableObject.CreateInstance<MovieRecorderSettings>();
		movieSettings.name = "Orbital GIF";
		movieSettings.Enabled = true;
		movieSettings.EncoderSettings = new GifEncoderSettings{Quality = 90u, Loop = true};
		movieSettings.ImageInputSettings = new GameViewInputSettings{OutputWidth = Resolution,OutputHeight = Resolution};
		movieSettings.OutputFile = Path.Combine(outputDir, "orbital_teste");

		// Configura a sessão
		RecorderControllerSettings controllerSettings =	ScriptableObject.CreateInstance<RecorderControllerSettings>();
		controllerSettings.AddRecorderSettings(movieSettings);
		controllerSettings.FrameRate = FPS;
		controllerSettings.CapFrameRate = true;
		int totalFrames = FPS * Duration;
		controllerSettings.SetRecordModeToFrameInterval(0, totalFrames - 1);

		// Inicia a gravação
		controller = new RecorderController(controllerSettings);
		controller.PrepareRecording();
		if (controller.StartRecording())
		{
			Debug.Log(
				$"Iniciando gravação GIF: {totalFrames} frames"
			);
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
}
