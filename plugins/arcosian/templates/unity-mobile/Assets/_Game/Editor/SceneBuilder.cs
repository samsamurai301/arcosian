using System.IO;
using Game.Presentation;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Game.EditorTools
{
    /// <summary>
    /// Generates Assets/_Game/Scenes/Main.unity (camera + Bootstrap) and applies the mobile player settings.
    /// Idempotent: run it again any time. Batch: -executeMethod Game.EditorTools.SceneBuilder.BuildAll
    /// </summary>
    public static class SceneBuilder
    {
        public const string ScenePath = "Assets/_Game/Scenes/Main.unity";
        private const string TuningPath = "Assets/_Game/Data/tuning.json";
        private const string PlaceholderBundleId = "com.example.mergenumbers";

        public static void BuildAll()
        {
            GsArgs.Run("SceneBuilder.BuildAll", () =>
            {
                Build();
                return 0;
            });
        }

        [MenuItem("Game/Build Scene and Settings")]
        public static void Build()
        {
            AssetDatabase.Refresh();
            Directory.CreateDirectory(Path.Combine(Application.dataPath, "_Game/Scenes"));

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var camGo = new GameObject("Main Camera", typeof(Camera), typeof(AudioListener));
            camGo.tag = "MainCamera";
            var cam = camGo.GetComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.10f, 0.11f, 0.14f);
            cam.orthographic = true;

            var bootGo = new GameObject("Bootstrap");
            var boot = bootGo.AddComponent<Bootstrap>();
            var tuning = AssetDatabase.LoadAssetAtPath<TextAsset>(TuningPath);
            if (tuning == null) Debug.LogWarning("[gs] " + TuningPath + " not imported; Bootstrap will use built-in defaults.");
            var so = new SerializedObject(boot);
            so.FindProperty("tuningJson").objectReferenceValue = tuning;
            so.ApplyModifiedPropertiesWithoutUndo();

            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new IOException("could not save " + ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            ConfigurePlayerSettings();
            AssetDatabase.SaveAssets();
            Debug.Log("[gs] built " + ScenePath);
        }

        private static void ConfigurePlayerSettings()
        {
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.Portrait;
            PlayerSettings.allowedAutorotateToPortrait = true;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = false;
            PlayerSettings.allowedAutorotateToLandscapeRight = false;

            // Replace the bundle id (reverse-DNS, one per store) before release; only touch Unity's default.
            foreach (NamedBuildTarget target in new[] { NamedBuildTarget.Android, NamedBuildTarget.iOS })
            {
                string id = PlayerSettings.GetApplicationIdentifier(target);
                if (string.IsNullOrEmpty(id) || id.StartsWith("com.Company.") || id.StartsWith("com.DefaultCompany."))
                    PlayerSettings.SetApplicationIdentifier(target, PlaceholderBundleId);
            }

            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel24;
            PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        }
    }
}
