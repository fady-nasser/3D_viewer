using UnityEngine;
using UnityEngine.EventSystems;

public class HoverScale : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler
{
    [Header("Scale Settings")]
    public float scaleFactor = 1.1f;   // قد إيه يكبر لما تقفي عليه
    public float speed = 8f;           // سرعة التكبير والتصغير

    private Vector3 originalScale;
    private bool isHovered = false;

    private void Start()
    {
        originalScale = transform.localScale;
    }

    private void Update()
    {
        Vector3 targetScale = isHovered ? originalScale * scaleFactor : originalScale;
        transform.localScale = Vector3.Lerp(transform.localScale, targetScale, Time.unscaledDeltaTime * speed);
    }

    public void OnPointerEnter(PointerEventData eventData)
    {
        isHovered = true;
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        isHovered = false;
    }
}
