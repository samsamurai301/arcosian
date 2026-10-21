using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Game.Core
{
    /// <summary>Event type names emitted by <see cref="Sim.Apply"/>.</summary>
    public static class SimEventType
    {
        public const string NewGame = "new_game";
        public const string Slide = "slide";
        public const string Merge = "merge";
        public const string Score = "score";
        public const string Spawn = "spawn";
        public const string Win = "win";
        public const string Lose = "lose";
        public const string InvalidMove = "invalid_move";
        public const string Rejected = "rejected";
    }

    public readonly struct TileMove
    {
        public readonly int From;
        public readonly int To;
        public readonly int Value;
        public readonly bool Merged;

        public TileMove(int fromIdx, int toIdx, int value, bool merged)
        {
            From = fromIdx;
            To = toIdx;
            Value = value;
            Merged = merged;
        }
    }

    public readonly struct MergeInfo
    {
        public readonly int At;
        public readonly int Value;

        public MergeInfo(int at, int value)
        {
            At = at;
            Value = value;
        }
    }

    /// <summary>
    /// One thing that happened, described as data (what, not how to draw it).
    /// Fields are used per type: slide{Dir,Moves}, merge{At,Value}, score{Delta,Total}, spawn{At,Value},
    /// win/lose{Score}, new_game{Seed}, invalid_move{Dir}, rejected{Reason}.
    /// </summary>
    public sealed class SimEvent
    {
        public string Type;
        public string Dir;
        public int At = -1;
        public int Value;
        public int Delta;
        public int Total;
        public int Score;
        public long Seed;
        public string Reason;
        public List<TileMove> Moves;

        /// <summary>Stable text form, used to compare event streams for determinism.</summary>
        public override string ToString()
        {
            var sb = new StringBuilder(Type);
            sb.Append('|').Append(Dir).Append('|').Append(At).Append('|').Append(Value).Append('|').Append(Delta)
              .Append('|').Append(Total).Append('|').Append(Score).Append('|').Append(Seed.ToString(CultureInfo.InvariantCulture))
              .Append('|').Append(Reason);
            if (Moves != null)
                foreach (TileMove m in Moves)
                    sb.Append('|').Append(m.From).Append('>').Append(m.To).Append(':').Append(m.Value).Append(m.Merged ? "m" : "");
            return sb.ToString();
        }
    }

    /// <summary>Input to the sim: {"type":"move","dir":"left|right|up|down"} or {"type":"new_game","seed":n}.</summary>
    public sealed class GameAction
    {
        public string Type = "";
        public string Dir = "";
        public long? Seed;

        public static GameAction Move(string dir)
        {
            return new GameAction { Type = "move", Dir = dir };
        }

        public static GameAction NewGame(long seed)
        {
            return new GameAction { Type = "new_game", Seed = seed };
        }

        public static GameAction FromDict(Dictionary<string, object> d)
        {
            var a = new GameAction { Type = MiniJson.GetString(d, "type", ""), Dir = MiniJson.GetString(d, "dir", "") };
            object seed;
            if (d != null && d.TryGetValue("seed", out seed) && MiniJson.IsNumber(seed)) a.Seed = MiniJson.AsLong(seed);
            return a;
        }
    }

    public sealed class SlideResult
    {
        public int[] Grid;
        public bool Moved;
        public int Gain;
        public List<TileMove> Moves = new List<TileMove>();
        public List<MergeInfo> Merges = new List<MergeInfo>();
    }

    /// <summary>
    /// Deterministic simulation of the merge game. No engine references.
    /// Same seed + same actions =&gt; same events. Grid is row-major; "left" slides toward column 0, "up" toward row 0.
    /// </summary>
    public sealed class Sim
    {
        public static readonly string[] Dirs = { "left", "right", "up", "down" };

        public GameState State { get; private set; }
        public Tuning Tuning { get; private set; }

        public Sim(long seed = 1, Tuning tuning = null)
        {
            Tuning = tuning ?? new Tuning();
            NewGame(seed);
        }

        public List<SimEvent> NewGame(long seed)
        {
            State = new GameState(Tuning.Size, seed);
            var events = new List<SimEvent> { new SimEvent { Type = SimEventType.NewGame, Seed = seed } };
            for (int i = 0; i < Tuning.InitialTiles; i++)
            {
                SimEvent e = Spawn();
                if (e != null) events.Add(e);
            }
            return events;
        }

        public List<SimEvent> Apply(GameAction action)
        {
            switch (action == null ? "" : action.Type)
            {
                case "move":
                    return Move(action.Dir);
                case "new_game":
                    return NewGame(action.Seed ?? State.SeedValue);
            }
            return Rejected("unknown_action");
        }

        public Dictionary<string, object> ToDict()
        {
            return State.ToDict();
        }

        /// <summary>False (state untouched) when malformed or recorded for a different board size.</summary>
        public bool LoadDict(Dictionary<string, object> d)
        {
            if (MiniJson.GetLong(d, "size", 0) != Tuning.Size) return false;
            return State.FromDict(d);
        }

        /// <summary>Test helper: replace the grid (row-major) and re-evaluate status.</summary>
        public void SetGrid(int[] values)
        {
            State.Grid = (int[])values.Clone();
            State.Status = CanMove(State.Grid, State.Size) ? GameState.Playing : GameState.Lost;
        }

        private static List<SimEvent> Rejected(string reason)
        {
            return new List<SimEvent> { new SimEvent { Type = SimEventType.Rejected, Reason = reason } };
        }

        private List<SimEvent> Move(string dir)
        {
            if (State.Status != GameState.Playing) return Rejected("game_over");
            if (System.Array.IndexOf(Dirs, dir) < 0) return Rejected("bad_direction");

            SlideResult r = SlideGrid(State.Grid, State.Size, dir);
            if (!r.Moved) return new List<SimEvent> { new SimEvent { Type = SimEventType.InvalidMove, Dir = dir } };

            State.Grid = r.Grid;
            State.Moves++;
            State.Score += r.Gain;
            var events = new List<SimEvent> { new SimEvent { Type = SimEventType.Slide, Dir = dir, Moves = r.Moves } };
            bool reachedWin = false;
            foreach (MergeInfo m in r.Merges)
            {
                events.Add(new SimEvent { Type = SimEventType.Merge, At = m.At, Value = m.Value });
                if (m.Value >= Tuning.WinTile) reachedWin = true;
            }
            if (r.Gain > 0) events.Add(new SimEvent { Type = SimEventType.Score, Delta = r.Gain, Total = State.Score });
            SimEvent spawned = Spawn();
            if (spawned != null) events.Add(spawned);
            if (reachedWin)
            {
                State.Status = GameState.Won;
                events.Add(new SimEvent { Type = SimEventType.Win, Score = State.Score });
            }
            else if (!CanMove(State.Grid, State.Size))
            {
                State.Status = GameState.Lost;
                events.Add(new SimEvent { Type = SimEventType.Lose, Score = State.Score });
            }
            return events;
        }

        private SimEvent Spawn()
        {
            List<int> empties = State.EmptyCells();
            if (empties.Count == 0) return null;
            int at = empties[State.Rng.RandInt(empties.Count)];
            int value = State.Rng.RandFloat() < Tuning.SpawnFourChance ? 4 : 2;
            State.Grid[at] = value;
            return new SimEvent { Type = SimEventType.Spawn, At = at, Value = value };
        }

        /// <summary>Pure slide and merge of a row-major grid. Each tile merges at most once per move.</summary>
        public static SlideResult SlideGrid(int[] grid, int size, string dir)
        {
            var res = new SlideResult { Grid = new int[grid.Length] };
            for (int a = 0; a < size; a++)
            {
                int[] line = Line(size, dir, a);
                int write = 0;
                int lastVal = 0;
                int lastPos = -1;
                bool lastMerged = false;
                for (int i = 0; i < size; i++)
                {
                    int v = grid[line[i]];
                    if (v == 0) continue;
                    if (v == lastVal && !lastMerged)
                    {
                        int dst = line[lastPos];
                        res.Grid[dst] = v * 2;
                        res.Gain += v * 2;
                        res.Moves.Add(new TileMove(line[i], dst, v, true));
                        res.Merges.Add(new MergeInfo(dst, v * 2));
                        lastMerged = true;
                    }
                    else
                    {
                        int dst2 = line[write];
                        res.Grid[dst2] = v;
                        res.Moves.Add(new TileMove(line[i], dst2, v, false));
                        lastVal = v;
                        lastPos = write;
                        lastMerged = false;
                        write++;
                    }
                }
            }
            for (int i = 0; i < grid.Length; i++)
            {
                if (grid[i] != res.Grid[i])
                {
                    res.Moved = true;
                    break;
                }
            }
            return res;
        }

        public static bool CanMove(int[] grid, int size)
        {
            for (int i = 0; i < grid.Length; i++)
            {
                if (grid[i] == 0) return true;
                if (i % size < size - 1 && grid[i] == grid[i + 1]) return true;
                if (i + size < grid.Length && grid[i] == grid[i + size]) return true;
            }
            return false;
        }

        /// <summary>Cell indices of line <paramref name="a"/>, ordered from the edge that tiles slide toward.</summary>
        private static int[] Line(int size, string dir, int a)
        {
            var line = new int[size];
            for (int b = 0; b < size; b++)
            {
                switch (dir)
                {
                    case "left": line[b] = a * size + b; break;
                    case "right": line[b] = a * size + (size - 1 - b); break;
                    case "up": line[b] = b * size + a; break;
                    default: line[b] = (size - 1 - b) * size + a; break;
                }
            }
            return line;
        }
    }
}
