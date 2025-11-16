using UnityEngine;
using Unity.Cinemachine;
using UnityEngine.InputSystem; // ✅ Use new Input System

public class SplineDollyController : MonoBehaviour
{
    [SerializeField] private CinemachineSplineDolly dolly;
    [SerializeField] private float speed = 2f;

    private void Update()
    {
        if (dolly == null)
            return;

        float moveInput = 0f;

        // ✅ New Input System
        if (Keyboard.current.wKey.isPressed || Keyboard.current.upArrowKey.isPressed)
            moveInput = 1f;
        else if (Keyboard.current.sKey.isPressed || Keyboard.current.downArrowKey.isPressed)
            moveInput = -1f;

        // Move along the spline
        dolly.CameraPosition += moveInput * speed * Time.deltaTime;

        // Optional: clamp or loop position
        dolly.CameraPosition = Mathf.Clamp01(dolly.CameraPosition);
    }
}
