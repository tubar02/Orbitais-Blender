using System;
using System.IO;
using UnityEditor;
using UnityEngine;

[Serializable]
public class OrbitalJobConfig
{
	public OrbitalUnityConfig unity;
}

[Serializable]
public class OrbitalUnityConfig
{
	public OrbitalPresentationConfig presentation;
	public OrbitalRecordingConfig recording;
}

[Serializable]
public class OrbitalPresentationConfig
{
	public float rotation_speed;
	public float screen_fill;
	public int revolutions;
}

[Serializable]
public class OrbitalRecordingConfig
{
	public int fps;
	public int resolution;
	public int quality;
	public bool loop;
}

public static class OrbitalRunSettings
{
	private const string Key = "Orbitals.UnitySettings";

	public static OrbitalUnityConfig Current
	{
		get
		{
			string json = SessionState.GetString(Key, "");

			return string.IsNullOrEmpty(json) ? null : JsonUtility.FromJson<OrbitalUnityConfig>(json);
		}
	}

	public static void Load(string runDir)
	{
		string path = Path.Combine(runDir, "job.json");

		var job = JsonUtility.FromJson<OrbitalJobConfig>(File.ReadAllText(path));

		var settings = job?.unity;

		if (settings?.presentation == null || settings.recording == null)
		{
			throw new InvalidDataException("Configurações Unity ausentes no Job.");
		}

		var p = settings.presentation;
		var r = settings.recording;

		if (p.rotation_speed <= 0 ||
			float.IsNaN(p.rotation_speed) ||
			float.IsInfinity(p.rotation_speed) ||
			p.screen_fill <= 0 ||
			p.screen_fill > 0.95f ||
			p.revolutions < 1 ||
			r.fps < 1 ||
			r.resolution < 1 ||
			r.quality < 0 ||
			r.quality > 100)
		{
			throw new InvalidDataException("Parâmetros Unity inválidos no Job.");
		}

		SessionState.SetString(Key, JsonUtility.ToJson(settings));

		Debug.Log(
			$"Unity configurado: {r.fps} FPS, " +
			$"{r.resolution}px, " +
			$"{p.rotation_speed}°/s, " +
			$"{p.revolutions} revolução(ões)."
		);
	}

	public static void Clear()
	{
		SessionState.EraseString(Key);
	}
}