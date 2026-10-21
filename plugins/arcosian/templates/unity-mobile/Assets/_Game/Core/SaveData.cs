using System.Collections.Generic;

namespace Game.Core
{
    /// <summary>
    /// Versioned save schema and migrations (pure functions, unit-testable). Same schema as godot-mobile.
    /// v1: {version, best_score, games}
    /// v2: {version, profile{best_score, games_played, last_score, last_won}, settings{sound, haptics}, run}
    /// To change the schema: bump Current, add a V&lt;N&gt;ToV&lt;N+1&gt; step in Migrate, add a test in SimTests.
    /// </summary>
    public static class SaveData
    {
        public const int Current = 2;

        public static Dictionary<string, object> Default()
        {
            return new Dictionary<string, object>
            {
                { "version", Current },
                { "profile", new Dictionary<string, object>
                    {
                        { "best_score", 0 }, { "games_played", 0 }, { "last_score", 0 }, { "last_won", false },
                    } },
                { "settings", new Dictionary<string, object> { { "sound", true }, { "haptics", true } } },
                { "run", null },
            };
        }

        /// <summary>Returns a migrated deep copy, or null when the data is unreadable or from a newer build.</summary>
        public static Dictionary<string, object> Migrate(Dictionary<string, object> data)
        {
            if (data == null) return null;
            int v = (int)MiniJson.GetLong(data, "version", 1);
            if (v < 1 || v > Current) return null;
            var d = (Dictionary<string, object>)MiniJson.Clone(data);
            while (v < Current)
            {
                switch (v)
                {
                    case 1:
                        d = V1ToV2(d);
                        break;
                    default:
                        return null;
                }
                v = (int)MiniJson.GetLong(d, "version", v + 1);
            }
            return Normalize(d);
        }

        private static Dictionary<string, object> V1ToV2(Dictionary<string, object> d)
        {
            Dictionary<string, object> outp = Default();
            var profile = (Dictionary<string, object>)outp["profile"];
            profile["best_score"] = MiniJson.GetLong(d, "best_score", 0);
            profile["games_played"] = MiniJson.GetLong(d, "games", 0);
            return outp;
        }

        /// <summary>Guarantees profile and settings are objects and run is an object or null.</summary>
        private static Dictionary<string, object> Normalize(Dictionary<string, object> d)
        {
            Dictionary<string, object> def = Default();
            foreach (string key in new[] { "profile", "settings" })
                if (MiniJson.GetDict(d, key) == null) d[key] = def[key];
            if (MiniJson.GetDict(d, "run") == null) d["run"] = null;
            return d;
        }
    }
}
