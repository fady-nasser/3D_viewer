using UnityEngine;

public class HidableObject : MonoBehaviour
{
    public Material OldMaterial;
    public Material NewMaterial;
    private Renderer rend;
    public Renderer[] rends;

    void Awake()
    {
        if (rends == null || rends.Length == 0)
            rends = GetComponentsInChildren<Renderer>();
    }

    public void SetNewMaterial()
    {
        foreach (Renderer r in rends)
            r.material = NewMaterial; // assign your material here
    }

    public void SetOldMaterial()
    {
        foreach (Renderer r in rends)
            r.material = OldMaterial; // assign your material here
    }

    public void SetOpacity(float value)
    {
        foreach (Renderer r in rends)
        {
            Color c = r.material.color;
            c.a = value;
            r.material.color = c;
        }
    }
}
