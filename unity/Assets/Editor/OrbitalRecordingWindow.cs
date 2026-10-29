
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
		modeIndex = EditorGUILayout.Popup("Modo", modeIndex, modes);
		EditorGUILayout.Space();

		if (GUILayout.Button("Gravar lote"))
		{
			OrbitalRecordingRunner.StartBatch(bases[basisIndex], modes[modeIndex]);
		}
	}
}
