    using UnityEngine;
    using UnityEngine.SceneManagement;

    public class SceneLoader : MonoBehaviour
    {
        public void LoadSceneByIndex(int sceneIndex)
    {
            Debug.Log("Loading scene with index: " + sceneIndex);
            SceneManager.LoadScene(sceneIndex);
        }

        public void LoadSceneByName(string sceneName)
        {
            SceneManager.LoadScene(sceneName);
        }
    }