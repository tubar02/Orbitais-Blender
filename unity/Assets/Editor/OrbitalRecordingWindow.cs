
using UnityEditor;
using UnityEngine;

public class OrbitalRecordingWindow : EditorWindow
{
	private readonly string[] bases = { "real", "complex" };
	private readonly string[] modes = { "single", "batch", "signed" };

	private int basisIndex = 0;
	private int modeIndex = 2;

	[MenuItem("Tools/Orbitais/Configurar gravações")]
	public static void ShowWindow()
	{
		GetWindow<OrbitalRecordingWindow>("Orbital GIF Recorder");
	}

	private void OnGUI()
	{
		EditorGUILayout.LabelField("Gravação de orbitais", EditorStyles.boldLabel);
		basisIndex = EditorGUILayout.Popup("Base", basisIndex, bases);
		modeIndex = EditorGUILayout.Popup("Modo", modeIndex,modes);
		EditorGUILayout.Space();

		using (new EditorGUI.DisabledScope(!EditorApplication.isPlaying))
		{
			if (GUILayout.Button("Gravar lote"))
			{
				OrbitalGifRecorder.RecordBatch(bases[basisIndex], modes[modeIndex]);
			}
		}

		if (!EditorApplication.isPlaying)
		{
			EditorGUILayout.HelpBox("Entre em Play Mode para iniciar a gravação.", MessageType.Info);
		}
	}
}
