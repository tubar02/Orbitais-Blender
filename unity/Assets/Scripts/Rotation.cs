using UnityEngine;

public class Rotation : MonoBehaviour
{
	public float rotationSpeed = 90f;
	public int revolutions = 3;

	private float elapsedTime = 0f;
	private float rotationDuration;
	private float totalDuration;

	private Quaternion initialRotation;

	void Start()
	{
		initialRotation = transform.localRotation;

		rotationDuration = 360f / rotationSpeed;
		totalDuration = revolutions * rotationDuration;
	}

	void Update()
	{
		if (rotationSpeed <= 0f)
			return;

		elapsedTime += Time.deltaTime;

		float cycleTime = elapsedTime % totalDuration;
		int axisIndex = Mathf.FloorToInt(cycleTime / rotationDuration) % 3;
		float axisTime = cycleTime % rotationDuration;
		float angle = rotationSpeed * axisTime;

		Vector3 axis = axisIndex switch
		{
			0 => Vector3.up,
			1 => Vector3.right,
			2 => Vector3.forward,
			_ => Vector3.up
		};

		transform.localRotation = initialRotation * Quaternion.AngleAxis(angle, axis);
	}
}