using UnityEngine;
using UnityEngine.InputSystem;

public class OrbitalCamera : MonoBehaviour
{
    [Header("Target Settings")]
    [Tooltip("The object the camera will orbit around")]
    public Transform target;

    [Header("Rotation Settings")]
    [Tooltip("Speed of horizontal rotation")]
    public float horizontalSpeed = 100f;
    
    [Tooltip("Speed of vertical rotation")]
    public float verticalSpeed = 100f;

    [Header("Zoom Settings")]
    [Tooltip("Speed of zooming with scroll wheel")]
    public float scrollZoomSpeed = 2f;
    
    [Tooltip("Speed of zooming with +/- keys")]
    public float keyZoomSpeed = 5f;

    [Header("Initial Settings")]
    [Tooltip("Starting distance from target")]
    public float startDistance = 5f;

    private float currentDistance;
    private float horizontalAngle;
    private float verticalAngle;

    void Start()
    {
        if (target == null)
        {
            Debug.LogError("Target is not assigned! Please assign a target in the Inspector.");
            return;
        }

        // Set initial distance
        currentDistance = startDistance;

        // Calculate initial angles based on camera's starting position relative to target
        Vector3 direction = transform.position - target.position;
        horizontalAngle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
        verticalAngle = Mathf.Asin(direction.y / direction.magnitude) * Mathf.Rad2Deg;
    }

    void LateUpdate()
    {
        if (target == null) return;

        // Get keyboard reference
        Keyboard keyboard = Keyboard.current;
        Mouse mouse = Mouse.current;

        if (keyboard == null) return;

        // Handle rotation input (WASD or Arrow Keys)
        float horizontalInput = 0f;
        float verticalInput = 0f;

        // Horizontal input (A/D or Left/Right arrows)
        if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed)
            horizontalInput = 1f;
        if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed)
            horizontalInput = -1f;

        // Vertical input (W/S or Up/Down arrows)
        if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed)
            verticalInput = 1f;
        if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed)
            verticalInput = -1f;

        horizontalAngle += horizontalInput * horizontalSpeed * Time.deltaTime;
        verticalAngle += verticalInput * verticalSpeed * Time.deltaTime;

        // Handle zoom input
        // Scroll wheel
        if (mouse != null)
        {
            float scrollInput = mouse.scroll.ReadValue().y;
            currentDistance -= scrollInput * scrollZoomSpeed * Time.deltaTime;
        }

        // +/- keys (including numpad and equals for +)
        if (keyboard.equalsKey.isPressed || keyboard.numpadPlusKey.isPressed)
        {
            currentDistance -= keyZoomSpeed * Time.deltaTime;
        }
        if (keyboard.minusKey.isPressed || keyboard.numpadMinusKey.isPressed)
        {
            currentDistance += keyZoomSpeed * Time.deltaTime;
        }

        // Calculate new camera position on the sphere
        float horizontalRad = horizontalAngle * Mathf.Deg2Rad;
        float verticalRad = verticalAngle * Mathf.Deg2Rad;

        // Convert spherical coordinates to Cartesian coordinates
        float x = currentDistance * Mathf.Cos(verticalRad) * Mathf.Sin(horizontalRad);
        float y = currentDistance * Mathf.Sin(verticalRad);
        float z = currentDistance * Mathf.Cos(verticalRad) * Mathf.Cos(horizontalRad);

        // Set camera position
        transform.position = target.position + new Vector3(x, y, z);

        // Make camera look at target
        transform.LookAt(target);
    }
}