using UnityEngine;

public class Rotation : MonoBehaviour
{
    public float rotationSpeed;

    private int rotMod = 1;
    private float angle = 0f;
    private Quaternion initialRotation;

    void Start()
    {
        initialRotation = transform.rotation;
    }

    // Update is called once per frame
    void Update()
    {
        float rotationStep = rotationSpeed * Time.deltaTime;

        if (rotMod == 1)
        {
            transform.Rotate(0, 0, rotationStep);
        }
        else if (rotMod == 2)
        {
			transform.Rotate(rotationStep, 0, 0);
        }
        else if (rotMod == 3)
        {
            transform.Rotate(0, rotationStep, 0);
        }
        else 
        {
            rotMod = 1;
        }

        angle += rotationStep;

        if (angle >= 360f)
        {   
            transform.rotation = initialRotation;
            angle = 0f;
            rotMod++;
        }
    }
}
