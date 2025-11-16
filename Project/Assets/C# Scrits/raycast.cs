using UnityEngine;
using UnityEngine.UI; 
using TMPro; // ADD THIS

public class ObjectSelector : MonoBehaviour
{
    public TextMeshProUGUI objectNameText;   // <-- TextMeshPro instead of Text
    public Slider opacitySlider;

    private Renderer currentObjectRenderer;

    void Start()
    {
        opacitySlider.onValueChanged.AddListener(OnSliderValueChanged);
    }

    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            RaycastHit hit;

            if (Physics.Raycast(ray, out hit))
            {
                currentObjectRenderer = hit.collider.gameObject.GetComponent<Renderer>();

                if (currentObjectRenderer != null)
                {
                    objectNameText.text = hit.collider.gameObject.name;

                    Color color = currentObjectRenderer.material.color;
                    opacitySlider.value = color.a;
                }
            }
        }
    }

    void OnSliderValueChanged(float value)
    {
        if (currentObjectRenderer != null)
        {
            Color color = currentObjectRenderer.material.color;
            color.a = value;
            currentObjectRenderer.material.color = color;
        }
    }
}
