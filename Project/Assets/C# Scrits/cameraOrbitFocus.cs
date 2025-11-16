using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Linq;

public class ObjectSelectorAndOrbit : MonoBehaviour
{
    [Header("UI")]
    public TextMeshProUGUI objectNameText;
    public Slider opacitySlider;

    [Header("Speeds")]
    public float rotationSpeed = 100f;
    public float zoomSpeed = 5f;

    [Header("Zoom Limits")]
    public float minDistance = 0.5f;
    public float maxDistance = 100f;

    private Transform currentTargetTransform;
    private HidableObject currentHidableObject; // for new/old material control
    private HidableObject previousHidableObject;

    private Vector3 targetPoint;
    private float distance = 5f;

    private bool isIsolated = false;
    private Renderer[] allHidableRenderers;
    private List<Renderer> hiddenRenderers = new List<Renderer>();

    private bool isUsingNewMaterial = true; // tracks V toggle for current object

    void Start()
    {
        if (opacitySlider != null)
            opacitySlider.onValueChanged.AddListener(OnSliderValueChanged);
    }

    void Update()
    {
        // --- Click to select object ---
        if (Input.GetMouseButtonDown(0))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            if (Physics.Raycast(ray, out RaycastHit hit))
            {
                var go = hit.collider.gameObject;
                
                // Reset previous object material
                if (previousHidableObject != null)
                    previousHidableObject.SetOldMaterial();

                // Assign new selection
                previousHidableObject = currentHidableObject;
                currentTargetTransform = go.transform;
                currentHidableObject = go.GetComponent<HidableObject>();
                isUsingNewMaterial = true;

                if (currentHidableObject != null)
                    currentHidableObject.SetNewMaterial();

                // Renderer + Camera target setup
                Renderer[] rends = go.GetComponentsInChildren<Renderer>();
                if (rends.Length > 0)
                {
                    Bounds combined = rends[0].bounds;
                    for (int i = 1; i < rends.Length; i++)
                        combined.Encapsulate(rends[i].bounds);

                    targetPoint = combined.center;
                    float size = combined.extents.magnitude;
                    distance = size * 2f;
                }
                else
                {
                    targetPoint = go.transform.position;
                }

                if (objectNameText != null) objectNameText.text = go.name;
            }
        }

        // --- Toggle V: New <-> Old material ---
        if (currentHidableObject != null && Input.GetKeyDown(KeyCode.V))
        {
            if (isUsingNewMaterial)
            {
                currentHidableObject.SetOldMaterial();
                isUsingNewMaterial = false;
            }
            else
            {
                currentHidableObject.SetNewMaterial();
                isUsingNewMaterial = true;
            }
        }

        // --- F KEY ISOLATION ---
        if (currentTargetTransform != null && Input.GetKeyDown(KeyCode.F))
        {
            if (!isIsolated)
            {
                allHidableRenderers = FindObjectsOfType<Renderer>()
                    .Where(r => r.gameObject.CompareTag("Hidable")).ToArray();

                hiddenRenderers.Clear();
                foreach (var rend in allHidableRenderers)
                {
                    if (rend.gameObject != currentTargetTransform.gameObject)
                    {
                        rend.enabled = false;
                        hiddenRenderers.Add(rend);
                    }
                }
                isIsolated = true;
            }
            else
            {
                foreach (Renderer r in hiddenRenderers) r.enabled = true;
                hiddenRenderers.Clear();
                isIsolated = false;
            }
        }

        if (currentTargetTransform != null)
            OrbitCamera();
    }

    void OrbitCamera()
    {
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");

        Vector3 dir = (transform.position - targetPoint);
        float currentDist = dir.magnitude;
        Vector3 dirNorm = dir / currentDist;

        dirNorm = Quaternion.AngleAxis(h * rotationSpeed * Time.deltaTime, Vector3.up) * dirNorm;
        Vector3 rightAxis = Vector3.Cross(Vector3.up, dirNorm).normalized;
        dirNorm = Quaternion.AngleAxis(-v * rotationSpeed * Time.deltaTime, rightAxis) * dirNorm;

        if (Input.GetKey(KeyCode.Equals) || Input.GetKey(KeyCode.KeypadPlus)) currentDist -= zoomSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.Minus) || Input.GetKey(KeyCode.KeypadMinus)) currentDist += zoomSpeed * Time.deltaTime;

        currentDist = Mathf.Clamp(currentDist, minDistance, maxDistance);
        distance = currentDist;

        transform.position = targetPoint + dirNorm * currentDist;
        transform.LookAt(targetPoint);
    }

    void OnSliderValueChanged(float value)
    {
        if (currentHidableObject != null)
            currentHidableObject.SetOpacity(value);
    }
}
