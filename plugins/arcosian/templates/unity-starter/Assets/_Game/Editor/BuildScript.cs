using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Game.EditorTools
{
    /// <summary>
    /// Batch builds. Output path comes from -gsOut (relative paths are resolved against the project root).
    /// Exit codes: 0 built, 1 build failed or exception, 2 usage error (bad output path, missing keystore file).
    /// Android signing comes from environment variables, never from files in the repo:
    ///   GS_ANDROID_KEYSTORE_PATH, GS_ANDROID_KEYSTORE_PASS, GS_ANDROID_KEY_ALIAS, GS_ANDROID_KEY_PASS (defaults to the keystore pass).
    /// Optional GS_BUILD_NUMBER sets the Android version code / iOS build number.
    /// </summary>
    public static class BuildScript
    {
        public static void BuildAndroid()
        {
            GsArgs.Run("BuildScript.BuildAndroid", () => Build(BuildTarget.Android, "Builds/Android/game.aab"));
        }

        public static void BuildIOS()
        {
            GsArgs.Run("BuildScript.BuildIOS", () => Build(BuildTarget.iOS, "Builds/iOS"));
        }

        public static void BuildWindows()
        {
            GsArgs.Run("BuildScript.BuildWindows", () => Build(BuildTarget.StandaloneWindows64, "Builds/Windows/Game.exe"));
        }

        public static void BuildMacOS()
        {
            GsArgs.Run("BuildScript.BuildMacOS", () => Build(BuildTarget.StandaloneOSX, "Builds/macOS/Game.app"));
        }

        public static void BuildLinux()
        {
            GsArgs.Run("BuildScript.BuildLinux", () => Build(BuildTarget.StandaloneLinux64, "Builds/Linux/Game.x86_64"));
        }

        /// <summary>Unity calls the platform "Web"; the BuildTarget enum keeps the name WebGL.</summary>
        public static void BuildWeb()
        {
            GsArgs.Run("BuildScript.BuildWeb", () => Build(BuildTarget.WebGL, "Builds/Web"));
        }

        private static int Build(BuildTarget target, string defaultOut)
        {
            string output = GsArgs.Resolve(GsArgs.Get("-gsOut", defaultOut));
            if (target == BuildTarget.Android)
            {
                if (!output.EndsWith(".aab", StringComparison.OrdinalIgnoreCase))
                {
                    Debug.LogError("[gs] -gsOut for Android must end with .aab: " + output);
                    return 2;
                }
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                EditorUserBuildSettings.buildAppBundle = true;
                if (!ApplyKeystore()) return 2;
            }
            else if (target == BuildTarget.iOS || target == BuildTarget.WebGL)
            {
                Directory.CreateDirectory(output);  // these targets write a folder
            }
            else
            {
                Directory.CreateDirectory(Path.GetDirectoryName(output));  // desktop: an executable or .app plus its data
            }

            string[] scenes = EnabledScenes();
            if (scenes.Length == 0)
            {
                SceneBuilder.Build();
                scenes = EnabledScenes();
            }
            if (scenes.Length == 0)
            {
                Debug.LogError("[gs] no scenes in build settings");
                return 2;
            }

            int number;
            if (int.TryParse(Environment.GetEnvironmentVariable("GS_BUILD_NUMBER"), out number))
            {
                PlayerSettings.Android.bundleVersionCode = number;
                PlayerSettings.iOS.buildNumber = number.ToString();
            }

            var options = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = output,
                target = target,
                targetGroup = BuildPipeline.GetBuildTargetGroup(target),
                options = BuildOptions.None,
            };
            BuildSummary summary = BuildPipeline.BuildPlayer(options).summary;
            Debug.Log("[gs] build " + summary.result + ": " + summary.totalErrors + " errors, " + summary.totalWarnings
                + " warnings, " + (summary.totalSize / (1024 * 1024)) + " MB -> " + output);
            return summary.result == BuildResult.Succeeded ? 0 : 1;
        }

        private static string[] EnabledScenes()
        {
            return EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
        }

        /// <summary>False only when a keystore path is given but unusable. Without one Unity debug-signs the AAB.</summary>
        private static bool ApplyKeystore()
        {
            string path = Environment.GetEnvironmentVariable("GS_ANDROID_KEYSTORE_PATH");
            if (string.IsNullOrEmpty(path))
            {
                Debug.LogWarning("[gs] GS_ANDROID_KEYSTORE_PATH not set: the AAB is debug-signed and cannot be uploaded to Google Play.");
                return true;
            }
            if (!File.Exists(path))
            {
                Debug.LogError("[gs] keystore not found: " + path);
                return false;
            }
            string pass = Environment.GetEnvironmentVariable("GS_ANDROID_KEYSTORE_PASS") ?? "";
            PlayerSettings.Android.useCustomKeystore = true;
            PlayerSettings.Android.keystoreName = path;
            PlayerSettings.Android.keystorePass = pass;
            PlayerSettings.Android.keyaliasName = Environment.GetEnvironmentVariable("GS_ANDROID_KEY_ALIAS") ?? "";
            PlayerSettings.Android.keyaliasPass = Environment.GetEnvironmentVariable("GS_ANDROID_KEY_PASS") ?? pass;
            return true;
        }
    }

    /// <summary>Shared helpers for the batch entry points: -gs* argument parsing and exit handling.</summary>
    public static class GsArgs
    {
        public static string ProjectRoot
        {
            get { return Directory.GetParent(Application.dataPath).FullName; }
        }

        /// <summary>Value following the flag on the command line, or the fallback.</summary>
        public static string Get(string flag, string fallback = null)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (args[i] == flag) return args[i + 1];
            return fallback;
        }

        public static string Resolve(string path)
        {
            return Path.IsPathRooted(path) ? path : Path.GetFullPath(Path.Combine(ProjectRoot, path));
        }

        /// <summary>Runs the body, logs any exception, and exits the batch-mode editor with its code (0 ok, 1 failed, 2 usage).</summary>
        public static void Run(string label, Func<int> body)
        {
            int code;
            try
            {
                code = body();
            }
            catch (Exception e)
            {
                Debug.LogError("[gs] " + label + " failed: " + e);
                code = 1;
            }
            Exit(code);
        }

        public static void Exit(int code)
        {
            Debug.Log("[gs] exit code " + code);
            if (Application.isBatchMode) EditorApplication.Exit(code);
        }
    }
}
