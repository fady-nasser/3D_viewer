using UnityEngine;
using System.Diagnostics;
using System.IO;
using Debug = UnityEngine.Debug;

public class RunPython : MonoBehaviour
{
    public string pythonExePath = @"C:\Users\Fady\AppData\Local\Programs\Python\Python311\python.exe";
    public string pythonScriptPath = @"C:\Users\Fady\Desktop\test.py";

    public void RunPythonScript()
    {
        try
        {
            if (!File.Exists(pythonScriptPath))
            {
                Debug.LogError($"❌ Python script not found at {pythonScriptPath}");
                return;
            }

            if (!File.Exists(pythonExePath) && pythonExePath != "python")
            {
                Debug.LogError($"❌ Python executable not found at {pythonExePath}");
                return;
            }

            // Build the full command string
            string command = $"/k \"\"{pythonExePath}\" \"{pythonScriptPath}\"\"";

            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                Arguments = command,
                UseShellExecute = true,   // required for showing CMD
                CreateNoWindow = false,   // show the CMD window
                WorkingDirectory = Path.GetDirectoryName(pythonScriptPath)
            };

            Process.Start(psi);

            Debug.Log("✅ CMD opened and Python script executed.");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"❌ Failed: {ex.Message}");
        }
    }
}
