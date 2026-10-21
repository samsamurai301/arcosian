using System.Collections.Generic;
using System.IO;
using Game.Core;
using Game.Presentation;
using NUnit.Framework;
using UnityEngine;

namespace Game.Tests
{
    /// <summary>EditMode tests for Game.Core. They need no scene and no engine state, so they run in milliseconds.</summary>
    public class SimTests
    {
        /// <summary>Row-major 5x5 grid; the given cells fill from index 0, the rest are empty.</summary>
        private static int[] Grid(params int[] cells)
        {
            var g = new int[25];
            cells.CopyTo(g, 0);
            return g;
        }

        private static string Flat(List<SimEvent> events)
        {
            return string.Join("\n", events);
        }

        private static int[] Row0(int[] grid)
        {
            var row = new int[5];
            System.Array.Copy(grid, row, 5);
            return row;
        }

        [Test]
        public void MergeLeft_EachTileMergesOnce()
        {
            SlideResult r = Sim.SlideGrid(Grid(2, 2, 2, 2, 0), 5, "left");
            CollectionAssert.AreEqual(new[] { 4, 4, 0, 0, 0 }, Row0(r.Grid));
            Assert.AreEqual(8, r.Gain);
        }

        [Test]
        public void ThreeEqualTiles_MergeTheLeadingPair()
        {
            int[] g = Grid(0, 4, 4, 4, 0);
            CollectionAssert.AreEqual(new[] { 8, 4, 0, 0, 0 }, Row0(Sim.SlideGrid(g, 5, "left").Grid));
            CollectionAssert.AreEqual(new[] { 0, 0, 0, 4, 8 }, Row0(Sim.SlideGrid(g, 5, "right").Grid));
        }

        [Test]
        public void AllFourDirectionsSlideAndMerge()
        {
            int[] g = new int[25];
            g[0] = g[4] = g[20] = g[24] = 2;
            Assert.AreEqual(4, Sim.SlideGrid(g, 5, "up").Grid[0], "up merges column 0 at the top");
            Assert.AreEqual(4, Sim.SlideGrid(g, 5, "down").Grid[20], "down merges column 0 at the bottom");
            Assert.AreEqual(4, Sim.SlideGrid(g, 5, "right").Grid[4], "right merges row 0 at the right");
            Assert.AreEqual(4, Sim.SlideGrid(g, 5, "left").Grid[0], "left merges row 0 at the left");
        }

        [Test]
        public void MoveThatChangesNothing_IsInvalidAndDoesNotCount()
        {
            var sim = new Sim(1);
            sim.SetGrid(Grid(2, 4, 2, 4, 2));
            List<SimEvent> events = sim.Apply(GameAction.Move("left"));
            Assert.AreEqual(SimEventType.InvalidMove, events[0].Type);
            Assert.AreEqual(0, sim.State.Moves);
        }

        [Test]
        public void SameSeedAndMoves_GiveIdenticalEventsAndGrid()
        {
            var a = new Sim(5);
            var b = new Sim(5);
            foreach (string d in new[] { "left", "down", "right", "up", "left", "down" })
                Assert.AreEqual(Flat(a.Apply(GameAction.Move(d))), Flat(b.Apply(GameAction.Move(d))), "events for " + d);
            CollectionAssert.AreEqual(a.State.Grid, b.State.Grid);
            Assert.AreEqual(a.State.Score, b.State.Score);
        }

        [Test]
        public void NewGame_SpawnsInitialTiles()
        {
            var sim = new Sim(3);
            Assert.AreEqual(23, sim.State.EmptyCells().Count);
            Assert.AreEqual(GameState.Playing, sim.State.Status);
            List<SimEvent> events = sim.Apply(GameAction.NewGame(9));
            Assert.AreEqual(SimEventType.NewGame, events[0].Type);
            Assert.AreEqual(3, events.Count, "new_game plus two spawns");
            Assert.AreEqual(9, sim.State.SeedValue);
        }

        [Test]
        public void ReachingTheWinTile_EmitsWinAndEndsTheRun()
        {
            var sim = new Sim(1);
            sim.SetGrid(Grid(512, 512));
            List<SimEvent> events = sim.Apply(GameAction.Move("left"));
            Assert.AreEqual(SimEventType.Win, events[events.Count - 1].Type);
            Assert.AreEqual(GameState.Won, sim.State.Status);
            Assert.AreEqual(SimEventType.Rejected, sim.Apply(GameAction.Move("right"))[0].Type);
        }

        [Test]
        public void LockedGrid_IsLostAndRejectsMoves()
        {
            var cells = new int[25];
            for (int i = 0; i < 25; i++) cells[i] = ((i / 5 + i % 5) % 2 == 0) ? 2 : 4;
            Assert.IsFalse(Sim.CanMove(cells, 5));
            var sim = new Sim(1);
            sim.SetGrid(cells);
            Assert.AreEqual(GameState.Lost, sim.State.Status);
            List<SimEvent> events = sim.Apply(GameAction.Move("left"));
            Assert.AreEqual(SimEventType.Rejected, events[0].Type);
            Assert.AreEqual("game_over", events[0].Reason);
        }

        [Test]
        public void UnknownActionAndBadDirection_AreRejected()
        {
            var sim = new Sim(1);
            Assert.AreEqual("unknown_action", sim.Apply(new GameAction { Type = "jump" })[0].Reason);
            Assert.AreEqual("bad_direction", sim.Apply(GameAction.Move("sideways"))[0].Reason);
        }

        [Test]
        public void StateRoundTripsThroughJson_AndContinuesIdentically()
        {
            var a = new Sim(3);
            a.Apply(GameAction.Move("left"));
            a.Apply(GameAction.Move("down"));
            var restored = (Dictionary<string, object>)MiniJson.Parse(MiniJson.Write(a.ToDict()));
            var b = new Sim(99);
            Assert.IsTrue(b.LoadDict(restored));
            CollectionAssert.AreEqual(a.State.Grid, b.State.Grid);
            Assert.AreEqual(Flat(a.Apply(GameAction.Move("right"))), Flat(b.Apply(GameAction.Move("right"))));
        }

        [Test]
        public void LoadDict_RejectsMalformedAndMismatchedState()
        {
            var sim = new Sim(1);
            int[] before = (int[])sim.State.Grid.Clone();
            Assert.IsFalse(sim.LoadDict(null));
            Assert.IsFalse(sim.LoadDict(new Dictionary<string, object> { { "size", 5 }, { "grid", new List<object>() } }));
            Assert.IsFalse(sim.LoadDict(new Dictionary<string, object> { { "size", 4 }, { "grid", new List<object>(new object[16]) } }));
            CollectionAssert.AreEqual(before, sim.State.Grid, "failed loads leave the state untouched");
        }

        [Test]
        public void Rng_IsDeterministic_AndRestoresFromDict()
        {
            var a = new Rng(42);
            var b = new Rng(42);
            for (int i = 0; i < 20; i++) Assert.AreEqual(a.NextU32(), b.NextU32());
            Assert.AreNotEqual(new Rng(1).NextU32(), new Rng(2).NextU32());

            var c = new Rng(7);
            c.NextU32();
            var d = new Rng(0);
            d.FromDict(c.ToDict());
            for (int i = 0; i < 10; i++) Assert.AreEqual(c.NextU32(), d.NextU32());
            for (int i = 0; i < 200; i++) Assert.That(c.RandInt(7), Is.InRange(0, 6));
        }

        [Test]
        public void MiniJson_RoundTripsAndKeeps64BitIntegers()
        {
            const string text = "{\"a\":[1,2.5,-3e2,true,null,\"x\\n\\u0041\"],\"b\":{\"c\":9007199254740993}}";
            object parsed = MiniJson.Parse(text);
            var root = (Dictionary<string, object>)parsed;
            Assert.AreEqual(9007199254740993L, MiniJson.GetLong(MiniJson.GetDict(root, "b"), "c"));
            var list = (List<object>)root["a"];
            Assert.AreEqual(1L, list[0]);
            Assert.AreEqual(2.5, (double)list[1], 1e-12);
            Assert.AreEqual(-300.0, (double)list[2], 1e-12);
            Assert.AreEqual("x\nA", list[5]);
            Assert.AreEqual(MiniJson.Write(parsed), MiniJson.Write(MiniJson.Parse(MiniJson.Write(parsed, true))));
            object ignored;
            Assert.IsFalse(MiniJson.TryParse("{\"a\":", out ignored));
            Assert.IsFalse(MiniJson.TryParse("[1,2] trailing", out ignored));
        }

        [Test]
        public void Tuning_FallsBackToDefaultsAndClamps()
        {
            Tuning d = Tuning.Parse("not json");
            Assert.AreEqual(5, d.Size);
            Assert.AreEqual(1024, d.WinTile);
            Tuning t = Tuning.Parse("{\"size\":99,\"win_tile\":256,\"spawn_four_chance\":7}");
            Assert.AreEqual(8, t.Size);
            Assert.AreEqual(256, t.WinTile);
            Assert.AreEqual(1.0, t.SpawnFourChance, 1e-12);
            Assert.AreEqual(2, t.InitialTiles);
        }

        [Test]
        public void SaveMigration_V1BecomesV2_AndNewerIsRejected()
        {
            var v1 = new Dictionary<string, object> { { "version", 1 }, { "best_score", 120 }, { "games", 4 } };
            Dictionary<string, object> v2 = SaveData.Migrate(v1);
            Assert.AreEqual(SaveData.Current, MiniJson.GetLong(v2, "version"));
            Dictionary<string, object> profile = MiniJson.GetDict(v2, "profile");
            Assert.AreEqual(120, MiniJson.GetLong(profile, "best_score"));
            Assert.AreEqual(4, MiniJson.GetLong(profile, "games_played"));
            Assert.IsTrue(MiniJson.GetBool(MiniJson.GetDict(v2, "settings"), "sound"));
            Assert.IsNull(SaveData.Migrate(new Dictionary<string, object> { { "version", SaveData.Current + 1 } }));
        }

        [Test]
        public void SaveMigration_RepairsMissingSections()
        {
            Dictionary<string, object> d = SaveData.Migrate(new Dictionary<string, object> { { "version", 2 }, { "profile", 5 } });
            Assert.IsNotNull(MiniJson.GetDict(d, "profile"));
            Assert.IsNotNull(MiniJson.GetDict(d, "settings"));
            Assert.IsNull(MiniJson.GetDict(d, "run"));
        }

        [Test]
        public void SmokePlaythrough_Passes()
        {
            string path = Path.Combine(Application.dataPath, "_Game/Tests/Playthroughs/smoke.json");
            string error;
            Dictionary<string, object> report = Playthrough.RunScript(File.ReadAllText(path), new Tuning(), null, "test", out error);
            Assert.IsNotNull(report, error);
            Assert.AreEqual("pass", MiniJson.GetString(report, "verdict"));
        }

        [Test]
        public void Playthrough_ReportsFailedExpectations()
        {
            const string script = "{\"seed\":1,\"steps\":[{\"action\":{\"type\":\"new_game\",\"seed\":1},\"expect\":{\"moves\":{\"op\":\">\",\"value\":0}}}]}";
            string error;
            Dictionary<string, object> report = Playthrough.RunScript(script, new Tuning(), null, "test", out error);
            Assert.AreEqual("fail", MiniJson.GetString(report, "verdict"));
            Assert.AreEqual(1, ((List<object>)report["findings"]).Count);
        }

        [Test]
        public void GreedyBot_NeverSoftlocks()
        {
            string error;
            Dictionary<string, object> report = Playthrough.RunBots("greedy", 20, 1, new Tuning(), "test", out error);
            Assert.IsNotNull(report, error);
            Assert.AreEqual(0, MiniJson.GetLong(MiniJson.GetDict(report, "metrics"), "softlocks", -1));
            Assert.AreEqual("pass", MiniJson.GetString(report, "verdict"));
        }

        [Test]
        public void SwipeClassification_PicksTheDominantAxis()
        {
            Assert.AreEqual("right", SwipeInput.Classify(new Vector2(80f, 20f), 40f));
            Assert.AreEqual("left", SwipeInput.Classify(new Vector2(-80f, -20f), 40f));
            Assert.AreEqual("up", SwipeInput.Classify(new Vector2(10f, 90f), 40f));
            Assert.AreEqual("down", SwipeInput.Classify(new Vector2(-10f, -90f), 40f));
            Assert.IsNull(SwipeInput.Classify(new Vector2(10f, 10f), 40f), "short drags are taps");
        }
    }
}
