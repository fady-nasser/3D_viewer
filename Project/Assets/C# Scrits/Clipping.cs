using UnityEngine;
using UnityEngine.UI;
using System.IO;
using System.Collections.Generic;

public class NiftiClippingPlanes : MonoBehaviour
{
    [Header("UI Elements")]
    public Slider axialSlider;
    public Slider sagittalSlider;
    public Slider coronalSlider;
    public Dropdown datasetDropdown;
    
    [Header("UI Text (Optional)")]
    public Text axialText;
    public Text sagittalText;
    public Text coronalText;

    [Header("Plane GameObjects")]
    public GameObject axialPlane;
    public GameObject sagittalPlane;
    public GameObject coronalPlane;

    [Header("Spacing Settings")]
    [Tooltip("Scale factor for plane movement (typically 1.0)")]
    public float spacingScale = 1.0f;

    private string currentDatasetFolder;
    private string axialFolder;
    private string sagittalFolder;
    private string coronalFolder;

    private int axialSliceCount;
    private int sagittalSliceCount;
    private int coronalSliceCount;

    private int dimX, dimY, dimZ;

    private Material axialMaterial;
    private Material sagittalMaterial;
    private Material coronalMaterial;

    private Vector3 axialStartPos;
    private Vector3 sagittalStartPos;
    private Vector3 coronalStartPos;

    private bool isLoaded = false;

    // Dataset names
    private string[] datasetNames = { "Cardiovascular", "Dental", "Nervous", "Musculoskeletal", "Import" };

    void Start()
    {
        // Store initial plane positions
        if (axialPlane != null)
        {
            axialStartPos = axialPlane.transform.position;
            axialMaterial = axialPlane.GetComponent<Renderer>().material;
        }
        if (sagittalPlane != null)
        {
            sagittalStartPos = sagittalPlane.transform.position;
            sagittalMaterial = sagittalPlane.GetComponent<Renderer>().material;
        }
        if (coronalPlane != null)
        {
            coronalStartPos = coronalPlane.transform.position;
            coronalMaterial = coronalPlane.GetComponent<Renderer>().material;
        }

        // Setup dropdown
        if (datasetDropdown != null)
        {
            datasetDropdown.ClearOptions();
            List<string> options = new List<string>(datasetNames);
            Debug.Log("Adding datasets to dropdown: " + string.Join(", ", options));
            datasetDropdown.AddOptions(options);
            datasetDropdown.onValueChanged.AddListener(OnDatasetChanged);
        }

        // Setup slider listeners
        if (axialSlider != null)
            axialSlider.onValueChanged.AddListener(OnAxialSliderChanged);
        if (sagittalSlider != null)
            sagittalSlider.onValueChanged.AddListener(OnSagittalSliderChanged);
        if (coronalSlider != null)
            coronalSlider.onValueChanged.AddListener(OnCoronalSliderChanged);

        // Load the first dataset by default
        LoadDataset(0);
    }

    void OnDatasetChanged(int index)
    {
        LoadDataset(index);
    }

    void LoadDataset(int datasetIndex)
    {
        if (datasetIndex < 0 || datasetIndex >= datasetNames.Length)
        {
            Debug.LogError("Invalid dataset index: " + datasetIndex);
            return;
        }

        string datasetName = datasetNames[datasetIndex];
        Debug.Log($"Loading dataset: {datasetName}");

        // Setup folder paths
        string baseFolder = @"D:\MedicalData";
        currentDatasetFolder = Path.Combine(baseFolder, datasetName);
        axialFolder = Path.Combine(currentDatasetFolder, "Axial");
        sagittalFolder = Path.Combine(currentDatasetFolder, "Sagittal");
        coronalFolder = Path.Combine(currentDatasetFolder, "Coronal");

        Debug.Log($"Looking for slices in: {currentDatasetFolder}");

        // Check if folders exist
        if (!Directory.Exists(axialFolder))
        {
            Debug.LogError($"Axial folder not found: {axialFolder}");
            return;
        }
        if (!Directory.Exists(sagittalFolder))
        {
            Debug.LogError($"Sagittal folder not found: {sagittalFolder}");
            return;
        }
        if (!Directory.Exists(coronalFolder))
        {
            Debug.LogError($"Coronal folder not found: {coronalFolder}");
            return;
        }

        // Count slices in each folder
        string[] axialFiles = Directory.GetFiles(axialFolder, "axial_*.png");
        string[] sagittalFiles = Directory.GetFiles(sagittalFolder, "sagittal_*.png");
        string[] coronalFiles = Directory.GetFiles(coronalFolder, "coronal_*.png");

        axialSliceCount = axialFiles.Length;
        sagittalSliceCount = sagittalFiles.Length;
        coronalSliceCount = coronalFiles.Length;

        Debug.Log($"Found slices - Axial: {axialSliceCount}, Sagittal: {sagittalSliceCount}, Coronal: {coronalSliceCount}");

        if (axialSliceCount == 0 || sagittalSliceCount == 0 || coronalSliceCount == 0)
        {
            Debug.LogError("No slices found! Make sure to run the Python script first.");
            return;
        }

        // Read dimensions from dimensions.txt
        string dimensionsFile = Path.Combine(currentDatasetFolder, "dimensions.txt");
        if (File.Exists(dimensionsFile))
        {
            string[] dims = File.ReadAllText(dimensionsFile).Split(',');
            dimX = int.Parse(dims[0]);
            dimY = int.Parse(dims[1]);
            dimZ = int.Parse(dims[2]);
            Debug.Log($"Dimensions from file: {dimX} x {dimY} x {dimZ}");
        }
        else
        {
            // Fallback to slice counts
            dimX = sagittalSliceCount;
            dimY = coronalSliceCount;
            dimZ = axialSliceCount;
            Debug.LogWarning("dimensions.txt not found, using slice counts as dimensions");
        }

        // Scale planes according to dimensions
        if (axialPlane != null)
        {
            axialPlane.transform.localScale = new Vector3(dimX * 0.1f, 1f, dimY * 0.1f);
        }
        if (sagittalPlane != null)
        {
            sagittalPlane.transform.localScale = new Vector3(dimY * 0.1f, 1f, dimZ * 0.1f);
        }
        if (coronalPlane != null)
        {
            coronalPlane.transform.localScale = new Vector3(dimX * 0.1f, 1f, dimZ * 0.1f);
        }

        // Setup sliders - reset to center
        if (axialSlider != null)
        {
            axialSlider.minValue = 0;
            axialSlider.maxValue = axialSliceCount - 1;
            axialSlider.wholeNumbers = true;
            axialSlider.value = axialSliceCount / 2; // Center
        }

        if (sagittalSlider != null)
        {
            sagittalSlider.minValue = 0;
            sagittalSlider.maxValue = sagittalSliceCount - 1;
            sagittalSlider.wholeNumbers = true;
            sagittalSlider.value = sagittalSliceCount / 2; // Center
        }

        if (coronalSlider != null)
        {
            coronalSlider.minValue = 0;
            coronalSlider.maxValue = coronalSliceCount - 1;
            coronalSlider.wholeNumbers = true;
            coronalSlider.value = coronalSliceCount / 2; // Center
        }

        isLoaded = true;
        Debug.Log($"Dataset '{datasetName}' loaded successfully!");

        // Load initial slices at center
        LoadAxialSlice(axialSliceCount / 2);
        LoadSagittalSlice(sagittalSliceCount / 2);
        LoadCoronalSlice(coronalSliceCount / 2);
    }

    void OnAxialSliderChanged(float value)
    {
        if (isLoaded)
        {
            LoadAxialSlice((int)value);
            if (axialText != null)
                axialText.text = $"Axial: {(int)value}";
        }
    }

    void OnSagittalSliderChanged(float value)
    {
        if (isLoaded)
        {
            LoadSagittalSlice((int)value);
            if (sagittalText != null)
                sagittalText.text = $"Sagittal: {(int)value}";
        }
    }

    void OnCoronalSliderChanged(float value)
    {
        if (isLoaded)
        {
            LoadCoronalSlice((int)value);
            if (coronalText != null)
                coronalText.text = $"Coronal: {(int)value}";
        }
    }

    void LoadAxialSlice(int sliceIndex)
    {
        string path = Path.Combine(axialFolder, $"axial_{sliceIndex:D4}.png");
        LoadTextureToMaterial(path, axialMaterial);

        // Move plane along Y-axis (up/down)
        if (axialPlane != null)
        {
            float normalizedPosition = (float)sliceIndex / (axialSliceCount - 1); // 0 to 1
            float yPosition = (normalizedPosition - 0.5f) * dimZ * spacingScale; // Center at 0
            axialPlane.transform.position = axialStartPos + new Vector3(0, yPosition, 0);
        }
    }

    void LoadSagittalSlice(int sliceIndex)
    {
        string path = Path.Combine(sagittalFolder, $"sagittal_{sliceIndex:D4}.png");
        LoadTextureToMaterial(path, sagittalMaterial);

        // Move plane along X-axis (left/right)
        if (sagittalPlane != null)
        {
            float normalizedPosition = (float)sliceIndex / (sagittalSliceCount - 1); // 0 to 1
            float xPosition = (normalizedPosition - 0.5f) * dimX * spacingScale; // Center at 0
            sagittalPlane.transform.position = sagittalStartPos + new Vector3(xPosition, 0, 0);
        }
    }

    void LoadCoronalSlice(int sliceIndex)
    {
        string path = Path.Combine(coronalFolder, $"coronal_{sliceIndex:D4}.png");
        LoadTextureToMaterial(path, coronalMaterial);

        // Move plane along Z-axis (forward/back)
        if (coronalPlane != null)
        {
            float normalizedPosition = (float)sliceIndex / (coronalSliceCount - 1); // 0 to 1
            float zPosition = (normalizedPosition - 0.5f) * dimY * spacingScale; // Center at 0
            coronalPlane.transform.position = coronalStartPos + new Vector3(0, 0, zPosition);
        }
    }

    void LoadTextureToMaterial(string path, Material material)
    {
        if (material == null)
        {
            Debug.LogWarning("Material is null");
            return;
        }

        if (!File.Exists(path))
        {
            Debug.LogError("Slice file not found: " + path);
            return;
        }

        // Clean up old texture to prevent memory leaks
        if (material.mainTexture != null)
        {
            Destroy(material.mainTexture);
        }

        byte[] fileData = File.ReadAllBytes(path);
        Texture2D texture = new Texture2D(2, 2);
        texture.LoadImage(fileData);
        
        material.mainTexture = texture;
    }

    void OnDestroy()
    {
        // Clean up textures
        if (axialMaterial != null && axialMaterial.mainTexture != null)
            Destroy(axialMaterial.mainTexture);
        if (sagittalMaterial != null && sagittalMaterial.mainTexture != null)
            Destroy(sagittalMaterial.mainTexture);
        if (coronalMaterial != null && coronalMaterial.mainTexture != null)
            Destroy(coronalMaterial.mainTexture);
    }
}