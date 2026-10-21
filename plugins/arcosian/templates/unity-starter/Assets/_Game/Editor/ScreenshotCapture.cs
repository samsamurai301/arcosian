using System.IO;
using Game.Presentation;
using UnityEditor;
using UnityEngine;

namespace Game.EditorTools
{
    /// <summary>
    /// Visual-gate screenshots of the running game: start.png (fresh board) and played.png (after six scripted moves).
    ///   Unity -batchmode -projectPath &lt;p&gt; -executeMethod Game.EditorTools.ScreenshotCapture.Run -gsOut &lt;abs dir&gt;
    /// Needs a graphics device: do NOT pass -nographics (on Linux CI use xvfb-run). Enters play mode, so the
    /// editor reloads scripts once; a SessionState flag carries the output directory across that reload.
    /// Exit codes: 0 both PNGs written, 1 capture failed, 2 usage error. Game view size decides the resolution.
    /// </summary>
    [InitializeOnLoad]
    public static class ScreenshotCapture
    {
        private const string OutKey = "gs.shots.out";
        private static readonly string[] Moves = { "left", "down", "right", "up", "left", "down" };
        private static int _stage;
        private static int _waitUntil;
        private static int _frame;

        static ScreenshotCapture()
        {
            if (!string.IsNullOrEmpty(SessionState.GetString(OutKey, ""))) EditorApplication.playModeStateChanged += OnPlayMode;
        }

        public static void Run()
        {
            string outArg = GsArgs.Get("-gsOut");
            if (string.IsNullOrEmpty(outArg))
            {
                Debug.LogError("[gs] usage: -gsOut <output directory> is required");
                GsArgs.Exit(2);
                return;
            }
            string dir = GsArgs.Resolve(outArg);
            Directory.CreateDirectory(dir);
            if (!File.Exists(GsArgs.Resolve(SceneBuilder.ScenePath))) SceneBuilder.Build();
            UnityEditor.SceneManagement.EditorSceneManager.OpenScene(SceneBuilder.ScenePath);
            SessionState.SetString(OutKey, dir);
            EditorApplication.EnterPlaymode();
        }

        private static void OnPlayMode(PlayModeStateChange change)
        {
            if (change != PlayModeStateChange.EnteredPlayMode) return;
            _stage = 0;
            _frame = 0;
            _waitUntil = 30; // let the first frames render
            EditorApplication.update += Tick;
        }

        private static void Tick()
        {
            if (++_frame < _waitUntil) return;
            string dir = SessionState.GetString(OutKey, "");
            Bootstrap game = Bootstrap.Current;
            if (game == null)
            {
                Finish(dir, 1);
                return;
            }
            switch (_stage)
            {
                case 0:
                    ScreenCapture.CaptureScreenshot(Path.Combine(dir, "start.png"));
                    foreach (string m in Moves) game.DebugMove(m);
                    _waitUntil = _frame + 30; // moves animate for about 0.1 s each; wait for the board to settle
                    break;
                case 1:
                    ScreenCapture.CaptureScreenshot(Path.Combine(dir, "played.png"));
                    _waitUntil = _frame + 10; // the PNG is written at the end of the capture frame
                    break;
                default:
                    bool ok = File.Exists(Path.Combine(dir, "start.png")) && File.Exists(Path.Combine(dir, "played.png"));
                    Finish(dir, ok ? 0 : 1);
                    return;
            }
            _stage++;
        }

        private static void Finish(string dir, int code)
        {
            EditorApplication.update -= Tick;
            SessionState.EraseString(OutKey);
            Debug.Log("[gs] screenshots in " + dir + " (exit " + code + ")");
            EditorApplication.ExitPlaymode();
            GsArgs.Exit(code);
        }
    }
}
