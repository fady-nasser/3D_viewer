using UnityEngine;

public class AutoMeshCollider : MonoBehaviour
{
    void Awake()
    {
        foreach (Transform child in GetComponentsInChildren<Transform>())
        {
            Mesh mesh = null;

            // Standard Mesh
            MeshFilter mf = child.GetComponent<MeshFilter>();
            if (mf != null) mesh = mf.sharedMesh;

            // If animated character / deformable mesh
            if (mesh == null)
            {
                SkinnedMeshRenderer smr = child.GetComponent<SkinnedMeshRenderer>();
                if (smr != null) mesh = smr.sharedMesh;
            }

            if (mesh != null) AddCollider(child.gameObject, mesh); 
        }
    }

    void AddCollider(GameObject obj, Mesh mesh)
    {
        MeshCollider mc = obj.GetComponent<MeshCollider>();
        if (mc == null) mc = obj.AddComponent<MeshCollider>();

        mc.sharedMesh = mesh;
        mc.convex = false; // change to true ONLY if you want physics like rigidbody
    }
}
