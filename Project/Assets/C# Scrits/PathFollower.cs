using UnityEngine;
using UnityEngine.Splines; // important for spline API

[RequireComponent(typeof(ParticleSystem))]
public class SplineParticleFollower : MonoBehaviour
{
    public SplineContainer spline; // assign your spline here
    public float duration = 5f;    // time to complete spline
    private float t = 0f;

    private ParticleSystem ps;
    private ParticleSystem.Particle[] particles;

    void Start()
    {
        ps = GetComponent<ParticleSystem>();
        particles = new ParticleSystem.Particle[ps.main.maxParticles];
    }

    void Update()
    {
        // Get how much of the spline should be followed this frame
        t += Time.deltaTime / duration;
        if (t > 1f) t = 0f; // loop

        // Sample spline position and direction
        Vector3 position = spline.EvaluatePosition(t);
        Vector3 tangent = spline.EvaluateTangent(t);

        // Move particle system along spline
        transform.position = position;
        transform.rotation = Quaternion.LookRotation(tangent);

        // Optional: if you want particles to "emit" along the spline trail:
        // You can simulate emission rate based on movement
    }
}
