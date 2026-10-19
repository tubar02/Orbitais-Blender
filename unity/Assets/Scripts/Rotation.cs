using UnityEngine;

public class Rotation : MonoBehaviour
{
    public float rotationSpeedX;
    public float rotationSpeedY;
    public float rotationSpeedZ;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.Rotate(rotationSpeedX, rotationSpeedY, rotationSpeedZ);
    }
}
