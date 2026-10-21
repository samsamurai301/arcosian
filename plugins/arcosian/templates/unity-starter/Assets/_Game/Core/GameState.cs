using System.Collections;
using System.Collections.Generic;

namespace Game.Core
{
    /// <summary>Plain data for one run of the 5x5 merge game. Serialisable; no logic beyond queries.</summary>
    public sealed class GameState
    {
        public const string Playing = "playing";
        public const string Won = "won";
        public const string Lost = "lost";

        public int Size;
        public int[] Grid;
        public int Score;
        public int Moves;
        public string Status = Playing;
        public long SeedValue;
        public Rng Rng;

        public GameState(int size = 5, long seed = 1)
        {
            Size = size;
            SeedValue = seed;
            Rng = new Rng(seed);
            Grid = new int[size * size];
        }

        public List<int> EmptyCells()
        {
            var list = new List<int>();
            for (int i = 0; i < Grid.Length; i++)
                if (Grid[i] == 0) list.Add(i);
            return list;
        }

        public int MaxTile()
        {
            int m = 0;
            foreach (int v in Grid)
                if (v > m) m = v;
            return m;
        }

        /// <summary>
        /// Resolves playthrough "expect" paths: score, moves, status, won, lost, max_tile, empty_count, grid_sum, grid.&lt;index&gt;.
        /// Returns null for unknown paths. Numbers come back as int, flags as bool, status as string.
        /// </summary>
        public object Lookup(string path)
        {
            switch (path)
            {
                case "score": return Score;
                case "moves": return Moves;
                case "status": return Status;
                case "won": return Status == Won;
                case "lost": return Status == Lost;
                case "max_tile": return MaxTile();
                case "empty_count": return EmptyCells().Count;
                case "grid_sum":
                    int sum = 0;
                    foreach (int v in Grid) sum += v;
                    return sum;
            }
            if (path != null && path.StartsWith("grid."))
            {
                int idx;
                if (int.TryParse(path.Substring(5), out idx) && idx >= 0 && idx < Grid.Length) return Grid[idx];
            }
            return null;
        }

        public Dictionary<string, object> ToDict()
        {
            var cells = new List<object>(Grid.Length);
            foreach (int v in Grid) cells.Add(v);
            return new Dictionary<string, object>
            {
                { "size", Size },
                { "grid", cells },
                { "score", Score },
                { "moves", Moves },
                { "status", Status },
                { "seed", SeedValue },
                { "rng", Rng.ToDict() },
            };
        }

        /// <summary>Returns false and leaves the state untouched when the dictionary is malformed.</summary>
        public bool FromDict(Dictionary<string, object> d)
        {
            object g;
            if (d == null || !d.TryGetValue("grid", out g)) return false;
            var list = g as IList;
            int n = (int)MiniJson.GetLong(d, "size", 0);
            if (list == null || n < 2 || n > 8 || list.Count != n * n) return false;
            var cells = new int[n * n];
            for (int i = 0; i < cells.Length; i++)
            {
                long v = MiniJson.AsLong(list[i], -1);
                if (v < 0 || v > int.MaxValue) return false;
                cells[i] = (int)v;
            }
            string status = MiniJson.GetString(d, "status", Playing);
            if (status != Playing && status != Won && status != Lost) return false;
            Size = n;
            Grid = cells;
            Score = (int)MiniJson.GetLong(d, "score", 0);
            Moves = (int)MiniJson.GetLong(d, "moves", 0);
            Status = status;
            SeedValue = MiniJson.GetLong(d, "seed", 1);
            Rng.FromDict(MiniJson.GetDict(d, "rng"));
            return true;
        }
    }
}
