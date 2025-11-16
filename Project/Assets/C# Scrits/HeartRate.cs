using UnityEngine;
using TMPro;  // If using TextMeshPro

public class HeartRateController : MonoBehaviour
{
    [Header("UI Input")]
    public TMP_InputField heartRateInput;

    [Header("Particle System")]
    public ParticleSystem bloodCellParticles;

    [Header("Speed Settings")]
    public float baseBPM = 60f;   // Normal resting heart rate
    public float baseSpeed = 1f;  // Particle speed at base BPM
    public float speedMultiplier = 0.02f;  // How much speed changes per BPM difference

    private ParticleSystem.MainModule mainModule;

    void Start()
    {
        if (bloodCellParticles != null)
            mainModule = bloodCellParticles.main;

        // Add listener to detect user input changes
        heartRateInput.onEndEdit.AddListener(OnHeartRateChanged);
    }

    void OnHeartRateChanged(string bpmText)
    {
        if (float.TryParse(bpmText, out float bpm))
        {
            // Compute new speed proportionally
            float newSpeed = baseSpeed + (bpm - baseBPM) * speedMultiplier;

            // Clamp so it doesn’t get extreme
            newSpeed = Mathf.Clamp(newSpeed, 0.1f, 10f);

            // Apply new speed
            mainModule.startSpeed = newSpeed;

            Debug.Log($"Heart rate: {bpm} BPM → Particle speed: {newSpeed}");
        }
        else
        {
            Debug.LogWarning("Invalid BPM input!");
        }
    }
}
