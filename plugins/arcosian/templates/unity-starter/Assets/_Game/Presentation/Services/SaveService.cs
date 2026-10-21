using System;
using System.Collections.Generic;
using System.IO;
using Game.Core;
using UnityEngine;

namespace Game.Presentation.Services
{
    /// <summary>
    /// Versioned JSON save (schema and migrations live in Game.Core.SaveData).
    /// Write order: temp file, copy current to .bak, delete current, move temp into place. A crash at any point
    /// leaves either the new file, the old file, or the .bak, and Load tries them in that order.
    /// Flush() writes only when dirty; Bootstrap calls it on pause, focus loss, quit and run end.
    /// </summary>
    public sealed class SaveService
    {
        private readonly string _path;
        private bool _dirty;

        public Dictionary<string, object> Data { get; private set; }

        public SaveService(string path)
        {
            _path = path;
            Data = SaveData.Default();
        }

        private Dictionary<string, object> Profile { get { return MiniJson.GetDict(Data, "profile"); } }
        private Dictionary<string, object> Settings { get { return MiniJson.GetDict(Data, "settings"); } }

        public int BestScore { get { return (int)MiniJson.GetLong(Profile, "best_score", 0); } }
        public bool SoundOn { get { return MiniJson.GetBool(Settings, "sound", true); } }
        public bool HapticsOn { get { return MiniJson.GetBool(Settings, "haptics", true); } }
        public Dictionary<string, object> Run { get { return MiniJson.GetDict(Data, "run"); } }

        public void Load()
        {
            Data = TryRead(_path) ?? TryRead(_path + ".bak") ?? SaveData.Default();
            _dirty = false;
        }

        public void SetSettings(bool sound, bool haptics)
        {
            Settings["sound"] = sound;
            Settings["haptics"] = haptics;
            _dirty = true;
        }

        public void RecordResult(int score, bool won)
        {
            Dictionary<string, object> p = Profile;
            p["best_score"] = Math.Max(BestScore, score);
            p["games_played"] = MiniJson.GetLong(p, "games_played", 0) + 1;
            p["last_score"] = score;
            p["last_won"] = won;
            _dirty = true;
        }

        /// <summary>Remember the run in progress so "continue" works after the OS kills the app.</summary>
        public void StashRun(Dictionary<string, object> run)
        {
            Data["run"] = run;
            _dirty = true;
        }

        public void ClearRun()
        {
            Data["run"] = null;
            _dirty = true;
        }

        public void Flush()
        {
            if (!_dirty) return;
            try
            {
                string dir = Path.GetDirectoryName(_path);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                string tmp = _path + ".tmp";
                File.WriteAllText(tmp, MiniJson.Write(Data, true));
                if (File.Exists(_path))
                {
                    File.Copy(_path, _path + ".bak", true);
                    File.Delete(_path);
                }
                File.Move(tmp, _path);
                _dirty = false;
            }
            catch (IOException e)
            {
                Debug.LogWarning("[save] write failed: " + e.Message);
            }
            catch (UnauthorizedAccessException e)
            {
                Debug.LogWarning("[save] write failed: " + e.Message);
            }
        }

        private static Dictionary<string, object> TryRead(string path)
        {
            try
            {
                if (!File.Exists(path)) return null;
                object parsed;
                if (!MiniJson.TryParse(File.ReadAllText(path), out parsed)) return null;
                return SaveData.Migrate(parsed as Dictionary<string, object>);
            }
            catch (IOException)
            {
                return null;
            }
            catch (UnauthorizedAccessException)
            {
                return null;
            }
        }
    }
}
