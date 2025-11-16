using UnityEngine;

public class FocusController : MonoBehaviour
{
    public float focusSpeed = 5f; // Smooth focus speed
    public float orbitSpeed = 200f; // Right mouse orbit speed
    public float fadeSpeed = 5f;
    public float minDistance = 2f;

    private Camera cam;
    private Transform focusedTarget = null;
    private bool isFocusing = false;
    private Vector3 focusOffset;

    void Start()
    {
        cam = Camera.main;
    }

    void Update()
    {
        if (Input.GetMouseButtonDown(0)) // Click part
            TrySelectPart();

        if (Input.GetKeyDown(KeyCode.F)) // Toggle focus
            ToggleFocus();

        if (isFocusing && focusedTarget != null)
        {
            SmoothFocus();
            HandleOrbit();
        }
    }

    void TrySelectPart()
    {
        Ray ray = cam.ScreenPointToRay(Input.mousePosition);
        if (Physics.Raycast(ray, out RaycastHit hit))
            focusedTarget = hit.transform;
    }

    void ToggleFocus()
    {
        if (!isFocusing && focusedTarget != null)
        {
            EnterFocus();
        }
        else
        {
            ExitFocus();
        }
    }

    void EnterFocus()
    {
        isFocusing = true;
        Vector3 dir = (cam.transform.position - focusedTarget.position).normalized;
        focusOffset = dir * minDistance;

        foreach (Renderer r in FindObjectsOfType<Renderer>())
            if (r.transform != focusedTarget)
                StartCoroutine(FadeObject(r, 0.1f));
    }

    void ExitFocus()
    {
        isFocusing = false;

        foreach (Renderer r in FindObjectsOfType<Renderer>())
            StartCoroutine(FadeObject(r, 1f));
    }

    void SmoothFocus()
    {
        Vector3 targetPos = focusedTarget.position + focusOffset;
        cam.transform.position = Vector3.Lerp(cam.transform.position, targetPos, Time.deltaTime * focusSpeed);
        cam.transform.LookAt(focusedTarget);
    }

    void HandleOrbit()
    {
        if (Input.GetMouseButton(1)) // RIGHT MOUSE DRAG
        {
            float rotX = Input.GetAxis("Mouse X") * orbitSpeed * Time.deltaTime;
            cam.transform.RotateAround(focusedTarget.position, Vector3.up, rotX);
            focusOffset = cam.transform.position - focusedTarget.position;
        }
    }

    System.Collections.IEnumerator FadeObject(Renderer r, float targetAlpha)
    {
        Material mat = r.material;
        Color c = mat.color;
        while (Mathf.Abs(c.a - targetAlpha) > 0.01f)
        {
            c.a = Mathf.Lerp(c.a, targetAlpha, Time.deltaTime * fadeSpeed);
            mat.color = c;
            yield return null;
        }
    }
}
