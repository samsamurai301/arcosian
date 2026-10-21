using System;
using System.Collections.Generic;

namespace Game.Core
{
    /// <summary>
    /// Scripted playthroughs and bot runs on the pure sim, producing playtest-report documents
    /// (schema_version 1.0) as plain dictionaries; serialise with <see cref="MiniJson.Write"/>.
    /// Script format: {"schema_version":"1.0","seed":1,"steps":[{"action":{...},"expect":{"path": value | {"op":">=","value":n}}}]}
    /// Expect paths: see <see cref="GameState.Lookup"/>. Ops: == (default), !=, >=, &lt;=, >, &lt;.
    /// Time metrics are estimates: SecPerMove seconds per accepted move.
    /// </summary>
    public static class Playthrough
    {
        public const double SecPerMove = 0.8;
        public const int MaxMoves = 5000; // a run longer than this without ending counts as a softlock

        /// <summary>Returns null and sets <paramref name="error"/> when the script cannot be read.</summary>
        public static Dictionary<string, object> RunScript(string json, Tuning tuning, long? seedOverride, string build, out string error)
        {
            error = null;
            object parsed;
            if (!MiniJson.TryParse(json, out parsed))
            {
                error = "playthrough script is not valid JSON";
                return null;
            }
            var spec = parsed as Dictionary<string, object>;
            object stepsObj = null;
            if (spec != null) spec.TryGetValue("steps", out stepsObj);
            var steps = stepsObj as List<object>;
            if (steps == null)
            {
                error = "playthrough script needs a \"steps\" array";
                return null;
            }

            long seed = seedOverride ?? MiniJson.GetLong(spec, "seed", 1);
            Dictionary<string, object> report = NewReport("deterministic_script", 1, seed, build);
            var reportSteps = (List<object>)report["steps"];
            var findings = (List<object>)report["findings"];
            var sim = new Sim(seed, tuning);
            bool allOk = true;

            for (int t = 0; t < steps.Count; t++)
            {
                var step = steps[t] as Dictionary<string, object>;
                Dictionary<string, object> action = MiniJson.GetDict(step, "action") ?? new Dictionary<string, object>();
                Dictionary<string, object> expect = MiniJson.GetDict(step, "expect") ?? new Dictionary<string, object>();
                sim.Apply(GameAction.FromDict(action));

                var observed = new Dictionary<string, object>();
                bool ok = true;
                foreach (KeyValuePair<string, object> kv in expect)
                {
                    object got = sim.State.Lookup(kv.Key);
                    observed[kv.Key] = got;
                    ok = Matches(got, kv.Value) && ok;
                }
                reportSteps.Add(new Dictionary<string, object>
                {
                    { "t", t }, { "action", action }, { "expect", expect }, { "observed", observed }, { "ok", ok },
                });
                if (ok) continue;
                allOk = false;
                findings.Add(new Dictionary<string, object>
                {
                    { "severity", "major" },
                    { "title", "expectation failed at step " + t },
                    { "detail", "expected " + MiniJson.Write(expect) + ", observed " + MiniJson.Write(observed) },
                    { "repro", "seed=" + seed + ", steps 0.." + t },
                });
            }

            var metrics = (Dictionary<string, object>)report["metrics"];
            metrics["win_rate"] = sim.State.Status == GameState.Won ? 1.0 : 0.0;
            metrics["avg_session_sec"] = sim.State.Moves * SecPerMove;
            metrics["errors"] = findings.Count;
            report["verdict"] = allOk ? "pass" : "fail";
            return report;
        }

        /// <summary>Bot runs for difficulty and softlock estimation. bot is "greedy" or "random".</summary>
        public static Dictionary<string, object> RunBots(string bot, int runs, long seed, Tuning tuning, string build, out string error)
        {
            error = null;
            if ((bot != "greedy" && bot != "random") || runs < 1)
            {
                error = "usage: bot must be greedy|random and runs >= 1";
                return null;
            }
            Dictionary<string, object> report = NewReport("bot", runs, seed, build);
            int wins = 0, softlocks = 0, totalMoves = 0, firstRewardMoves = 0;
            for (int r = 0; r < runs; r++)
            {
                var sim = new Sim(seed + r, tuning);
                var chooser = new Rng(seed * 7919 + r);
                int firstReward = -1;
                while (sim.State.Status == GameState.Playing && sim.State.Moves < MaxMoves)
                {
                    string dir = Pick(sim, bot, chooser);
                    if (dir == null) break;
                    List<SimEvent> events = sim.Apply(GameAction.Move(dir));
                    if (firstReward < 0 && sim.State.Score > 0) firstReward = sim.State.Moves;
                    if (events[0].Type == SimEventType.Rejected) break;
                }
                if (sim.State.Status == GameState.Won) wins++;
                else if (sim.State.Status == GameState.Playing) softlocks++;
                totalMoves += sim.State.Moves;
                firstRewardMoves += Math.Max(firstReward, 0);
            }

            var metrics = (Dictionary<string, object>)report["metrics"];
            metrics["win_rate"] = (double)wins / runs;
            metrics["avg_session_sec"] = (double)totalMoves / runs * SecPerMove;
            metrics["time_to_first_reward_sec"] = (double)firstRewardMoves / runs * SecPerMove;
            metrics["softlocks"] = softlocks;
            if (softlocks > 0)
            {
                ((List<object>)report["findings"]).Add(new Dictionary<string, object>
                {
                    { "severity", "blocker" },
                    { "title", "softlock" },
                    { "detail", softlocks + " of " + runs + " runs neither ended nor had a move available" },
                    { "repro", "mode=bot bot=" + bot + " seed=" + seed + " runs=" + runs },
                });
            }
            report["verdict"] = softlocks == 0 ? "pass" : "fail";
            return report;
        }

        private static Dictionary<string, object> NewReport(string mode, int runs, long seed, string build)
        {
            return new Dictionary<string, object>
            {
                { "schema_version", "1.0" },
                { "build", build },
                { "mode", mode },
                { "runs", runs },
                { "seed", seed },
                { "steps", new List<object>() },
                { "screenshots", new List<object>() },
                { "findings", new List<object>() },
                { "metrics", new Dictionary<string, object>
                    {
                        { "win_rate", 0.0 }, { "avg_session_sec", 0.0 }, { "time_to_first_reward_sec", 0.0 },
                        { "softlocks", 0 }, { "crashes", 0 }, { "errors", 0 },
                    } },
                { "verdict", "pass" },
            };
        }

        /// <summary>Greedy maximises (score gain, empty cells) over legal moves without spawning; random picks any legal move.</summary>
        private static string Pick(Sim sim, string bot, Rng chooser)
        {
            string best = null;
            double bestKey = -1.0;
            var legal = new List<string>();
            foreach (string d in Sim.Dirs)
            {
                SlideResult r = Sim.SlideGrid(sim.State.Grid, sim.State.Size, d);
                if (!r.Moved) continue;
                legal.Add(d);
                int empties = 0;
                foreach (int v in r.Grid)
                    if (v == 0) empties++;
                double key = r.Gain * 100.0 + empties;
                if (key > bestKey)
                {
                    bestKey = key;
                    best = d;
                }
            }
            if (legal.Count == 0) return null;
            return bot == "greedy" ? best : legal[chooser.RandInt(legal.Count)];
        }

        private static bool Matches(object got, object want)
        {
            var w = want as Dictionary<string, object>;
            if (w == null) return Equal(got, want);
            object v;
            w.TryGetValue("value", out v);
            string op = MiniJson.GetString(w, "op", "==");
            switch (op)
            {
                case ">=":
                case "<=":
                case ">":
                case "<":
                    if (!MiniJson.IsNumber(got) || !MiniJson.IsNumber(v)) return false;
                    double a = MiniJson.ToDouble(got), b = MiniJson.ToDouble(v);
                    return op == ">=" ? a >= b : op == "<=" ? a <= b : op == ">" ? a > b : a < b;
                case "!=":
                    return !Equal(got, v);
                default:
                    return Equal(got, v);
            }
        }

        private static bool Equal(object a, object b)
        {
            if (MiniJson.IsNumber(a) && MiniJson.IsNumber(b))
                return Math.Abs(MiniJson.ToDouble(a) - MiniJson.ToDouble(b)) < 1e-9;
            return Equals(a, b);
        }
    }
}
