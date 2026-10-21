using System.IO;
using Game.Core;
using UnityEditor;
using UnityEngine;

namespace Game.EditorTools
{
    /// <summary>
    /// Headless playtest on the pure sim, writing a playtest-report JSON. Arguments:
    ///   -gsMode script|bot (default script)   -gsOut &lt;report.json&gt;   -gsSeed &lt;n&gt; (optional)
    ///   script: -gsScript &lt;path to playthrough JSON&gt;
    ///   bot:    -gsBot greedy|random (default greedy)  -gsRuns &lt;n&gt; (default 200)
    /// Exit codes: 0 verdict pass, 1 verdict fail, 2 usage or input error.
    /// </summary>
    public static class PlaytestRunner
    {
        private const string TuningPath = "Assets/_Game/Data/tuning.json";

        public static void Run()
        {
            GsArgs.Run("PlaytestRunner.Run", Execute);
        }

        private static int Execute()
        {
            string mode = GsArgs.Get("-gsMode", "script");
            string outArg = GsArgs.Get("-gsOut");
            if (string.IsNullOrEmpty(outArg))
            {
                Debug.LogError("[gs] usage: -gsOut <report.json> is required");
                return 2;
            }

            string tuningFile = GsArgs.Resolve(TuningPath);
            Tuning tuning = Tuning.Parse(File.Exists(tuningFile) ? File.ReadAllText(tuningFile) : null);
            long seedValue;
            long? seed = long.TryParse(GsArgs.Get("-gsSeed"), out seedValue) ? seedValue : (long?)null;
            string build = Application.productName + " " + PlayerSettings.bundleVersion;

            string error;
            System.Collections.Generic.Dictionary<string, object> report;
            if (mode == "script")
            {
                string scriptArg = GsArgs.Get("-gsScript");
                string scriptPath = string.IsNullOrEmpty(scriptArg) ? null : GsArgs.Resolve(scriptArg);
                if (scriptPath == null || !File.Exists(scriptPath))
                {
                    Debug.LogError("[gs] usage: -gsScript <existing playthrough JSON>, got '" + scriptArg + "'");
                    return 2;
                }
                report = Playthrough.RunScript(File.ReadAllText(scriptPath), tuning, seed, build, out error);
            }
            else if (mode == "bot")
            {
                int runs;
                if (!int.TryParse(GsArgs.Get("-gsRuns", "200"), out runs)) runs = 0;
                report = Playthrough.RunBots(GsArgs.Get("-gsBot", "greedy"), runs, seed ?? 1, tuning, build, out error);
            }
            else
            {
                Debug.LogError("[gs] usage: -gsMode script|bot");
                return 2;
            }

            if (report == null)
            {
                Debug.LogError("[gs] " + error);
                return 2;
            }
            string outPath = GsArgs.Resolve(outArg);
            Directory.CreateDirectory(Path.GetDirectoryName(outPath));
            File.WriteAllText(outPath, MiniJson.Write(report, true) + "\n");
            string verdict = MiniJson.GetString(report, "verdict", "fail");
            Debug.Log("[gs] " + mode + " verdict=" + verdict + " metrics=" + MiniJson.Write(report["metrics"]) + " -> " + outPath);
            return verdict == "pass" ? 0 : 1;
        }
    }
}
